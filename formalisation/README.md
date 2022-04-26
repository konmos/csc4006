# Framework for Story-thinking in SE

With this Python package we 'formalise' the relationship between story-thinking and computational-thinking (see research article in the `docs` folder for more information on this). For lack of a better word, we refer to it simply as 'formalisation'. This is a Python library which enables us to reason about software more in line with how we would reason about stories. This README is a developer guide for using the library; for examples take a look at the Jupyter notebook provided and the code inside `formalisation/examples`.

# Writing 'story centric' software

Fundamentally, using this framework forces us to think about software in terms of events and actions. This is not too dissimilar to standard event-based programming. To demonstrate its usage, we consider a simple example, which we will develop as we go along (we are assuming this code lives at the top-level directory and that `formalisation` is accessible from the script).

Assume that we are trying to implement the following story in code;

> Paul is resting after a long day's work in an apple orchard. It is peak season; the glistening, juicy apples are calling out to Paul, however he is too tired to pick them himself. Coincidentally, an apple falls from one of the trees and lands right beside Paul. He eats it and this gives him the motivation to pick another one, however, he is not sure if he is hungry anymore after eating the first apple. He's not sure if he should eat another one.

We now consider a possible software implementation of the above story, step by step.

```python
from formalisation.formalisation import World

w = World()


@w.event()
def apple_falls(ctx):
    print('an apple has fallen')


if __name__ == '__main__':
    w.process()
```

In the above snippet, we have modelled a global `World` instance; this is similar to the idea of a global world in a story where events and actions take place. We then describe this world with a global event which simply indicates when an apple has fallen. When we call `w.process()`, the library automatically figures out which global events exist (we call these 'origin' events) and calls them in turn (`apple_falls` in this case).

Now, running this script in the command line, we get the following output:

```
an apple has fallen
```

Let us now add Paul to the world.

```python
from formalisation.formalisation import World, Agent

w = World()


class Paul(Agent):
    @w.event('apple_falls')
    def eat_apple(self, ctx):
        print('an apple has been eaten')


@w.event()
def apple_falls(ctx):
    print('an apple has fallen')


if __name__ == '__main__':
    w.process()
```

Here we have modelled Paul as an agent composed of a single action - eating an apple. Notice the argument to `w.event`, this indicates that the **action** `Paul.eat_apple` is triggered by the **event** `apple_falls`. We can describe this with the following flow (FDL):

```
apple_falls -> {Paul.eat_apple}
```

If we run the above code, however, we will see that nothing has changed. We must add the agent to the world. We can do this with `w.add_agent`.

```python
from formalisation.formalisation import World, Agent

w = World()


class Paul(Agent):
    @w.event('apple_falls')
    def eat_apple(self, ctx):
        print('an apple has been eaten')


@w.event()
def apple_falls(ctx):
    print('an apple has fallen')


if __name__ == '__main__':
    w.add_agent(Paul)
    w.process()
```

Now we get the correct output:

```
an apple has fallen
an apple has been eaten
```

Oftentimes, however, it may be 'thematically accurate' to model the agent construction as a global event:

```python
from formalisation.formalisation import World, Agent

w = World()


class Paul(Agent):
    @w.event('apple_falls')
    def eat_apple(self, ctx):
        print('an apple has been eaten')


@w.event()
def apple_falls(ctx):
    print('an apple has fallen')


@w.event()
def paul_rests(ctx):
    w.add_agent(Paul)


if __name__ == '__main__':
    w.process_with_callback(
        lambda w, r: w.reset_agents(),
        ['paul_rests', 'apple_falls']
    )
```

Notice how we now have two global events (`paul_rests` and `apple_falls`). Due to this, we must explicitly pass a list of the origin events to the `process` call as not doing so would result in non-deterministic behaviour. We also use `process_with_callback` in this example so that we can cleanup the agents once we're done processing. This is useful if you want to run the same code multiple times within the same environment.

So far, we have modelled the first part of the story - an apple falling and paul eating the apple. We still have to map the second half to code, however. This is not as easy as adding another action because Paul may not always eat the apple. For more complex interactions such as this, we must use `EventConfig` as a return value to dynamically override the default flow of actions/events.


```python
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
def apple_falls(ctx):
    print('an apple has fallen')


@w.event()
def paul_rests(ctx):
    w.add_agent(Paul)


if __name__ == '__main__':
    w.process_with_callback(
        lambda w, r: w.reset_agents(),
        ['paul_rests', 'apple_falls']
    )
```

In the above code, we have modelled the rest of the story. There is now roughly a 50% chance that Paul will pick and eat a second apple. We achieve this with the `no_propagate` argument to `EventConfig`. This is a very powerful construct that allows us to achieve complex behaviour on the fly. For a summary of what options `EventConfig` can accept, see the below definition:

```python

# EventConfig allows the user to overwrite behavior of event
# propagation on the fly;
#  targets = list of targets this event should propagate to (agents)
#  no_propagate = boolean indicating whether related events should be triggered
#  event_overwrite = trigger this event instead
#  args = args to pass to *ALL* triggered events
#  kwargs = kwargs to pass to *ALL* triggered events
EventConfig = namedtuple(
    'EventConfig',
    ['targets', 'no_propagate', 'event_overwrite', 'args', 'kwargs'],
    defaults=[None, False, None, [], {}]
)
```

The keen reader may have noticed at this point that the way we approached this problem and implemented the original story may not necessarily be the only way. In fact, there may be many ways to achieve the same functionality. This is, interestingly, in line with how stories themselves can be understood and interpreted in different ways. This is one of the strengths (and weaknesses) of story-thinking.

## Threaded Agents

One of the strengths of this library is the ability to model agents either as instances of a class or as individual threads. This is done by simply using the `ThreadedAgent` class as shown below.

```python
import random
from formalisation.formalisation import World, ThreadedAgent, EventConfig

w = World()


class Paul(ThreadedAgent):
    @w.event('apple_falls')
    def eat_apple(self, ctx):
        print('an apple has been eaten')

        if random.random() > 0.5:
            return EventConfig(no_propagate=True)

    @w.event('Paul.eat_apple')
    def pick_apple(self, ctx):
        print('another apple has been picked and eaten')


@w.event()
def apple_falls(ctx):
    print('an apple has fallen')


@w.event()
def paul_rests(ctx):
    w.add_agent(Paul)

    for agent in w.agents:
        agent.start()


if __name__ == '__main__':
    w.process_with_callback(
        lambda w, r: w.reset_agents(),
        ['paul_rests', 'apple_falls']
    )
```

We had to start the thread manually from within the `paul_rests` event, however, all other overheads and complications are handled automatically by the library.

## Using the runner

In addition to running the script as you would any other Python program, we can use the provided 'runner' for additional functionality.

```
Usage: runner.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  draw-fdl
  run
  step
  web
```

### run

This is the most basic command which simply runs the script, accepting various arguments to modify the runtime behaviour.

*Note: the output files for the fdl and trace options must be .html files.*

```
Usage: runner.py run [OPTIONS] FNAME

Options:
  -origin TEXT  list of origin events
  -ix           ignore exceptions
  -trace TEXT   output file for trace visualization
  -unique       output unique nodes when used with -trace
  -fdl TEXT     output file for FDL visualization
  --help        Show this message and exit.
```

```
$ python runner.py run paul_allens_apples -origin paul_rests,apple_falls

Running with ['paul_rests', 'apple_falls']...

an apple has fallen
an apple has been eaten
another apple has been picked and eaten
```

### draw-fdl

Visualise a textual description of FDL to a HTML file.

```
Usage: runner.py draw-fdl [OPTIONS] FDL

Options:
  --help  Show this message and exit.
```

```
$ python runner.py draw-fdl "foo->{bar}"
```

This will create an output file `fdl.html` and open it in your browser.

### step

Step through the event/action flow in realtime. This starts an interactive shell session where you can execute commands while stepping through the flow of a program.

*Note: Live stepping should only be used for non-threaded applications.*

```
Usage: runner.py step [OPTIONS] FNAME

Options:
  -origin TEXT  list of origin events
  -ix           ignore exceptions
  --help        Show this message and exit.
```

```
$ python runner.py step -origin paul_rests,apple_falls paul_allens_apples

> help
Available Commands:
  exit: Stop stepping and exit the program.
  step [X]: Make X steps (default = 1).
  trace: Return current raw trace.
  fdl: Return the FDL for this world.
  trace_graph [unique]: Draw the current trace.
  fdl_graph: Draw the FDL for this world.
> trace
None
> step
True
> trace
[{'event': 'paul_rests', 'triggered': [], 'id': '00'}]
> step
an apple has fallen
True
> trace
[{'event': 'paul_rests', 'triggered': [], 'id': '00'}, {'event': 'apple_falls', 'triggered': [], 'id': '01'}]
> step
an apple has been eaten
True
> step
another apple has been picked and eaten
True
> step
False
```

### web

Start a web server and open a web-based interface for live stepping. Here, the output graph is updated dynamically and can be modified with comprehensive options.

```
Usage: runner.py web [OPTIONS] FNAME

Options:
  -host TEXT     server hostname
  -port INTEGER  server port
  -origin TEXT   list of origin events
  -ix            ignore exceptions
  --help         Show this message and exit.
```

```
$ python runner.py web paul_allens_apples -origin paul_rests,apple_falls

Starting httpd server on localhost:8080

127.0.0.1 - - [26/Apr/2022 12:40:42] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [26/Apr/2022 12:40:42] "GET /favicon.ico HTTP/1.1" 200 -
127.0.0.1 - - [26/Apr/2022 12:40:47] "POST / HTTP/1.1" 200 -
127.0.0.1 - - [26/Apr/2022 12:40:51] "POST / HTTP/1.1" 200 -
an apple has fallen
127.0.0.1 - - [26/Apr/2022 12:40:55] "POST / HTTP/1.1" 200 -
an apple has been eaten
127.0.0.1 - - [26/Apr/2022 12:41:00] "POST / HTTP/1.1" 200 -
another apple has been picked and eaten
127.0.0.1 - - [26/Apr/2022 12:41:04] "POST / HTTP/1.1" 200 -
```

## Misc.

See the below definitions for some miscellaneous functionality exposed by the `World` instance.

```python
def generate_fdl(self) -> t.List[str]:
    ...

def draw_trace_graph(self, notebook: bool = True, unique_events: bool = False,
                    fname: str = None, show: bool = True):
    ...

def draw_flow_graph(self, notebook: bool = True, fname: str = None):
    ...

def get_origin_events(self) -> t.List[str]:
    ...
```

See the source code for more details.
