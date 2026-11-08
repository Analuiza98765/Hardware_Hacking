
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Pasta onde os arquivos serão salvos
pasta = Path(__file__).parent

# Gera uma chave privada RSA
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Identificação do certificado
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NexaSense"),
    x509.NameAttribute(NameOID.COMMON_NAME, "NexaSense ESP32"),
])

# Cria um certificado autoassinado
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.now(timezone.utc))
    .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
    .add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )
    .sign(private_key, hashes.SHA256())
)

# Salva certificado em DER
(pasta / "server-cert.der").write_bytes(
    cert.public_bytes(serialization.Encoding.DER)
)

# Salva chave privada em DER
(pasta / "server-key.der").write_bytes(
    private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
)

print("Certificado e chave privada gerados!")
print("server-cert.der")
print("server-key.der")


# Converte os arquivos DER em arrays C++ para o ESP32
cert_bytes = (pasta / "server-cert.der").read_bytes()
key_bytes = (pasta / "server-key.der").read_bytes()

def gerar_array(nome, dados):
    valores = ", ".join(f"0x{byte:02x}" for byte in dados)
    return f"unsigned char {nome}[] = {{{valores}}};\n"

conteudo = """#pragma once

"""

conteudo += gerar_array("example_crt_DER", cert_bytes)
conteudo += f"const int example_crt_DER_len = {len(cert_bytes)};\n\n"

conteudo += gerar_array("example_key_DER", key_bytes)
conteudo += f"const int example_key_DER_len = {len(key_bytes)};\n"

(pasta.parent / "src" / "certificates.h").write_text(
    conteudo,
    encoding="utf-8"
)

print("Arquivo src/certificates.h gerado!")
