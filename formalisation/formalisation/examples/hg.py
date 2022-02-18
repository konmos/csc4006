import random
import math
from ..formalisation import EventConfig, World, Agent

w = World()


RADIUS = 15
START_POINT = (0, 0)
END_POINT = (100, 100)


def get_random_point(radius, centerX, centerY):
    # https://stackoverflow.com/a/50746409
    r = radius * math.sqrt(random.random())
    theta = random.random() * 2 * math.pi
    return centerX + r * math.cos(theta), centerY + r * math.sin(theta)


def gen_random_walk(origin, end, radius):
    distance = math.dist(origin, end)
    last_point = origin

    yield origin

    while distance > radius:
        new_point = get_random_point(radius, *last_point)
        dist = math.dist(new_point, end)

        while dist >= distance:
            new_point = get_random_point(radius, *last_point)
            dist = math.dist(new_point, end)

        distance = dist
        last_point = new_point

        yield last_point

    yield end


def check_visibility(current_point, points, view_distance):
    visible = []

    for p in points:
        if p == current_point:
            continue

        if math.dist(p, current_point) <= view_distance:
            visible.append(p)

    return visible


class Pebble():
    def __init__(self, position, visited=False):
        self.pos = position
        self.visited = visited

    def __repr__(self):
        return f'<Pebble {self.pos}>'


class Hansel(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.steps = []  # dropped pebbles
        self.path = []   # path taken when following pebbles backwards

        self._last_pebble = None  # marker when moving backwards
        self._walk = gen_random_walk(START_POINT, END_POINT, RADIUS)  # step generator

    @w.event('Hansel.step_forward')
    def step_forward(self, ctx):
        try:
            p = Pebble(next(self._walk))
        except StopIteration:
            return EventConfig(event_overwrite='forest')

        self.steps.append(p)

    @w.event('Hansel.follow_back')
    def follow_back(self, ctx):
        if self._last_pebble is None:
            next_pebble = self.steps[-1]
        else:
            if self._last_pebble.pos == START_POINT:
                return EventConfig(event_overwrite='home', args=[True])

            visible_locations = check_visibility(
                self._last_pebble.pos,
                [x.pos for x in self.steps],
                RADIUS
            )

            try:
                next_pebble = next(
                    x for x in self.steps if x.pos in visible_locations and not x.visited
                )
            except StopIteration:
                next_pebble = None

        if next_pebble is not None:
            self._last_pebble = next_pebble
            self._last_pebble.visited = True
            self.path.append(self._last_pebble)
        else:
            return EventConfig(event_overwrite='home', args=[True])


@w.event()
def home(ctx, end=False):
    if not end:
        w.add_agent(Hansel)

        return EventConfig(
            event_overwrite='Hansel.step_forward'
        )


@w.event()
def forest(ctx):
    return EventConfig(
        event_overwrite='Hansel.follow_back'
    )
