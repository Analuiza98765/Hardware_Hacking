# Análise do firmware

## Escopo e método

Análise estática dos arquivos fornecidos no projeto, da configuração do PlatformIO e do binário compilado localmente. Não foi recebida uma imagem original de firmware extraída de hardware; portanto, o arquivo preservado é o fonte educacional original, não um dump de flash.

## Preservação e identificação

- Fonte original: `firmware/original/nexasense-original.ino`
- Cópia de trabalho atual: `src/main.cpp`
- SHA-256 e tamanhos: `firmware/hashes.txt`
- Data da análise: 2026-11-02
- Ambiente de compilação: PlatformIO, ESP32 Dev Module (`esp32dev`), Arduino-ESP32 3.3.12, ESP-IDF 5.x subjacente.

O arquivo original foi mantido sem alteração. O hash identifica exatamente esse arquivo fonte; não deve ser interpretado como hash de uma imagem binária original do dispositivo.

## Estrutura e conteúdo relevante

O firmware atual é um programa Arduino C++ compilado a partir de `src/main.cpp`. Ele inicializa o DHT22 no GPIO 15, conecta à rede virtual `Wokwi-GUEST`, aguarda no máximo 10 segundos e inicia o servidor HTTPS na porta 443.

| Item | Observação | Relevância |
|---|---|---|
| `/` | GET de diagnóstico, sem dados do sensor | Superfície de informação de baixo impacto |
| `/api/sensor` | GET, exige `X-API-Key` antes de ler o sensor | Controle de acesso implementado no protótipo |
| Resposta | Identificador do dispositivo, temperatura e umidade em JSON | Dados ambientais; classificação depende do contexto de implantação |
| TLS | Certificado autoassinado de laboratório | Criptografa a sessão, mas exige confiança/pinning no cliente |
| Configuração secreta | `src/secrets.h` e `src/certificates.h` são arquivos locais gerados e ignorados pelo Git | Não publicar nem reutilizar credenciais ou chaves de teste |
| Depuração | Mensagens de inicialização, IP local e eventos no Serial | Pode revelar estado operacional a quem tem acesso à UART/monitor |
| Atualização | Não foi identificado mecanismo OTA no código analisado | Processo de atualização comercial precisa ser definido e autenticado |

O código original arquivado não contém a autenticação e o timeout presentes na versão de trabalho; também servia os dados por HTTP na porta 80. Consulte `findings/findings.md` para distinguir condição original, correção implementada e risco residual.

## Resultado de compilação

`platformio run` concluiu com sucesso. A imagem compilada ocupou 99,4% do limite de aplicação indicado pelo ambiente PlatformIO (1.302.937 de 1.310.720 bytes) e 16,5% da RAM reportada (53.996 de 327.680 bytes). A margem pequena de flash deve ser acompanhada ao adicionar funcionalidades.

Na extensão Wokwi para VS Code, foram observadas a inicialização normal do servidor HTTPS e as respostas de API esperadas. Com SSID temporariamente inexistente, o monitor serial confirmou o timeout de 10 segundos; depois, o SSID de simulação original foi restaurado, o firmware foi recompilado e a conexão/API autenticada foram revalidadas. Consulte as capturas e o script de integração em `network/evidence/` e `network/test_api_https.py`.

## Limitações

- Não houve dump de flash nem análise de partições de um ESP32 físico.
- O hash do fonte não comprova a integridade de uma imagem recebida de um equipamento.
- A análise de strings e configuração foi feita nos fontes acessíveis; não houve engenharia reversa avançada.
- O build confirma compilação, não valida por si só o comportamento de rede, TLS, autenticação ou o sensor em hardware.
