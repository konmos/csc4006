# This file is a part of the final year project "Story and Software" (CSC4006).
# Author: Konrad Mosoczy (Queen's University Belfast - QUB)
# https://github.com/konmos/csc4006 (also available on GitLab)
# ------------------------------------------------------------------------------
# This is the Dining Philosophers (non-threaded) example for the story-thinking framework.

from ..formalisation import World, Agent

w = World()

class Fork:
    """
    A single fork.
    """
    def __init__(self):
        self.in_use = False  # True if a philosopher is eating with this fork.


class ForkInUse(Exception):
    """Raised when an attempt is made to eat with a fork which is already used."""


class Philosopher(Agent):
    """
    Represents a philosopher.
    Each philosopher is either thinking or eating at all times.
    """
    def __init__(self, *args, **kwargs):
        super().__init__ (*args, **kwargs)

        # Think by default.
        self.is_thinking = True
        self.is_eating = False

    def get_forks(self, ctx):
        """Return the appropriate forks from the context."""
        return ctx.forks[self.agent_id], ctx.forks[(self.agent_id + 1) % len(ctx.forks)]

    @w.event('dine')
    def think(self, ctx):
        """Philosopher thinks and stops eating."""
        f = self.get_forks(ctx)

        f[0].in_use = False
        f[1].in_use = False

        self.is_thinking = True
        self.is_eating = False

    @w.event('Philosopher.think')
    def eat(self, ctx):
        """Philosopher eats and stops thinking."""
        f = self.get_forks(ctx)

        if f[0].in_use or f[1].in_use:
            raise ForkInUse

        f[0].in_use = True
        f[1].in_use = True

        self.is_eating = True
        self.is_thinking = False


@w.event()
def dine(ctx):
    n_philosophers = 5

    ctx.forks = [Fork() for _ in range(n_philosophers)]  # As many forks as philosophers.

    for _ in range(n_philosophers):
        w.add_agent(Philosopher)


if __name__ == '__main__':
    w.process_with_callback(
        lambda w, r: w.reset_agents(),
        ignore_exceptions=True
    )
