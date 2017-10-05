# coding=utf8
import socket
from selectors2 import DefaultSelector, EVENT_READ, EVENT_WRITE
import time

url = 'xkcd.com'

selector = DefaultSelector()
stopped = False
res = []

def log_time(func):
    def wrapper(*args, **kw):
        start_time = time.time()
        func(*args, **kw)
        print(time.time() - start_time)
    return wrapper

class Future(object):
    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result=None):
        self.result = result
        for fn in self._callbacks:
            fn(self)

    def __iter__(self):
        yield self
        return self.result

class Task(object):
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        # f.set_result(None)
        self.step(f)

    def step(self, future):
        try:
            next_future = self.coro.send(future.result)
        except StopIteration:
            return
        next_future.add_done_callback(self.step)

def connect(sock, address):
    f = Future()
    sock.setblocking(False)
    try:
        sock.connect(address)
    except IOError:
        pass

    def on_connected():
        f.set_result(None)

    selector.register(sock.fileno(), EVENT_WRITE, on_connected)
    yield f
    selector.unregister(sock.fileno())

def read(sock):
    f = Future()

    def on_readable():
        f.set_result(sock.recv(4096))

    selector.register(sock.fileno(), EVENT_READ, on_readable)
    chunk = yield f
    selector.unregister(sock.fileno())
    return chunk

def read_all(sock):
    response = []
    chunk = yield from read(sock)
    while chunk:
        response.append(chunk)
        chunk = yield from read(sock)
    return b''.join(response)

# def read_all(sock):
#     response = []
#     def on_readable():
#         f.set_result(sock.recv(4096))
#     chunk = True
#     while chunk:
#         f = Future()
#         selector.register(sock.fileno(), EVENT_READ, on_readable)
#         chunk = yield f
#         selector.unregister(sock.fileno())
#         if chunk:
#             response.append(chunk)
#     return b''.join(response)

class Crawler(object):
    def __init__(self, url, id):
        self.url = url
        self.response = b''
        self.id = id

    def fetch(self):
        sock = socket.socket()
        yield from connect(sock, (self.url, 80))
        request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(self.url)
        sock.send(request.encode('ascii'))
        self.response = yield from read_all(sock)
        global res, stopped
        res.append(self.response)
        if len(res) >= 10:
            stopped = True

@log_time
def loop():
    for i in range(10):
        crawler = Crawler(url, i)
        Task(crawler.fetch())
    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()

loop()
