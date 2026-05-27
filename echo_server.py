import socket

SERVER_IP = "10.25.1.162"
SERVER_PORT = 5000

my_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Escutando em ({SERVER_IP}:{SERVER_PORT})")
my_sock.bind((SERVER_IP, SERVER_PORT))

while True:
    msg, source = my_sock.recvfrom(512)
    print(f"Recebi/devolvendo a {source}: {msg}")
    my_sock.sendto(msg, source)

my_sock.close()