# Registro de achados de segurança — NexaSense

## Escopo e método

Achados derivados de análise estática dos fontes/configurações e de evidências da simulação Wokwi e do experimento HTTP em loopback. Não houve teste em hardware físico, captura de tráfego do ESP32, acesso a redes de produção ou exploração de sistemas externos. As severidades são preliminares e condicionadas ao cenário de implantação.

## Resumo

| ID | Condição observada | Impacto | Probabilidade no cenário avaliado | Risco | Estado atual |
|---|---|---|---|---|---|
| F-01 | API original sem autenticação | Acesso não autorizado a dados ambientais | Média em rede alcançável | Médio | Corrigido no firmware de laboratório; risco residual de segredo embutido |
| F-02 | API original por HTTP sem TLS | Exposição/leitura ou alteração do tráfego | Média se houver interceptação na rede | Médio | TLS adicionado; confiança e gestão de chave ainda inadequadas para produção |
| F-03 | Wi-Fi `Wokwi-GUEST` aberto | Exposição contextual da conexão | Não aplicável ao ambiente simulado | Não classificado | Configuração exclusiva do simulador |
| F-04 | Firmware original aguardava Wi-Fi indefinidamente | Indisponibilidade da API se a rede falhasse | Alta quando a rede estivesse indisponível | Médio | Timeout de 10 s implementado; reconexão ainda ausente |
| F-05 | Segredos de teste precisam ser distribuídos no dispositivo | Extração/reuso de chave de API ou chave TLS | Média com acesso à imagem ou ao dispositivo | Médio | Configuração fonte separada e ignorada; segredo ainda integra o binário em execução |

## F-01 — API original sem autenticação

**Categoria:** Controle de acesso  
**Severidade preliminar:** Média  
**Evidência:** `firmware/original/nexasense-original.ino` registra `/api/sensor` sem validar credenciais. As capturas de autenticação documentam respostas 401 sem chave e com chave incorreta e 200 com a chave de teste correta.

**Impacto:** Um cliente que alcance o endpoint original pode obter temperatura e umidade sem autorização.

**Correção na versão atual:** `src/main.cpp` exige o cabeçalho `X-API-Key` antes de ler o sensor. Teste de integração pelo encaminhamento HTTPS local do Wokwi confirmou 401 sem chave, 401 com chave incorreta e 200 com a chave local correta e JSON válido. As evidências estão em `network/evidence/F-01-wokwi-https.png` e `network/evidence/F-01-wokwi-https-test.txt`; a captura histórica de cliente está em `network/evidence/F-01-autenticacao.png`.

**Risco residual:** A chave é necessária ao firmware para comparar o pedido e, portanto, fica recuperável por análise do binário. A configuração local evita publicar o valor no fonte, mas não cria uma identidade resistente à extração. Não usar chave compartilhada em produção.

## F-02 — HTTP sem TLS no firmware original

**Categoria:** Confidencialidade e integridade do transporte  
**Severidade preliminar:** Média  
**Evidência:** O fonte original inicia `WebServer` na porta 80. `network/teste_http.py` demonstra, em loopback independente, um JSON legível enviado por HTTP; a imagem correspondente não é captura do ESP32.

**Impacto:** Um observador na mesma rede poderia ler ou alterar dados em trânsito.

**Correção na versão atual:** Servidor HTTPS na porta 443 com certificado de laboratório. A simulação e o encaminhamento local estão descritos em `wokwi.toml`.

**Risco residual:** O certificado é autoassinado, não representa uma cadeia de confiança comercial, e sua chave de teste é provisionada no firmware. Os testes locais precisaram fixar TLS 1.2; a negociação padrão do cliente não interoperou com o handshake do servidor no simulador. No teste de loopback, a validação convencional de cadeia de confiança e hostname fica desabilitada; em seguida, o script compara o certificado DER recebido com o certificado local esperado, aceitando somente essa cópia exata como pinning de laboratório. Isso não equivale à validação de uma cadeia comercial nem deve ser usado como configuração de produção. Não foi feita captura de pacotes nem teste em placa física.

## F-03 — Rede Wi-Fi aberta no simulador

**Categoria:** Configuração de rede  
**Severidade:** Não classificada como vulnerabilidade no protótipo  
**Evidência:** `ssid` igual a `Wokwi-GUEST`, senha vazia e canal 6 em `src/main.cpp`.

Essa configuração é prevista pelo Wokwi e não demonstra exposição de uma rede real. Para produção, usar WPA2/WPA3 e provisionar credenciais sem armazená-las em código-fonte, logs ou repositório.

## F-04 — Timeout Wi-Fi ausente no firmware original

**Categoria:** Disponibilidade e resiliência  
**Severidade preliminar:** Média  
**Evidência:** O fonte original espera `WL_CONNECTED` sem limite. `network/evidence/F-04-wifi-timeout.png` registra o cenário simulado de rede inexistente.

**Impacto:** O servidor não é inicializado enquanto o firmware permanece no laço de conexão.

**Correção na versão atual:** Limite de 10 segundos. Recompilei temporariamente com SSID inexistente, iniciei o firmware na extensão Wokwi do VS Code e observei `Falha ao conectar ao Wi-Fi!` e `Tempo limite de conexao atingido.` após a espera limitada. A captura está em `network/evidence/F-04-wifi-timeout-vscode.png`. Em seguida, restaurei `Wokwi-GUEST`, recompilei e confirmei a conexão e os testes HTTPS 401/401/200. A configuração final do fonte continua usando somente `Wokwi-GUEST`.

**Risco residual:** Após falha de conexão, o `setup()` retorna e o firmware permanece sem API; não há reconexão automática/backoff. A mitigação melhora o comportamento de inicialização, mas não implementa recuperação de serviço.

## F-05 — Segredos de teste incorporados à imagem

**Categoria:** Gestão de credenciais e chaves  
**Severidade preliminar:** Média  
**Evidência:** A autenticação usa uma chave compilada, e o servidor TLS precisa da chave privada para operar. Os arquivos locais de configuração e certificados são ignorados pelo Git, mas o firmware compilado contém o material necessário ao seu funcionamento. A chave antiga que aparecia na captura histórica foi redigida e rotacionada antes da distribuição do pacote.

**Impacto:** Quem obtiver o binário ou acesso físico poderá recuperar ou reutilizar credenciais de laboratório; a reutilização em produto ampliaria o impacto.

**Mitigação:** Não distribuir arquivos locais de segredo, capturas não redigidas nem binários de teste. Em produção, provisionar identidades e chaves únicas por dispositivo, com armazenamento protegido, rotação e revogação. Não reutilizar as chaves geradas pelo script de laboratório.

## Demonstração prática e limites

- Autenticação: o teste integrado Wokwi confirma HTTPS e cenários HTTP 401/200; a captura histórica de cliente está sanitizada.
- HTTP: demonstração local em `127.0.0.1:8000`, sem ligação ao ESP32; prova somente o comportamento genérico de HTTP sem TLS.
- Wi-Fi: evidência de timeout e recuperação da configuração normal no Wokwi; a conexão normal e a API autenticada foram revalidadas depois do teste.
- Interfaces físicas: mapeadas por configuração e documentação; não testadas em placa.

Não foi realizada interceptação de tráfego, extração de firmware, tentativa de acesso físico privilegiado, análise de OTA ou teste contra terceiros.

## Caso real relacionado

O NVD documenta **CVE-2019-15894**, uma falha em versões antigas do ESP-IDF em que injeção física de falha podia contornar a verificação de Secure Boot no ESP32. O NVD descreve a combinação com Flash Encryption como mitigação complementar. O caso não prova que este protótipo seja afetado: o ambiente compilado usa uma linha atual do Arduino-ESP32/ESP-IDF e não houve teste físico. Ele fundamenta a recomendação de defesa em camadas e proteção do acesso físico.

Fonte: [NVD CVE-2019-15894](https://nvd.nist.gov/vuln/detail/CVE-2019-15894).

## Referências reconhecidas

- [OWASP IoT Security Testing Guide](https://owasp.org/www-project-iot-security-testing-guide/)
- [NISTIR 8259A — IoT Device Cybersecurity Capability Core Baseline](https://csrc.nist.gov/pubs/ir/8259/a/final)
- [ETSI EN 303 645 V3.1.3](https://www.etsi.org/deliver/etsi_en/303600_303699/303645/03.01.03_60/en_303645v030103p.pdf)
- [MITRE EMB3D](https://emb3d.mitre.org/)
- [Espressif ESP-IDF Security Overview](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/security.html)
