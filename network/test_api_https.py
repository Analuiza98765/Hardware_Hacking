"""Exercise the NexaSense HTTPS API through the local Wokwi port forward."""

import argparse
import http.client
import json
import re
import ssl
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_PORT = 8443
SECRETS_FILE = ROOT / "src" / "secrets.h"
CERTIFICATE_FILE = ROOT / "certificates" / "server-cert.der"


def load_api_key():
    if not SECRETS_FILE.is_file():
        raise FileNotFoundError(
            "Create src/secrets.h from src/secrets.example.h before testing."
        )

    match = re.search(
        r'^\s*#define\s+NEXASENSE_API_KEY\s+"([^"\r\n]+)"',
        SECRETS_FILE.read_text(encoding="ascii"),
        re.MULTILINE,
    )
    if not match or match.group(1).startswith("REPLACE_"):
        raise ValueError("Configure a non-placeholder local API key in src/secrets.h.")
    return match.group(1)


def create_tls_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    return context


def request(path, api_key, context, expected_certificate):
    headers = {}
    if api_key is not None:
        headers["X-API-Key"] = api_key

    connection = http.client.HTTPSConnection(
        "localhost",
        LOCAL_PORT,
        context=context,
        timeout=10,
    )
    try:
        connection.request("GET", path, headers=headers)
        sock = connection.sock
        if sock is None:
            raise ConnectionError("HTTPS connection closed before TLS verification.")
        peer_certificate = sock.getpeercert(binary_form=True)
        if peer_certificate != expected_certificate:
            raise ssl.SSLError(
                "The simulator certificate does not match the local test certificate."
            )
        tls_version = sock.version()
        response = connection.getresponse()
        body = response.read().decode("utf-8", "replace")
        return response.status, body, tls_version
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expect-sensor-error",
        action="store_true",
        help="Expect HTTP 500 because the DHT22 is intentionally disconnected.",
    )
    args = parser.parse_args()
    api_key = load_api_key()
    context = create_tls_context()
    expected_certificate = CERTIFICATE_FILE.read_bytes()
    sensor_status = 500 if args.expect_sensor_error else 200
    cases = [
        ("Sem chave", "/api/sensor", None, 401),
        ("Chave incorreta", "/api/sensor", "invalid-local-test-key", 401),
        (
            "Chave correta / sensor desconectado"
            if args.expect_sensor_error
            else "Chave correta",
            "/api/sensor",
            api_key,
            sensor_status,
        ),
        ("Rota raiz", "/", None, 200),
        ("Rota inexistente", "/missing", None, 404),
    ]

    failed = False
    tls_version = None
    for label, path, key, expected_status in cases:
        status, body, tls_version = request(
            path, key, context, expected_certificate
        )
        passed = status == expected_status
        print(
            f"{label}: HTTP {status} (esperado {expected_status}) - "
            f"{'PASSOU' if passed else 'FALHOU'}"
        )
        failed |= not passed

        if path == "/api/sensor" and key == api_key and passed:
            data = json.loads(body)
            if args.expect_sensor_error:
                if data != {"erro": "Falha na leitura do sensor"}:
                    raise ValueError(
                        "A falha do sensor não produziu o JSON de erro esperado."
                    )
                print("  JSON de erro validado: Falha na leitura do sensor")
            elif (
                set(data) != {"dispositivo", "temperatura", "umidade"}
                or data["dispositivo"] != "NexaSense"
                or not isinstance(data["temperatura"], (int, float))
                or not isinstance(data["umidade"], (int, float))
            ):
                raise ValueError("Resposta autenticada contém JSON inesperado.")
            else:
                print("  JSON valido: dispositivo, temperatura, umidade")

    if tls_version is None:
        raise ssl.SSLError("No TLS session was available for verification.")
    print(
        f"TLS {tls_version}; certificado DER comparado com a copia local esperada; "
        "pinning exato usado somente neste teste local."
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
