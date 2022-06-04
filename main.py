
from operator import le
import socket
import queue
from threading import Thread, Lock

from typing import List


b_client_id = 0
b_clients = {}

client_lock = Lock()


def open_read_only_socket(remote_addresss, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((remote_addresss, port))
    return s


def open_write_only_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", port))
    s.listen(10)
    return s


def fan_out_thread(idx, socket):
    while True:
        try:
            print(idx, b_clients)
            q = b_clients[idx]
            message = q.get()
            socket.sendall(message)
        except InterruptedError:
            del b_clients[idx]


def run_server(socket: socket.socket):
    global b_client_id, b_clients
    print("running server on a seperate thread")
    while True:
        clientsocket, address = socket.accept()
        print("connected by", address)

        with client_lock:
            b_clients[b_client_id] = queue.Queue()

            client_thread = Thread(target=fan_out_thread,
                                   args=(b_client_id, clientsocket))
            client_thread.start()
            b_client_id += 1


def read_1k_from_socket(socket):
    chunks = []
    bytes_recd = 0
    while bytes_recd < 1024:

        chunk = socket.recv(min(1024 - bytes_recd, 1024))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    message = b"".join(chunks)
    return message


def server(a_address: str, a_port: int, b_port: int):
    try:
        a_socket = open_read_only_socket(a_address, a_port)
        server_socket = open_write_only_socket(b_port)

        server_thread = Thread(target=run_server, args=(server_socket,))

        server_thread.start()
        print("started server")

        while True:
            message = read_1k_from_socket(a_socket)
            # print("mesage:", len(message))
            for i in b_clients.keys():
                client = b_clients[i]
                client.put(message)
    except TimeoutError:
        raise
    except InterruptedError:
        raise
    except Exception as e:
        print("something horrible went wrong", e)


server("localhost", 1234, 1235)
