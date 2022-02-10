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
        self.agents: t.List[object] = []
        # self.components = []
        self.events: t.Mapping[str, Event] = {}
        self.ctx: SimpleNamespace = SimpleNamespace()

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

    def process(self, events: t.List[str]) -> None:
        """
        Process a series of events recursively.
        Each event can trigger other events.
        """
        for e in events:
            evt = self.events[e]

            if '.' in e:
                agent = e.split('.')[0]

                for a in self.agents:
                    if a.__class__.__name__ == agent:
                        # Pass the instance reference
                        evt.func(a, self.ctx)
            else:
                evt.func(self.ctx)

            # Trigger related events
            related_events = [
                x for x in self.events if e == self.events[x].triggered_by
            ]

            self.process(related_events)
