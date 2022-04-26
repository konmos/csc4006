# This file is a part of the final year project "Story and Software" (CSC4006).
# Author: Konrad Mosoczy (Queen's University Belfast - QUB)
# https://github.com/konmos/csc4006 (also available on GitLab)
# ------------------------------------------------------------------------------
# This is the example as covered in the developer guide (README).

import random
from formalisation.formalisation import World, Agent, EventConfig

w = World()


class Paul(Agent):
    @w.event('apple_falls')
    def eat_apple(self, ctx):
        print('an apple has been eaten')

        if random.random() > 0.5:
            return EventConfig(no_propagate=True)

    @w.event('Paul.eat_apple')
    def pick_apple(self, ctx):
        print('another apple has been picked and eaten')


@w.event()
def paul_rests(ctx):
    w.add_agent(Paul)


@w.event()
def apple_falls(ctx):
    print('an apple has fallen')


if __name__ == '__main__':
    w.process_with_callback(
        lambda w, r: w.reset_agents(),
        ['paul_rests', 'apple_falls']
    )
