import click
import importlib
from typing import get_type_hints

from formalisation.formalisation import World, visualize_fdl


def _get_world(module):
    _mod = importlib.import_module(module)
    return [x for x in vars(_mod).values() if isinstance(x, World)][0]


@click.group()
def cli():
    pass


@cli.command()
@click.argument('fdl')
def draw_fdl(fdl):
    visualize_fdl(fdl, notebook=False)


@cli.command()
@click.argument('fname')
@click.option('-origin', default=None, type=str, help='list of origin events')
@click.option('-ix', default=False, is_flag=True, help='ignore exceptions')
@click.option('-trace', default=None, help='output file for trace visualization', type=str)
@click.option('-unique', default=False, help='output unique nodes when used with -trace', is_flag=True)
@click.option('-fdl', default=None, help='output file for FDL visualization', type=str)
def run(fname, origin=None, ix=False, trace=None, unique=False, fdl=None):
    world = _get_world(fname)

    if origin is not None:
        origin_events = [x.strip() for x in origin.split(',')]
    else:
        origin_events = world.get_origin_events()

    print(f'Running with {origin_events}...\n')

    world.process(
        events=origin_events,
        ignore_exceptions=ix
    )

    print('Done.')

    if fdl is not None:
        world.draw_flow_graph(notebook=False, fname=fdl)

    if trace is not None:
        world.draw_trace_graph(notebook=False, fname=trace, unique_events=unique)


class LiveStepper:
    def __init__(self, world):
        self.world = world
        self.exit = False

    def parse_command(self, command):
        cmd, *args = [x.strip() for x in command.split(' ')]

        try:
            meth = getattr(self, f'cmd_{cmd}')
        except AttributeError:
            return 'Invalid Command.'

        type_hints = list(get_type_hints(meth).values())

        for i in range(len(args)):
            if i < len(type_hints):
                args[i] = type_hints[i](args[i])

        return meth(*args)

    def cmd_help(self):
        return (
            'Available Commands:\n'
            '  exit: Stop stepping and exit the program.\n'
            '  step [X]: Make X steps (default = 1).\n'
            '  trace: Return current raw trace.\n'
            '  fdl: Return the FDL for this world.\n'
            '  trace_graph [unique]: Draw the current trace.\n'
            '  fdl_graph: Draw the FDL for this world.'
        )

    def cmd_exit(self):
        self.exit = True

    def cmd_step(self, by: int = 1):
        ret = False

        for _ in range(by):
            ret = self.world.step()

        return ret

    def cmd_trace(self):
        return self.world._last_trace

    def cmd_fdl(self):
        return '\n'.join(self.world.generate_fdl())

    def cmd_trace_graph(self, *args):
        self.world.draw_trace_graph(
            notebook=False,
            unique_events='unique' in args
        )

    def cmd_fdl_graph(self):
        self.world.draw_fdl_graph(notebook=False)


@cli.command()
@click.argument('fname')
def step(fname):
    world = _get_world(fname)
    stepper = LiveStepper(world)

    while not stepper.exit:
        print(stepper.parse_command(input('> ')))


if __name__ == '__main__':
    cli()
