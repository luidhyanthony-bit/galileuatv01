import sys
import socket
import ssl

# Verifica se o usuario passou todos os argumentos na tela
if len(sys.argv) != 4:
    print("Uso: python https.py site resource output")
    sys.exit()

host = sys.argv[1]
resource = sys.argv[2]
output = sys.argv[3]

port = 80

# Descobre se o site comeca com https para mudar a porta
if host.lower().startswith("https://"):
    host = host[8:]
    port = 443

# Cria o socket normal de internet
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Se for https, coloca a protecao SSL por cima do socket
if port == 443:
    contexto = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    sock = contexto.wrap_socket(sock, server_hostname=host)

# Conecta no servidor (site)
sock.connect((host, port))

# Monta o texto da requisicao HTTP juntando os pedacos com +
requisicao = (
        "GET " + resource + " HTTP/1.1\r\n"
        "Host: " + host + "\r\n"
        "Connection: close\r\n\r\n"
    )

# Envia para o servidor transformado em bytes
sock.send(requisicao.encode())

# Comeca a receber a resposta e guarda tudo na variavel dados
dados = b""
while b"\r\n\r\n" not in dados:
    bloco = sock.recv(4096)
    dados = dados + bloco

# Separa onde acaba o cabecalho e comeca o corpo (dados reais)
posicao_divisao = dados.find(b"\r\n\r\n")
cabecalho_bytes = dados[:posicao_divisao]
corpo = dados[posicao_divisao + 4:]

# Converte o cabecalho para texto maiusculo e quebra em linhas
linhas_cabecalho = cabecalho_bytes.decode().upper().split("\r\n")

tamanho_conteudo = -1
eh_chunked = False

# Procura as informacoes necessarias dentro do cabecalho linha por linha
for linha in linhas_cabecalho:
    if "CONTENT-LENGTH:" in linha:
        partes = linha.split(":")
        tamanho_conteudo = int(partes[1].strip())
        
    if "TRANSFER-ENCODING: CHUNKED" in linha:
        eh_chunked = True

# --- SE FOR POR TAMANHO FIXO ---
if tamanho_conteudo != -1:
    while len(corpo) < tamanho_conteudo:
        corpo = corpo + sock.recv(4096)
    corpo = corpo[:tamanho_conteudo]

# --- SE FOR POR BLOCOS (CHUNKED) ---
elif eh_chunked:
    resultado_final = b""
    
    while True:
        # Garante que leu a linha que diz o tamanho do bloco
        while b"\r\n" not in corpo:
            corpo = corpo + sock.recv(4096)
            
        pos_quebra = corpo.find(b"\r\n")
        texto_tamanho = corpo[:pos_quebra]
        tamanho_bloco = int(texto_tamanho, 16)
        
        # Se o tamanho do bloco for zero, acabou o arquivo
        if tamanho_bloco == 0:
            break
            
        # Garante que o bloco inteiro ja chegou do servidor
        while len(corpo) < pos_quebra + 4 + tamanho_bloco:
            corpo = corpo + sock.recv(4096)
            
        # Pega so os dados do bloco e junta no resultado
        resultado_final = resultado_final + corpo[pos_quebra + 2 : pos_quebra + 2 + tamanho_bloco]
        
        # Joga fora o bloco que ja leu e avanca o buffer
        corpo = corpo[pos_quebra + 4 + tamanho_bloco:]
        
    corpo = resultado_final

# --- SALVA O ARQUIVO FINAL ---
if tamanho_conteudo != -1 or eh_chunked:
    arquivo = open(output, "wb")
    arquivo.write(corpo)
    arquivo.close()
    print("Salvo com sucesso.")
else:
    print("Erro: Formato nao identificado.")

sock.close()