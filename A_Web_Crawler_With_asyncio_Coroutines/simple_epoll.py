# coding=utf8
import socket
from selectors2 import DefaultSelector, EVENT_READ, EVENT_WRITE
import time
import math

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

class Crawler(object):
    def __init__(self, url):
        self.url = url
        self.sock = None
        self.response = ''

    def fetch(self):
        self.sock = socket.socket()
        self.sock.setblocking(False)
        try:
            self.sock.connect((self.url, 80))
        except:
            pass
        selector.register(self.sock.fileno(), EVENT_WRITE, self.connected)

    def connected(self, key, mask):
        selector.unregister(key.fd)
        request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(self.url)
        self.sock.send(request.encode('ascii'))
        selector.register(key.fd, EVENT_READ, self.read_response)

    def read_response(self, key, mask):
        response = ''
        chunk = self.sock.recv(4096)
        if chunk:
            self.response += chunk
        else:
            selector.unregister(key.fd)
            global res, stopped
            res.append(self.response)
            if len(res) >= 10:
                stopped = True


@log_time
def loop():
    for i in range(10):
        crawler = Crawler(url)
        crawler.fetch()
    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)

loop()
