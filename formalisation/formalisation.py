import typing as t
from dataclasses import dataclass
from types import SimpleNamespace


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

    def reset_agents(self):
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

    def process(self, events: t.List[str], ignore_exceptions: bool = False) -> None:
        """
        Process a series of events recursively. Each event can trigger other events.
        """
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

            triggered = self.process(
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

    def process_with_callback(self, callback: t.Callable, *args, **kwargs):
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

    def generate_flow_description(self, origin_events: t.List[str] = None):
        """
        Generate a description of this world in FDL (Flow Description Language).
        """
        if origin_events is None:
            # To generate the flow description, we start with events that have no
            # triggers. These are the most likely (guaranteed?) to be top level events.
            origin_events = [x.name for x in self.events.values() if x.triggered_by is None]

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
