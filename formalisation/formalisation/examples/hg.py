# This file is a part of the final year project "Story and Software" (CSC4006).
# Author: Konrad Mosoczy (Queen's University Belfast - QUB)
# https://github.com/konmos/csc4006 (also available on GitLab)
# ------------------------------------------------------------------------------
# This is the Hansel and Gretel example for the story-thinking framework.

import random
import math
from ..formalisation import EventConfig, World, Agent

w = World()

# Constants.
# Radius controls how often a pebble is dropped and what pebbles are visible.
# Start point is the origin (home location).
# End point is the point at which Hansel turns around.
RADIUS = 15
START_POINT = (0, 0)
END_POINT = (100, 100)


def get_random_point(radius, centerX, centerY):
    """Generate a random point within a specified radius from a center point."""
    # https://stackoverflow.com/a/50746409
    r = radius * math.sqrt(random.random())
    theta = random.random() * 2 * math.pi
    return centerX + r * math.cos(theta), centerY + r * math.sin(theta)


def gen_random_walk(origin, end, radius):
    """
    Generate a random walk from a start point to end point.
    Each point is within the specified radius.
    """
    distance = math.dist(origin, end)
    last_point = origin

    yield origin

    # If we haven't reached the end point yet...
    while distance > radius:
        new_point = get_random_point(radius, *last_point)
        dist = math.dist(new_point, end)

        # Keep only the points which get us closer to the destination.
        while dist >= distance:
            new_point = get_random_point(radius, *last_point)
            dist = math.dist(new_point, end)

        distance = dist
        last_point = new_point

        yield last_point

    yield end  # Make sure to return the end point once we're done.


def check_visibility(current_point, points, view_distance):
    """
    Check which points are visible from a specified location,
    given a radius within which we can see.
    """
    visible = []

    for p in points:
        if p == current_point:
            continue

        if math.dist(p, current_point) <= view_distance:
            visible.append(p)

    return visible


class Pebble():
    """Represents a single pebble."""
    def __init__(self, position, visited=False):
        self.pos = position
        self.visited = visited

    def __repr__(self):
        return f'<Pebble {self.pos}>'


class Hansel(Agent):
    """Represents Hansel."""
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
            # Once we've reached the end, override the event flow
            # to indicate that Hansel should head back home.
            return EventConfig(event_overwrite='forest')

        self.steps.append(p)

    @w.event('Hansel.follow_back')
    def follow_back(self, ctx):
        if self._last_pebble is None:
            next_pebble = self.steps[-1]
        else:
            if self._last_pebble.pos == START_POINT:
                # We've reached home again. We're done.
                return EventConfig(event_overwrite='home', args=[True])

            # Try to pick another point to move to.
            # It must be a point which we can see and which hasn't been visited yet.
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
            # If we're not stuck, at the pebble to our path.
            self._last_pebble = next_pebble
            self._last_pebble.visited = True
            self.path.append(self._last_pebble)
        else:
            # This breaks the recursion and allows us to exit.
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
