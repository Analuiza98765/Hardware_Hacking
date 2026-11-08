# Análise de protocolos e comunicações

## Escopo

Análise estática do firmware/configuração e revisão das evidências de simulação existentes. A rede `Wokwi-GUEST` e o encaminhamento local descrito em `wokwi.toml` pertencem ao ambiente educacional. Não houve captura de pacotes do ESP32, teste em rede de produção ou interceptação de tráfego.

## Protocolos observados

| Trecho | Protocolo/configuração | Evidência | Avaliação |
|---|---|---|---|
| Sensor → ESP32 | Sinal digital DHT22 no GPIO 15 | `diagram.json` e `DHT_PIN` em `src/main.cpp` | Comunicação local; sem teste elétrico físico |
| ESP32 → rede | Wi-Fi, SSID virtual `Wokwi-GUEST`, canal 6 | `WiFi.begin` em `src/main.cpp` | Rede aberta prevista pelo simulador; não representa configuração de produção |
| Dispositivo → rede de laboratório | Wi-Fi virtual via gateway Wokwi | Configuração Wokwi e associação confirmada no monitor serial | Meio de laboratório; não há captura do tráfego de rádio |
| Cliente local → API atual | HTTPS/TLS, TCP encaminhado `localhost:8443` → `target:443`, GET | `HTTPSServer` e rotas em `src/main.cpp`; regra em `wokwi.toml` | O cliente local alcança o servidor HTTPS simulado; certificado autoassinado exige confiança explícita |
| Cliente → API original | HTTP, TCP/80, GET | Fonte preservado em `firmware/original/nexasense-original.ino` | A versão original não criptografava nem autenticava a rota do sensor |
| Monitor → ESP32 | UART0, 115200 baud | `Serial.begin` e configuração do diagrama Wokwi | Logs revelam estado de inicialização; acesso físico não foi testado |

O fluxo do protótipo é `DHT22 → ESP32 (firmware e Flash) → Wi-Fi/rede de laboratório Wokwi → encaminhamento local → cliente HTTPS`. O dispositivo disponibiliza um servidor; o cliente local inicia as requisições. MQTT não é utilizado nem está presente na configuração examinada.

A versão atual exige `X-API-Key` para `/api/sensor`; a chave de desenvolvimento é fornecida localmente por `src/secrets.h`, que não deve ser distribuído. Essa alteração não transforma uma chave compartilhada embutida no firmware em identidade segura de produção: quem puder extrair ou analisar a imagem poderá recuperar o segredo. A rota `/` informa apenas o estado geral do serviço.

## Teste de integração no Wokwi pelo VS Code

O firmware foi executado na extensão Wokwi para VS Code após o build com PlatformIO. A simulação conectou-se à rede virtual e iniciou o HTTPS na porta 443. Usando o encaminhamento `localhost:8443` → `target:443`, o script `network/test_api_https.py` testou a API em loopback:

| Cenário | Resultado observado |
|---|---|
| `/api/sensor` sem `X-API-Key` | HTTP 401 |
| `/api/sensor` com chave incorreta | HTTP 401 |
| `/api/sensor` com chave local correta | HTTP 200; JSON com dispositivo, temperatura e umidade |
| `/` | HTTP 200 |
| `/missing` | HTTP 404 |

O cliente de teste restringe a negociação a TLS 1.2. Na conexão local, desabilita a validação convencional da cadeia de confiança e do hostname, mas compara os bytes DER do certificado recebido com o arquivo local esperado e rejeita divergências. Trata-se de pinning exato do certificado para este laboratório, não de validação de uma cadeia comercial. A versão TLS foi fixada porque o handshake padrão do cliente não interoperou com a implementação TLS do servidor na simulação; com TLS 1.2, os cenários acima foram aprovados. Evidências: saída serial do Wokwi em `network/evidence/F-01-wokwi-https.png` e resultado do cliente em `network/evidence/F-01-wokwi-https-test.txt`.

### Teste controlado de falha do DHT22

As conexões do DHT22 foram removidas temporariamente de `diagram.json`, e a simulação foi parada e iniciada para carregar o diagrama alterado. Com o sensor desconectado, as requisições sem chave e com chave incorreta continuaram retornando HTTP 401; a rota autenticada retornou HTTP 500 com `{"erro":"Falha na leitura do sensor"}`. As rotas `/` e `/missing` mantiveram HTTP 200 e 404. Resultado salvo em `network/evidence/F-06-dht-desconectado-test.txt`; a captura serial complementar está em `network/evidence/F-06-dht-desconectado-vscode.png`.

Esse ensaio demonstra tratamento previsível da falha de leitura e não caracteriza vulnerabilidade. As três conexões originais foram restauradas em `diagram.json` após o teste. Para reproduzir, desconecte o DHT22, pare e inicie a simulação e execute `python network/test_api_https.py --expect-sensor-error`; em seguida, restaure os fios, reinicie e rode o teste sem a opção.

## Teste do timeout de Wi-Fi

Para validar F-04 no Wokwi, o SSID foi trocado temporariamente para `REDE_INEXISTENTE`, o firmware foi recompilado pelo PlatformIO e a simulação foi iniciada novamente no VS Code. O monitor serial exibiu a tentativa e, após o limite configurado, `Falha ao conectar ao Wi-Fi!` e `Tempo limite de conexao atingido.`. A evidência da execução está em `network/evidence/F-04-wifi-timeout-vscode.png`.

Depois do teste, o fonte foi restaurado para `Wokwi-GUEST`, recompilado e executado novamente. A conexão normal e os testes integrados da API foram aprovados. O ensaio verifica o caminho de falha na **simulação**, não a cobertura de rede ou o comportamento de uma placa física.

## Demonstração HTTP local

`network/teste_http.py` inicia um servidor somente em `127.0.0.1:8000`, envia JSON de exemplo e exibe a resposta HTTP 200 e o corpo legível no servidor. A execução foi repetida com sucesso durante esta tarefa.

Essa demonstração ilustra a ausência de confidencialidade no HTTP, mas **não** é captura do tráfego do NexaSense. A imagem `network/evidence/http-python-demo.png` é evidência do experimento local independente. As imagens `F-01-autenticacao.png` e `F-04-*.png` documentam os cenários de simulação descritos nos achados.

## Reprodução autorizada

1. Abra o projeto no Wokwi e inicie a simulação com a configuração `Wokwi-GUEST`.
2. Observe no monitor serial a conexão, o endereço IP e a inicialização do servidor.
3. Use apenas o encaminhamento local configurado em `wokwi.toml` (`localhost:8443` → `target:443`), se suportado pelo ambiente.
4. Execute `python network/test_api_https.py`. O script lê o segredo local ignorado, testa os cenários da tabela via TLS 1.2 e não imprime o valor da chave. Em loopback, compara o certificado recebido com o certificado DER local esperado; essa configuração de pinning é exclusiva do laboratório.
5. Para demonstrar apenas HTTP em loopback, execute `python network/teste_http.py`.

O gateway público do Wokwi não foi usado para expor a API à Internet. Não foram realizados testes contra serviços ou redes de terceiros.

## Recomendações

- Em produção, usar credenciais individuais, provisionadas com segurança, e rotação/revogação; não distribuir a mesma API Key em todos os dispositivos.
- Usar certificados e chaves distintos por dispositivo, com cadeia de confiança validada pelo cliente e ciclo de renovação.
- Armazenar material criptográfico com proteção adequada ao hardware; não publicar arquivos de chave nem arrays derivados.
- Reduzir logs de produção e proteger/desabilitar interfaces de debug conforme o modelo de ameaça.
