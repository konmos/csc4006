import itertools
import typing as t
from collections import namedtuple
from dataclasses import dataclass
from threading import Thread
from queue import Empty, Queue
from types import SimpleNamespace

try:
    import networkx as nx
    from pyvis.network import Network
    DRAWING_ENABLED = True
except ImportError:
    DRAWING_ENABLED = False


def _check_drawing_libs():
    if not DRAWING_ENABLED:
        print(
            'networkx, matplotlib, pyvis libraries required for drawing functionality.'
        )

    return DRAWING_ENABLED


# EventConfig allows the user to overwrite behavior of event
# propagation on the fly;
#  targets = list of targets this event should propagate to (agents)
#  no_propagate = boolean indicating whether related events should be triggered
#  event_overwrite = trigger this event instead
#  args = args to pass to *ALL* triggered events
#  kwargs = kwargs to pass to *ALL* triggered events
#
# NOTE: Complex examples which rely on EventConfig generate
# unreliable FDL. What can we do about this?
EventConfig = namedtuple(
    'EventConfig',
    ['targets', 'no_propagate', 'event_overwrite', 'args', 'kwargs'],
    defaults=[None, False, None, [], {}]
)

Trace = t.List[t.Dict[str, t.Union[str, 'Trace']]]
Nodes = t.List[str]
Edges = t.List[t.Tuple[str, str]]
EventType = t.Union[str, t.Tuple[str, EventConfig]]


def _graph_from_trace(events: Trace, unique_events: bool = False, *,
                      last_event: str = None, event_counter: int = 0) -> Edges:
    """
    Recursively parse an execution trace and return a set of nodes and edges
    to represent it graphically.
    """
    if events is None:
        return []

    nodes, edges = [], []
    _event_counter = event_counter

    for event in events:
        if not unique_events:
            dest = event['event']
        else:
            _id = event['id'] if event['id'] is not None else _event_counter
            dest = f'{_id}:{event["event"]}'
            _event_counter += 1

        if event.get('agent') is not None:
            dest += f':{event["agent"][0]}'

        nodes.append(dest)

        if last_event is not None:
            edges.append((last_event, dest))

        n, e = _graph_from_trace(
            event['triggered'], unique_events, last_event=dest, event_counter=_event_counter
        )

        edges.extend(e)
        nodes.extend(n)

        _event_counter += len(n)

    return set(nodes), set(edges)


def _graph_from_fdl(fdl: t.Union[str, t.List[str]]) -> t.Tuple[Nodes, Edges]:
    """
    Return a set of nodes and edges for a FDL description.
    """
    if isinstance(fdl, str):
        fdl = fdl.split('\n')

    nodes, edges = [], []

    for f in fdl:
        source, destinations = [x.strip() for x in f.split('->')]

        nodes.append(source)

        for dest in destinations[1:-1].split(','):  # Ignore braces
            dest = dest.strip()

            if not dest:
                continue

            nodes.append(dest)
            edges.append((source, dest))

    return nodes, edges


def visualize_fdl(fdl: t.Union[str, t.List[str]], notebook: bool = True, fname: str = None):
    """
    Draw the visual representation of a FDL description.
    """
    if not _check_drawing_libs():
        return

    G = nx.DiGraph()
    nodes, edges = _graph_from_fdl(fdl)

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    net = Network(
        notebook=notebook,
        directed=True,
        bgcolor='#222222',
        font_color='white'
    )

    net.from_nx(G)
    return net.show(fname or 'fdl.html')


@dataclass
class Event:
    name: str
    func: t.Callable
    triggered_by: t.Optional[str]


# @dataclass
# class ProcessingStep:
#     """
#     Marker used for live stepping.
#     """
#     # The event representing this step.
#     event: EventType

#     # Have we processed this event before?
#     done: bool = False

#     # List of agents which have successfully executed this event.
#     # If this is a global event, -1 is appended on success instead.
#     agents: t.List[t.Union[int, t.Tuple[int, int]]] = None

#     # List of steps which this event triggered.
#     triggered: t.List['ProcessingStep'] = None


class ProcessingStep:
    next_id = itertools.count()

    def __init__(self, event, done = False, agents = None, triggered = None) -> None:
        self.event = event
        self.done = done
        self.agents = agents or []
        self.triggered = triggered or []
        self.id = next(ProcessingStep.next_id)


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


class ThreadedAgent(Thread, Agent):
    def __init__(self, agent_id: t.Tuple[int, int], *args, **kwargs) -> None:
        Thread.__init__(self, *args, **kwargs)
        Agent.__init__(self, agent_id)

        self._stop_cycle = False
        self.event_q = Queue()

    def dispatch_event(self, event, *args):
        self.event_q.put((event, *args))

    def process_event(self, event, ctx, *args, **kwargs):
        # Event will be of the format "Class.event"
        evt = event.split('.')[-1]
        return getattr(self, evt)(ctx, *args, **kwargs)

    def join(self, *args, **kwargs):
        self._stop_cycle = True
        super().join(*args, **kwargs)

    def run(self):
        while not self._stop_cycle:
            try:
                event, q, ctx, args, kwargs = self.event_q.get(timeout=2)
            except Empty:
                continue

            try:
                ret = self.process_event(event, ctx, *args, **kwargs)
                q.put((self, None, ret))
            except Exception as e:
                q.put((self, e, None))


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
        self._processing_state = None  # Used for live stepping

    def reset_agents(self) -> None:
        """
        Remove all agents. Useful for cleanup if they are added by an event.
        """
        self.agents = []

    def add_event(self, event: t.Callable, event_name: str, triggered_by: t.Optional[str] = None) -> None:
        """
        Create and add a new event instance.
        Events should return either `None` or `EventConfig`.
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

    def _get_related_events(self, event_name, cfg=None):
        """
        Generate a list of events to trigger next, taking into account the current config.
        """
        cfg = cfg or EventConfig()

        # Force no event triggers.
        if cfg.no_propagate:
            return []

        # Return the event specified instead.
        if cfg.event_overwrite is not None:
            return [(cfg.event_overwrite, cfg)]

        # The config gets passed on to all further events but
        # not all options will be applicable or make sense in this context.
        # This is necessary, however, to pas the options that *do* make sense
        # for these events, such as args and kwargs.
        return [
            (x.name, cfg) for x in self.events.values() if event_name == x.triggered_by
        ]

    def _process(self, events: t.List[t.Union[EventType, ProcessingStep]] = None,
                 ignore_exceptions: bool = False, single_step: bool = False) -> t.Tuple[Trace, bool]:
        """
        Process a series of events recursively. Each event can trigger other events.

        Return a tuple containing the trace of events, and a boolean indicating whether or not
        we made a new step. If no step has been made, it can be concluded that execution is over.
        """
        if events is None:
            events = self.get_origin_events()

        _events = []

        # Used for live stepping - indicates if we made a new step in this
        # recursive step. If so, we have to return.
        # Live stepping works almost identical to a normal execution with the exception
        # that we don't execute events which were previously executed. We only
        # update the trace in these circumstances. Thus, we must keep track
        # of which events are "done" and also whether the event was executed
        # and by whom. This is because an event may not necessarily be a part of the
        # trace, even if it is "done" (i.e., due to exceptions).
        _stepped = False

        for event in events:
            # If we made a step, return.
            # Remember that this also must be checked by all upper levels
            # of the recursion (if any).
            if single_step and _stepped:
                return _events, True

            _e = event

            # If `single_step` is true, events MUST have the type `list[ProcessingStep]`.
            if single_step:
                _e = event.event

            if isinstance(_e, tuple):
                event_name, cfg = _e
            else:
                event_name, cfg = _e, EventConfig()

            trace = []
            evt = self.events[event_name]

            # _next_events keeps track of all events which should be triggered next.
            # Care should be taken to prevent events being executed multiple times.
            # _done_configs keeps track of which event configurations have already
            # been passed to _next_events. This helps avoid duplicates.
            _next_events, _done_configs = [], []

            if '.' in event_name:
                agent = event_name.split('.')[0]

                # Filter out appropriate agents.
                agents, q = [x for x in self.agents if x.__class__.__name__ == agent], None

                if cfg.targets is not None:
                    agents = [x for x in agents if x in cfg.targets]

                # Output queue for threading.
                if agents and isinstance(agents[0], ThreadedAgent):
                    q = Queue(maxsize=len(agents))

                # Below this point, the construct `if not single_step or not event.done` is used
                # quite frequently. For brevity, it will be explained here. It is quite messy
                # and not ideal, however, what we are essenitally just ensuring that *either*
                # this event has NOT already been processed previously OR we are not live stepping
                # (in which case we should process it anyway).

                for a in agents:
                    if q is None:
                        # Non-threaded agent
                        try:
                            if not single_step or not event.done:
                                # We are not live stepping, or this event hasn't been done yet.
                                ret = evt.func(a, self.ctx, *cfg.args, **cfg.kwargs)  # Pass the instance reference

                            if single_step and not event.done:
                                # We are live stepping and this event is new.
                                event.agents.append(a._agent_id)

                            if not single_step or a._agent_id in event.agents:
                                # We are not live stepping OR this agent already executed this event.
                                trace.append({
                                    'event': event_name,
                                    'agent': a._agent_id,
                                    'triggered': [],
                                    'id': f'{a.global_id}{event.id}' if single_step else None  # For live stepping
                                })

                            if not single_step or not event.done:
                                # We are not live stepping OR this event hasn't been processed yet.
                                if ret not in _done_configs:
                                    _done_configs.append(ret)
                                    _next_events.extend(self._get_related_events(event_name, ret))
                        except Exception as exc:
                            if not ignore_exceptions:
                                raise exc
                    else:
                        # Threaded agent.
                        # Live stepping not supported here.
                        # Here we just dispatch the events to all applicable agents.
                        # The results get collected later.
                        a.dispatch_event(event_name, q, self.ctx, cfg.args, cfg.kwargs)

                # If we had threaded agents, we must collect and process all results.
                if q is not None:
                    # Block until all results have been processed.
                    _processed = 0  # <= len(agents)

                    while _processed != len(agents):
                        # (agent: Agent, exception: Exception | None, ret: Any)
                        a, exception, ret = q.get()

                        if exception is None:
                            trace.append({
                                'event': event_name,
                                'agent': a._agent_id,
                                'triggered': []
                            })

                            if ret not in _done_configs:
                                _done_configs.append(ret)
                                _next_events.extend(self._get_related_events(event_name, ret))
                        else:
                            if not ignore_exceptions:
                                raise exception

                        _processed += 1
            else:
                # In terms of live stepping here, the process and logic is similar
                # to that in the above if (agent) statement.
                try:
                    if not single_step or not event.done:
                        ret = evt.func(self.ctx, *cfg.args, **cfg.kwargs)

                    if single_step and not event.done:
                        event.agents.append(-1)  # Append -1 instead of agent_id

                    if not single_step or -1 in event.agents:
                        trace.append({
                            'event': event_name,
                            'triggered': [],
                            'id': f'0{event.id}' if single_step else None  # For live stepping
                        })

                    if not single_step or not event.done:
                        _next_events.extend(self._get_related_events(event_name, ret))
                except Exception as exc:
                    if not ignore_exceptions:
                        raise exc

            if single_step and not event.done:
                # This marks one step.
                _stepped = True
                event.done = True
                event.triggered = [ProcessingStep(event=x, agents=[]) for x in _next_events]

            # Check if the event was triggered.
            # It may have been triggered only once, or by every (or some) agents.
            # We also checked if we made a step if live stepping. If so, we can
            # return at this point.
            if not trace:
                continue

            if not single_step or not _stepped:
                # At this point, we know the event was triggered.
                # We don't know how many times it was triggered, however, or if any exceptions occurred.
                # Search for related events and relegate them to a recursive call.
                related_events = event.triggered if single_step else _next_events

                triggered, _stepped = self._process(
                    related_events,
                    ignore_exceptions=ignore_exceptions,
                    single_step=single_step
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

        return _events, _stepped

    def process(self, *args, **kwargs) -> Trace:
        """
        Run `World._process` and set `self._last_trace`.
        """
        self._last_trace, _ = self._process(*args, **kwargs)

        # We must tell all threaded agents to quit.
        # TODO: Should we somehow start them here also?
        #       This gets tricky if events create agents.
        for a in self.agents:
            if isinstance(a, ThreadedAgent):
                a.join()

        return self._last_trace

    def step(self, events=None, *args, **kwargs):
        current_steps = []

        if self._processing_state is None:
            if events is None:
                events = self.get_origin_events()

            for e in events:
                current_steps.append(ProcessingStep(event=e, agents=[]))

            self._processing_state = current_steps

        self._last_trace, stepped = self._process(
            self._processing_state, single_step=True, *args, **kwargs
        )

        return stepped

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

    def generate_fdl(self) -> t.List[str]:
        """
        Generate a description of this world in FDL (Flow Description Language).
        This method generates the FDL based on a set of "origin events"
        from which the FDL stems. To generate generic FDL based on ALL events,
        use `generate_fdl`.
        """
        flow = []

        for e in self.events.values():
            related_events = [
                x.name for x in self.events.values() if x.triggered_by == e.name
            ]

            flow.append(f'{e.name} -> {{{",".join([e for e in related_events])}}}')

        return flow

    def draw_trace_graph(self, notebook: bool = True, unique_events: bool = False,
                         fname: str = None, show: bool = True):
        """
        Visualize the last event trace resulting from processing the world.
        """
        if not _check_drawing_libs():
            return

        if self._last_trace is None:
            return print(
                'No trace found. Have you called `World.process`?'
            )

        nodes, edges = _graph_from_trace(self._last_trace, unique_events)

        G = nx.DiGraph()

        origin_events = [e['event'] for e in self._last_trace]

        for node in nodes:
            if node in origin_events or (unique_events and node.split(':', 1)[1] in origin_events):
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

        if show:
            return net.show(fname or 'trace.html')

        return net.write_html(fname or 'trace.html')

    def draw_flow_graph(self, notebook: bool = True, fname: str = None):
        """
        Visualize the FDL description of this world.
        """
        flow = self.generate_fdl()
        return visualize_fdl(flow, notebook=notebook, fname=fname)
