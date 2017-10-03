# coding=utf8
import socket
import threading
import time
import math

url = 'xkcd.com'
res = []

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
    response = ''
    chunk = sock.recv(4096)
    while chunk:
        response += chunk
        chunk = sock.recv(4096)
    global res
    res.append(response)
    return response

@log_time
def multithread_way():
    for i in range(10):
        t = threading.Thread(target=blocking_way)
        t.start()
    while(len(res) != 10):
        pass

multithread_way()
