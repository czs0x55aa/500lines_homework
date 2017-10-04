# coding=utf8
import socket
import time
import math

url = 'xkcd.com'

def log_time(func):
    def wrapper(*args, **kw):
        start_time = time.time()
        func(*args, **kw)
        print(time.time() - start_time)
    return wrapper

def blocking_way():
    sock = socket.socket()

    sock.connect((url, 80))
    request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(url)
    sock.send(request.encode('ascii'))
    response = b''
    chunk = sock.recv(4096)
    while chunk:
        response += chunk
        chunk = sock.recv(4096)
    return response

@log_time
def syn_way():
    res = []
    for i in range(10):
        res.append(blocking_way())

syn_way()
