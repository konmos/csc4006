from enum import Enum, auto
from collections import Counter
from ..formalisation import World, Agent, EventConfig

w = World()


class Observation(Enum):
    '''
    Represents an observation that a general has made on a particular city.
    '''
    ATTACK = auto()
    RETREAT = auto()


class EnemyCity:
    def __init__(self, should_attack):
        self.should_attack = should_attack


class General(Agent):
    def __init__(self, _id, is_traitor=False):
        super().__init__(_id)

        self._objective_observation = None
        self.observations = []
        self.is_traitor = is_traitor

    @w.event('camp')
    def make_observation(self, ctx):
        self._objective_observation = (Observation.RETREAT, Observation.ATTACK)[ctx.city.should_attack]

    @w.event('General.listen')
    def speak(self, ctx, to_generals, m, previous_order=None):
        o = Observation.RETREAT

        if not self.is_traitor:
            if previous_order is not None:
                o = previous_order
            else:
                o = self._objective_observation

        return EventConfig(targets=to_generals, args=[o, m, to_generals])

    @w.event('General.speak')
    def listen(self, ctx, observation, m, generals):
        self.observations.append(observation)

        if m > 0:
            _generals = [x for x in generals if x is not self]

            return EventConfig(
                targets=[self],
                args=[_generals, m-1, observation]
            )

        return EventConfig(
            no_propagate=True
        )

    def make_decision(self):
        return Counter(self.observations).most_common()


@w.event()
def camp(ctx):
    ctx.city = EnemyCity(True)

    for i in range(4):
        w.add_agent(General, i >= 2)


@w.event()
def make_order(ctx):
    # First general is commander
    return EventConfig(
        event_overwrite='General.speak',
        targets=[w.agents[0]],
        args=[w.agents[1:], len([x for x in w.agents if x.is_traitor])]
    )


if __name__ == '__main__':
    w.process_with_callback(
        lambda w, r: w.reset_agents(),
        ['camp', 'make_order']
    )
