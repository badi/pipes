import core

@core.producer
def stdinLn():
    ":: Producer String"
    import sys
    while True:
        line = sys.stdin.readline()
        if line:
            print line.strip()
        else:
            break

@core.Producer
class Range(object):
    def __init__(self, *args, **kws):
        self._args = args
        self._kws = kws

    def __call__(self):
        return xrange(*self._args, **self._kws)

@core.producer
def prange():
    for i in xrange(1000):
        yield i

@core.pipe
def duplicate(x):
    yield x
    yield x

@core.consumer
def putStrLn(x):
    ":: Consumer ()"
    print x
    yield core.Unit()

COUNT = 0
@core.consumer
def count(x):
    global COUNT
    COUNT += 1
    yield core.Unit()

@core.Consumer
class Count(object):
    def __init__(self):
        self.count = 0

    def __call__(self, x):
        self.count += 1
        yield core.Unit()

def test():
    cnt = Count()
    core.run(prange,
            [duplicate],
            cnt)
    print cnt._fn.count

def test1():
    core.run(Range(10),
            [duplicate],
            putStrLn)

if __name__ == '__main__':
    test()
