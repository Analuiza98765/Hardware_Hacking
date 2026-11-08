
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.request
import json


class ServidorHTTP(BaseHTTPRequestHandler):

    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        dados = self.rfile.read(tamanho)

        print("\n--- REQUISICAO RECEBIDA ---")
        print("Metodo:", self.command)
        print("Caminho:", self.path)
        print("Dados recebidos:", dados.decode("utf-8"))

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Recebido com sucesso")

    def log_message(self, format, *args):
        pass


servidor = HTTPServer(("127.0.0.1", 8000), ServidorHTTP)

thread = threading.Thread(target=servidor.serve_forever)
thread.daemon = True
thread.start()

print("Servidor HTTP iniciado em http://127.0.0.1:8000")

dados = {
    "dispositivo": "NexaSense",
    "temperatura": 25.5,
    "umidade": 60.0
}

requisicao = urllib.request.Request(
    "http://127.0.0.1:8000/api/sensor",
    data=json.dumps(dados).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(requisicao) as resposta:
    print("\nResposta:", resposta.status)
    print(resposta.read().decode("utf-8"))

servidor.shutdown()
