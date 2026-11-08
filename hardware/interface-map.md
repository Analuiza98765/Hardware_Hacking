# Inventário dos componentes da ESP32-DevKitC V4

## Componentes identificados

| Componente | Função |
|---|---|
| LED 5V | Indica alimentação da placa |
| Conectores GPIO | Permitem conectar sensores e periféricos |
| Módulo ESP32 | Processamento e comunicação sem fio |
| Conversor USB-UART | Comunicação serial com o computador |
| Botão BOOT | Ativa o modo de gravação de firmware |
| Porta Micro-USB | Alimentação e comunicação |
| Botão EN | Reinicialização da placa |
| Antena Wi-Fi | Comunicação sem fio |

## Componentes utilizados pelo NexaSense

- ESP32: unidade principal de processamento.
- GPIO15: comunicação com o sensor DHT22.
- Wi-Fi: conexão à rede `Wokwi-GUEST`.
- UART0: comunicação serial com o monitor do Wokwi.
- DHT22: sensor de temperatura e umidade.

## Observações

Este inventário foi elaborado com base no modelo de placa selecionado no Wokwi e na documentação oficial da Espressif. Não houve inspeção de hardware físico.

A variante exata do módulo ESP32 ainda não foi identificada.

## Mapeamento das interfaces utilizadas

### GPIO
- GPIO15: conectado ao pino de dados do sensor DHT22.
- Função: receber os dados de temperatura e umidade.

### Wi-Fi
- SSID: Wokwi-GUEST.
- Senha: vazia.
- Canal configurado: 6.
- Utilização: conexão do ESP32 à rede sem fio.

### HTTP
- Porta: 80.
- Protocolo: HTTP, sem criptografia TLS.
- Método utilizado: GET.
- Rota `/`: retorna uma mensagem de funcionamento.
- Rota `/api/sensor`: disponibiliza temperatura e umidade em JSON.
- Autenticação: não implementada no código analisado.

### UART
- Interface: UART0.
- Velocidade: 115200 baud.
- Utilização: comunicação com o monitor serial do Wokwi.

### Observação
As informações acima foram obtidas pela análise do firmware e da configuração do projeto. Não representam resultados de testes de comunicação realizados em hardware físico.

## Uso, exposição e risco das interfaces

| Interface | O que pode permitir | Condição observada | Avaliação para produção |
|---|---|---|---|
| UART0 / USB-UART | Logs, console de diagnóstico e, conforme configuração/boot, comunicação de download | TX/RX aparecem ligados ao monitor serial do Wokwi a 115200 baud | Restringir acesso físico, reduzir logs e controlar modo de download; não há teste de console físico |
| JTAG | Depuração privilegiada e possível acesso a registradores/memória, dependendo de configuração | GPIOs 12–15 têm funções alternativas documentadas; não foi conectado/testado no Wokwi | Desabilitar ou proteger após validar serviço/recuperação de produção |
| GPIO15 | Sinal de dados DHT22; também função alternativa MTDO/strapping | Conectado ao DHT22 no diagrama Wokwi | Revisar multiplexação e comportamento de boot no projeto elétrico real |
| SPI / I²C | Comunicação com memória ou periféricos externos, conforme implementação | Interfaces disponíveis no MCU; não aparecem em uso pelo firmware atual | Reduzir interfaces e periféricos expostos ao necessário |
| USB, BOOT e EN | Alimentação, serial, gravação e reinicialização na placa de desenvolvimento | Componentes do modelo DevKitC documentados, não inspecionados fisicamente | Controlar acesso físico e política de manutenção no gabinete/produto final |

Uma interface disponível não foi classificada isoladamente como vulnerabilidade. A avaliação de impacto pressupõe acesso físico e depende de configurações de boot, eFuses, gabinete e processo de fabricação, não observados no simulador.

## Limitações do ambiente de simulação

O projeto utiliza o Wokwi gratuito, portanto existem limitações em relação à reprodução de um dispositivo físico.

1. Não há placa ESP32 física disponível para inspeção.
2. Não é possível realizar medições elétricas reais nos pinos GPIO.
3. Não é possível verificar fisicamente os componentes internos do módulo.
4. O ambiente simula o funcionamento do ESP32 e de seus periféricos, mas não representa todas as condições de um dispositivo físico.
5. O gateway público do Wokwi permite conexões de saída para a internet, mas não permite conexões de entrada para acessar diretamente o servidor HTTP simulado.
6. Não foram realizados testes físicos de hardware ou medições de rede com equipamentos externos.

### Considerações

As análises deste projeto devem distinguir:
- Características documentadas pelo fabricante.
- Configurações observadas no projeto Wokwi.
- Comportamentos identificados pela análise do firmware.
- Resultados de testes efetivamente realizados na simulação.

Nenhum resultado simulado deve ser apresentado como uma medição de hardware físico.