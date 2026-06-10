import socket

host = "viacep.com.br"
porta = 80
request = f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n"

falar(f"Conectando em {host}...")
try:
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((host, porta))
    
    falar("send HTTP...")
    cliente.sendall(request.encode('utf-8'))
    
    resposta = b""
    while True:
        dados = cliente.recv(4096)
        if not dados: break
        resposta += dados
    print(resposta)
    cliente.close()

