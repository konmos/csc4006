import click
import importlib

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


if __name__ == '__main__':
    cli()
