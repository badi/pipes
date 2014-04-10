from collections import deque

class Unit: pass

class State(object):
    def __init__(self):
        self._u = deque()
        self._d = deque()

    def push_down(self, value):
        self._d.appendleft(value)

    def push_up(self, value):
        self._u.appendleft(value)

    def pop_down(self):
        return self._d.pop()

    def pop_up(self):
        return self._u.pop()

    def iter_from_up(self):
        try:
            while True:
                yield self.pop_up()
        except IndexError:
            raise StopIteration

class producer(object):
    def __init__(self, fn):
        self._fn = fn
        self.state = None
        self._stream = None

    def set_stream(self, gen):
        self._stream = gen

    def __call__(self):
        for val in self._fn():
            self.state.push_down(val)
            yield Unit()

    def __str__(self):
        return '<producer %s>' % self._fn.__name__

class pipe(object):
    def __init__(self, fn):
        self._fn = fn
        self.state = None
        self._stream = None

    def set_stream(self, gen):
        self._stream = gen

    def __call__(self):
        for _ in self._stream():
            val = self.state.pop_down()
            for res in self._fn(val):
                self.state.push_down(res)
                yield Unit()

class consumer(object):
    def __init__(self, fn):
        self._fn = fn
        self.state = None
        self._stream = None

    def set_stream(self, gen):
        self._stream = gen

    def __call__(self):
        for _ in self._stream():
            val = self.state.pop_down()
            for result in self._fn(val):
                yield result

    def __str__(self):
        return '<consumer %s>' % self._fn.__name__


class Proxy(object):
    __wrap__ = lambda x: x
    def __init__(self, constructor):
        self._constructor = constructor

    def __call__(self, *args, **kws):
        obj = self._constructor(*args, **kws)
        wrapped = self.__wrap__(obj)
        return wrapped

class Producer(Proxy):
    __wrap__ = producer

class Pipe(Proxy):
    __wrap__ = pipe

class Consumer(Proxy):
    __wrap__ = consumer



def connect(prod, pipes, cons):
    """
    :: producer -> [pipe] -> consumer -> generator
    """
    s = State()
    prev = prod
    prev.state = s
    for curr in pipes:
        curr.state = s
        curr.set_stream(prev)
        prev = curr
    cons.set_stream(prev)
    cons.state = s

    for result in cons():
        if type(result) is Unit: continue
        yield result

def run(*args):
    ":: Producer -> Pipe -> ... -> Consumer"
    for result in connect(*args):
        pass
