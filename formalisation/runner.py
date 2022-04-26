import click
import json
import importlib
from typing import get_type_hints
from http.server import HTTPServer, BaseHTTPRequestHandler

from formalisation.formalisation import World, visualize_fdl, _graph_from_trace


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
    def __init__(self, world, origin=None, ix=False):
        self.world = world
        self.exit = False
        self.origin = origin
        self.ix = ix

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
            ret = self.world.step(events=self.origin, ignore_exceptions=self.ix)

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
@click.option('-origin', default=None, type=str, help='list of origin events')
@click.option('-ix', default=False, is_flag=True, help='ignore exceptions')
def step(fname, origin=None, ix=False):
    world = _get_world(fname)
    stepper = LiveStepper(
        world, [x.strip() for x in origin.split(',')] if origin else None, ix
    )

    while not stepper.exit:
        print(stepper.parse_command(input('> ')))


def _server_factory(world, origin, ignore_exceptions):
    class S(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.world = world  # Have to do this before the super.__init__
            self.ignore_exceptions = ignore_exceptions
            self.origin = origin
            super().__init__(*args, **kwargs)

        def _set_headers(self, content_type=None):
            self.send_response(200)
            self.send_header('Content-type', content_type or 'text/html')
            self.end_headers()

        def do_GET(self):
            """
            Reset the last trace and return the base HTML template.
            This does NOT reset the world state.
            """
            self._set_headers()

            self.world._last_trace = []

            with open('stepping.html', 'r') as fd:
                text = fd.read()

            self.wfile.write(text.encode('utf8'))

        def do_POST(self):
            """
            Perform a step and return the graph in vis.js format.
            """
            self._set_headers(content_type='text/json')

            # We don't care about the path.
            # Assume all POST requests represent a single step.
            self.world.step(events=self.origin, ignore_exceptions=self.ignore_exceptions)

            nodes, edges = [], []

            # Calculate the graph with unique nodes.
            n, e = _graph_from_trace(self.world._last_trace, True)

            # Process the graph so that vis.js understands it.
            for node in n:
                nodes.append({
                    'font': {'color': 'white'},
                    'group': 1,
                    'id': node,
                    'label': node,
                    'shape': 'dot',
                    'size': 10
                })

            for edge in e:
                edges.append({
                    'arrows': 'to',
                    'from': edge[0],
                    'to': edge[1]
                })

            # Return the graph in JSON format.
            # vis.js will handle the rest on the frontend.
            self.wfile.write(
                json.dumps({'nodes': nodes, 'edges': edges}).encode('utf8')
            )

    return S


@cli.command()
@click.argument('fname')
@click.option('-host', default='localhost', help='server hostname')
@click.option('-port', default=8080, help='server port')
@click.option('-origin', default=None, type=str, help='list of origin events')
@click.option('-ix', default=False, is_flag=True, help='ignore exceptions')
def web(fname, host, port, origin=None, ix=False):
    # This starts a simple web server for a specified world.
    # This allows the world to be stepped and visualized in real time
    # from a web browser using the vis.js library.
    # This implementation is obviously very crude. There
    # are lots of problems with this design and code. It needs
    # re-writing. It is not even close to being "production"/"end-user" ready.
    # These were all purposeful decisions. The purpose behind this code is purely
    # for demonstration/testing purposes.
    world = _get_world(fname)
    httpd = HTTPServer(
        (host, port),
        _server_factory(world, [x.strip() for x in origin.split(',')] if origin else None, ix)
    )

    print(f'Starting httpd server on {host}:{port}')
    httpd.serve_forever()


if __name__ == '__main__':
    cli()
