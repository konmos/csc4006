import typing as t
from dataclasses import dataclass
from types import SimpleNamespace

try:
    import networkx as nx
    from pyvis.network import Network
    DRAWING_ENABLED = True
except ImportError:
    DRAWING_ENABLED = False


Trace = t.List[t.Dict[str, t.Union[str, 'Trace']]]
Nodes = t.List[str]
Edges = t.List[t.Tuple[str, str]]

def _nodes_from_trace(events: Trace) -> Nodes:
    if events is None:
        return []

    nodes = []

    for event in events:
        if event.get('agent') is not None:
            nodes.append(f'{event["event"]}:{event["agent"][0]}')
        else:
            nodes.append(event['event'])

        nodes.extend(_nodes_from_trace(event['triggered']))

    return nodes


def _edges_from_trace(events: Trace) -> Edges:
    if events is None:
        return []

    edges = []

    for event in events:
        for triggered in event['triggered']:
            src = event['event']
            dest = triggered['event']

            if triggered.get('agent') is not None:
                dest += f':{triggered["agent"][0]}'

            if event.get('agent') is not None:
                src += f':{event["agent"][0]}'

            edges.append((src, dest))
            edges.extend(_edges_from_trace(event['triggered']))

    return edges


def _graph_from_dfl(dfl: t.Union[str, t.List[str]]) -> t.Tuple[Nodes, Edges]:
    """
    Return a set of nodes and edges for a DFL description.
    """
    if isinstance(dfl, str):
        dfl = dfl.split('\n')

    nodes, edges = [], []

    for f in dfl:
        source, destinations = [x.strip() for x in f.split('->')]

        nodes.append(source)

        for dest in destinations[1:-1].split(','):  # Ignore braces
            if not dest:
                continue

            nodes.append(dest)
            edges.append((source, dest))

    return nodes, edges


def visualize_dfl(dfl: t.Union[str, t.List[str]], notebook: bool = True):
    """
    Draw the visual representation of a DFL description.
    """
    G = nx.DiGraph()
    nodes, edges = _graph_from_dfl(dfl)

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    net = Network(
        notebook=notebook,
        directed=True,
        bgcolor='#222222',
        font_color='white'
    )

    net.from_nx(G)
    return net.show("dfl.html")


@dataclass
class Event:
    name: str
    func: t.Callable
    triggered_by: t.Optional[str]


class Agent:
    def __init__(self, agent_id: t.Tuple[int, int]) -> None:
        # agent_id is a two element tuple, where the first element
        # is the global ID amongst all other agents, and the second element
        # is an agent-specific ID.
        # For example;
        #   world.agents = [Foo, Foo, Bar]
        #   a = w.add_agent(Bar)
        #   a._agent_id == (3, 1)
        self._agent_id = agent_id

    @property
    def agent_id(self) -> int:
        return self._agent_id[1]

    @property
    def global_id(self) -> int:
        return self._agent_id[0]

    def __repr__(self) -> str:
        return f'<[Agent] {self.__class__.__name__} {self._agent_id}>'


class World:
    """
    A World class keeps track of all agents, componenets, events, and actions.
    This World instance is also responsible for processing and emitting events.
    """

    def __init__(self) -> None:
        self.agents: t.List[Agent] = []
        # self.components = []
        self.events: t.Mapping[str, Event] = {}
        self.ctx: SimpleNamespace = SimpleNamespace()

        self._last_trace: Trace = None

    def reset_agents(self) -> None:
        """
        Remove all agents. Useful for cleanup if they are added by an event.
        """
        self.agents = []

    def add_event(self, event: t.Callable, event_name: str, triggered_by: t.Optional[str] = None) -> None:
        """
        Create and add a new event instance.
        """
        self.events[event_name] = Event(
            name=event_name,
            func=event,
            triggered_by=triggered_by
        )

    def event(self, triggered_by: t.Optional[str] = None) -> t.Callable:
        """
        Decorator to create an event.
        """
        def decorator(f: t.Callable) -> t.Callable:
            self.add_event(f, f.__qualname__, triggered_by)
            return f

        return decorator

    def add_agent(self, blueprint: t.Type[Agent], *args, **kwargs) -> Agent:
        """
        Construct and Agent from a blueprint class and assign the proper ID's.
        """
        _id = [len(self.agents), 0]

        for a in self.agents:
            if isinstance(a, blueprint):
                _id[1] += 1

        agent = blueprint(tuple(_id), *args, **kwargs)
        self.agents.append(agent)
        return agent

    # def _agent_in_trace(self, event_trace, agent_id):
    #     if event_trace is None:
    #         return True

    #     for evt in event_trace:
    #         if evt.get('agent') == agent_id:
    #             return True

    #     return False

    def _process(self, events: t.List[str] = None, ignore_exceptions: bool = False) -> Trace:
        """
        Process a series of events recursively. Each event can trigger other events.
        """
        if events is None:
            events = self.get_origin_events()

        _events = []

        for e in events:
            trace = []
            evt = self.events[e]

            if '.' in e:
                agent = e.split('.')[0]

                for a in self.agents:
                    if a.__class__.__name__ == agent:
                        try:
                            # Pass the instance reference
                            evt.func(a, self.ctx)

                            trace.append({
                                'event': e,
                                'agent': a._agent_id,
                                'triggered': []
                            })
                        except Exception as exc:
                            if not ignore_exceptions:
                                raise exc
            else:
                try:
                    evt.func(self.ctx)

                    trace.append({
                        'event': e,
                        'triggered': []
                    })
                except Exception as exc:
                    if not ignore_exceptions:
                        raise exc

            # Check if the event was triggered.
            # It may have been triggered only once, or by every (or some) agents.
            if not trace:
                continue

            # At this point, we know the event was triggered.
            # We don't know how many times it was triggered, however, or if any exceptions occurred.
            # Search for related events and relegate them to a recursive call.
            related_events = [
                x for x in self.events if e == self.events[x].triggered_by
            ]

            triggered = self._process(
                related_events,
                ignore_exceptions=ignore_exceptions
            )

            if len(trace) == 1:
                trace[0]['triggered'] = triggered
            else:
                # agents
                for t in trace:
                    for e in triggered:
                        if t['agent'] == e['agent']:
                            t['triggered'].append(e)

            _events.extend(trace)

        return _events

    def process(self, *args, **kwargs) -> Trace:
        """
        Run `World._process` and set `self._last_trace`.
        """
        self._last_trace = self._process(*args, **kwargs)
        return self._last_trace

    def process_with_callback(self, callback: t.Callable, *args, **kwargs) -> Trace:
        """
        Events sometimes initialise the world state such as in the DP example.
        This results in an inconsistent world when re-running the code.
        This is a helper method where a callback can be passed which performs any required
        post-process operations. The callback must accept two arguments - the world
        instance and the trace of events returned by the `process` method.
        """
        ret = self.process(*args, **kwargs)
        callback(self, ret)
        return ret

    def get_origin_events(self) -> t.List[str]:
        """
        Try to automatically find the "origin" events in the world.
        These are events that are not triggered by any other event
        and can be run immediately. Events are returned in the order defined.
        """
        return [x.name for x in self.events.values() if x.triggered_by is None]

    def generate_flow_description(self, origin_events: t.List[str] = None) -> t.List[str]:
        """
        Generate a description of this world in FDL (Flow Description Language).
        """
        if origin_events is None:
            # To generate the flow description, we start with events that have no
            # triggers. These are the most likely (guaranteed?) to be top level events.
            origin_events = self.get_origin_events()

        flow = []

        for evt in origin_events:
            related_events = [
                x for x in self.events if evt == self.events[x].triggered_by
            ]

            # First generate the flow for this top level event.
            # Then, we do the same for each related event.
            flow.append(f'{evt} -> {{{",".join([e for e in related_events])}}}')
            flow.extend(self.generate_flow_description(related_events))

        return flow

    def draw_trace_graph(self, notebook: bool = True):
        """
        Visualize the last event trace resulting from processing the world.
        """
        if self._last_trace is None:
            return print(
                'No trace found. Have you called `World.process`?'
            )

        if not DRAWING_ENABLED:
            return print(
                'networkx, matplotlib, pyvis libraries required for drawing functionality.'
            )

        nodes = _nodes_from_trace(self._last_trace)
        edges = _edges_from_trace(self._last_trace)

        G = nx.DiGraph()

        origin_events = [e['event'] for e in self._last_trace]

        for node in nodes:
            if node in origin_events:
                # top level events
                G.add_node(node, size=15, group=1)
            else:
                G.add_node(node, group=2)

        G.add_edges_from(edges)

        net = Network(
            notebook=notebook,
            directed=True,
            bgcolor='#222222',
            font_color='white'
        )

        net.from_nx(G)
        return net.show("nx.html")

    def draw_flow_graph(self, notebook: bool = True):
        """
        Visualize the DFL description of this world.
        """
        flow = self.generate_flow_description()
        return visualize_dfl(flow, notebook=notebook)
