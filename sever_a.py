# Echo server program
import socket

HOST = "localhost"      # Symbolic name meaning all available interfaces
PORT = 1234             # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

conn, addr = s.accept()
print('Connected by', addr)
while 1:
    print("send all ...")
    conn.sendall(b"a"*1024)
conn.close()
