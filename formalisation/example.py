from formalisation import World

w = World()

class Fork:
    def __init__(self):
        self.in_use = False


class ForkInUse(Exception):
    pass


# Rework this to make use of ctx (for the forks)
class Philosopher:
    def __init__(self, forks):
        self.is_thinking = True
        self.is_eating = False
        self.forks = forks

    @w.event()
    def think(self, ctx):
        self.forks[0].in_use = False
        self.forks[1].in_use = False

        self.is_thinking = True
        self.is_eating = False

    @w.event('dine')
    def eat(self, ctx):
        if self.forks[0].in_use or self.forks[1].in_use:
            raise ForkInUse

        self.forks[0].in_use = True
        self.forks[1].in_use = True

        self.is_eating = True
        self.is_thinking = False


@w.event()
def dine(ctx):
    n_philosophers = 5

    ctx.forks = [Fork() for _ in range(n_philosophers)]  # as many forks as philosophers

    for x in range(n_philosophers):
        w.add_agent(Philosopher(
            (ctx.forks[x], ctx.forks[(x + 1) % len(ctx.forks)])
        ))


if __name__ == '__main__':
    w.process(['dine'])
