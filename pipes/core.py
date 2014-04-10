from collections import deque

class Unit: pass

class Proxy(object):
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
        self.proxy = None
        self._stream = None

    def set_stream(self, gen):
        self._stream = gen

    def __call__(self):
        for val in self._fn():
            self.proxy.push_down(val)
            yield Unit()

    def __str__(self):
        return '<producer %s>' % self._fn.__name__

class pipe(object):
    def __init__(self, fn):
        self._fn = fn
        self.proxy = None
        self._stream = None

    def set_stream(self, gen):
        self._stream = gen

    def __call__(self):
        for _ in self._stream():
            val = self.proxy.pop_down()
            for res in self._fn(val):
                self.proxy.push_down(res)
                yield Unit()

class consumer(object):
    def __init__(self, fn):
        self._fn = fn
        self.proxy = None
        self._stream = None

    def set_stream(self, gen):
        self._stream = gen

    def __call__(self):
        for _ in self._stream():
            val = self.proxy.pop_down()
            for result in self._fn(val):
                yield result

    def __str__(self):
        return '<consumer %s>' % self._fn.__name__
        

@producer
def stdinLn():
    ":: Producer String"
    import sys
    while True:
        line = sys.stdin.readline()
        if line:
            print line.strip()
        else:
            break

@producer
def range10():
    for i in xrange(10):
        print 'range10', i
        yield i

@pipe
def duplicate(x):
    print 'duplicate', x
    yield x
    yield x

@consumer
def putStrLn(x):
    ":: Consumer ()"
    print 'putStrLn', x
    yield Unit()

def connect(prod, pipes, cons):
    p = Proxy()
    prev = prod
    prev.proxy = p
    for curr in pipes:
        curr.proxy = p
        curr.set_stream(prev)
        prev = curr
    cons.set_stream(prev)
    cons.proxy = p

    for result in cons():
        if type(result) is Unit: continue
        yield result

def run(*args):
    ":: Producer -> Pipe -> ... -> Consumer"
    for result in connect(*args):
        pass


def test():
    run(range10,
        [duplicate],
        putStrLn)


if __name__ == '__main__':
    test()























