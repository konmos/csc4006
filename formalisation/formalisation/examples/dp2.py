import time
from ..formalisation import World, ThreadedAgent

w = World()

class Fork:
    def __init__(self):
        self.in_use = False


class ForkInUse(Exception):
    pass


class Philosopher(ThreadedAgent):
    def __init__(self, *args, **kwargs):
        super().__init__ (*args, **kwargs)

        self.is_thinking = True
        self.is_eating = False

    def get_forks(self, ctx):
        return ctx.forks[self.agent_id], ctx.forks[(self.agent_id + 1) % len(ctx.forks)]

    @w.event('dine')
    def think(self, ctx):
        f = self.get_forks(ctx)

        f[0].in_use = False
        f[1].in_use = False

        self.is_thinking = True
        self.is_eating = False

    @w.event('Philosopher.think')
    def eat(self, ctx):
        f = self.get_forks(ctx)

        if f[0].in_use or f[1].in_use:
            raise ForkInUse

        f[0].in_use = True
        f[1].in_use = True

        self.is_eating = True
        self.is_thinking = False

    def process_event(self, event, ctx, *args, **kwargs):
        # TODO: Better interface for this?
        #       Some way to automatically call events?
        if event == 'Philosopher.eat':
            self.eat(ctx, *args, **kwargs)
        else:
            self.think(ctx, *args, **kwargs)

        time.sleep(2)


@w.event()
def dine(ctx):
    n_philosophers = 5

    ctx.forks = [Fork() for _ in range(n_philosophers)]  # as many forks as philosophers

    for _ in range(n_philosophers):
        w.add_agent(Philosopher)

    # Start threads
    for philosopher in w.agents:
        philosopher.start()


if __name__ == '__main__':
    w.process_with_callback(
        lambda w, r: w.reset_agents(),
        ignore_exceptions=True
    )
