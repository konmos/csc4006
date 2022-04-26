# This file is a part of the final year project "Story and Software" (CSC4006).
# Author: Konrad Mosoczy (Queen's University Belfast - QUB)
# https://github.com/konmos/csc4006 (also available on GitLab)
# ------------------------------------------------------------------------------
# This is the Byzantine Generals example for the story-thinking framework.

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
    """
    Enemy City; this is generally used as a singleton.
    """
    def __init__(self, should_attack):
        self.should_attack = should_attack


class General(Agent):
    """
    Represents a single General.
    The general can be either a traitor or loyal.
    """
    def __init__(self, _id, is_traitor=False):
        super().__init__(_id)

        self._objective_observation = None
        self.observations = []
        self.is_traitor = is_traitor

    @w.event('camp')
    def make_observation(self, ctx):
        """Make the initial observation. Triggered by `camp` event."""
        self._objective_observation = (Observation.RETREAT, Observation.ATTACK)[ctx.city.should_attack]

    @w.event('General.listen')
    def speak(self, ctx, to_generals, m, previous_order=None):
        """
        Report an observation to others.
        """
        # The traitor simply returns RETREAT.
        # Loyal generals return the correct observation;
        # that is, the one the previous general made, or their own objective
        # observation if there is no previous order.
        o = Observation.RETREAT

        if not self.is_traitor:
            if previous_order is not None:
                o = previous_order
            else:
                o = self._objective_observation

        # Pass args and propagate only to the necessary generals.
        return EventConfig(targets=to_generals, args=[o, m, to_generals])

    @w.event('General.speak')
    def listen(self, ctx, observation, m, generals):
        """
        Receive an observation from some other general.
        """
        self.observations.append(observation)

        if m > 0:
            # Re-calculate the generals that need to receive the message
            # and decrement m by 1.
            _generals = [x for x in generals if x is not self]

            return EventConfig(
                targets=[self],
                args=[_generals, m-1, observation]
            )

        # We've finished.
        return EventConfig(
            no_propagate=True
        )

    def make_decision(self):
        # Most common observation.
        return Counter(self.observations).most_common()


@w.event()
def camp(ctx):
    """
    Initialise the city and agents.
    """
    ctx.city = EnemyCity(True)

    for i in range(4):
        w.add_agent(General, i >= 2)


@w.event()
def make_order(ctx):
    """
    Commander makes the first order and kicks off the 'recursive' algorithm.
    """
    # First general is commander.
    # Force the commander to speak by setting `targets`.
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
