import time
import threading
from ..formalisation import World, ThreadedAgent

w = World()

class Fork:
    def __init__(self):
        self.in_use = False


class ForkInUse(Exception):
    pass


# test procedure as described in the paper
def test(ctx, k):
    c = ctx.table

    if c[(k-1) % len(c)].c != 2 and c[k].c == 1 and c[(k+1) % len(c)].c != 2:
        c[k].c = 2
        c[k].prisem.release()


class Philosopher(ThreadedAgent):
    def __init__(self, *args, **kwargs):
        super().__init__ (*args, **kwargs)

        self.is_thinking = True
        self.is_eating = False

        self.c = 0  # state; 0 = thinking, 1 = hungry, 2 = eating
        self.prisem = threading.Semaphore(0)  # private semaphore

    def get_forks(self, ctx):
        return ctx.forks[self.agent_id], ctx.forks[(self.agent_id + 1) % len(ctx.forks)]

    @w.event('dine')
    def think(self, ctx):
        # Signal that we're not eating.
        ctx.mutex.acquire()
        self.c = 0
        test(ctx, (self.global_id + 1) % len(ctx.table))
        test(ctx, (self.global_id - 1) % len(ctx.table))
        ctx.mutex.release()

        f = self.get_forks(ctx)

        f[0].in_use = False
        f[1].in_use = False

        self.is_thinking = True
        self.is_eating = False

    @w.event('Philosopher.think')
    def eat(self, ctx):
        # Wait until we can eat.
        ctx.mutex.acquire()
        self.c = 1
        test(ctx, self.global_id)
        ctx.mutex.release()
        self.prisem.acquire()

        # Now we can eat.
        f = self.get_forks(ctx)

        if f[0].in_use or f[1].in_use:
            raise ForkInUse

        f[0].in_use = True
        f[1].in_use = True

        self.is_eating = True
        self.is_thinking = False

        time.sleep(2)  # Eat for some period of time

        # Now this is interesting.
        # The way the formalisation framework is (currently) structured
        # is that it processes events sequentially. That is to say,
        # ALL Philosopher.eat events must finish before any Philosopher.think
        # events get triggered. The order of Philsopher.eat events is arbitrary,
        # however there is a form of implicit synchronization introduced here
        # in that no philosopher can think until all philosophers have finished eating.
        # We have to call `self.think` here so that all locks get properly released and
        # any other philsophers can start eating. This call, however, does not get
        # mapped by the framework as we are calling it manually...
        # In a sense (as far as the framework is concerned) we are thinking while eating
        # which violates the event "flow". Perhaps this implies that there should be some
        # sort of "intermediary" stage between finishing eating and starting thinking.
        # Another potential solution is rewriting the event decorator so that it itself
        # updates the trace (as opposed to this logic happening inside `World._process`).
        # This, however, potentially complicates things significantly.
        self.think(ctx)


@w.event()
def dine(ctx):
    n_philosophers = 5

    ctx.forks = [Fork() for _ in range(n_philosophers)]  # as many forks as philosophers

    for _ in range(n_philosophers):
        w.add_agent(Philosopher)

    ctx.mutex = threading.Semaphore(1)
    ctx.table = w.agents

    # Start threads
    for philosopher in w.agents:
        philosopher.start()


if __name__ == '__main__':
    w.process_with_callback(
        lambda w, r: w.reset_agents()
    )
