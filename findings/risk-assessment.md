# Avaliação e priorização de riscos — NexaSense

## Critérios

- **Impacto:** consequência potencial para confidencialidade, integridade ou disponibilidade.
- **Probabilidade:** possibilidade no cenário e com as condições de acesso avaliados.
- **Risco:** classificação qualitativa preliminar; não é uma pontuação quantitativa nem substitui análise do produto comercial.

## Matriz

| ID | Evidência / fragilidade | Impacto | Probabilidade | Risco atual | Tratamento |
|---|---|---|---|---|---|
| F-01 | API original sem autenticação; atual verifica `X-API-Key` | Médio | Média em rede alcançável | Médio residual | Implementado e testado no Wokwi (401/401/200); segredo embarcado exige identidade individual |
| F-02 | HTTP/80 original; atual usa HTTPS/443 com certificado de teste autoassinado | Médio | Média em rede compartilhada | Médio residual | TLS 1.2 validado na simulação; fixar e validar cadeia TLS e proteger chaves em produção |
| F-03 | `Wokwi-GUEST` sem senha | Contextual | Não aplicável ao simulador | Não classificado | Não é vulnerabilidade confirmada; usar rede protegida em produção |
| F-04 | Espera Wi-Fi infinita no fonte original; atual limita a 10 s | Médio (indisponibilidade) | Alta se rede indisponível | Baixo/Médio residual | Timeout confirmado no Wokwi pelo VS Code; implementar reconexão/backoff |
| F-05 | Chaves necessárias ao serviço ficam recuperáveis da imagem de firmware | Médio | Média com acesso à imagem/dispositivo | Médio | Configuração de fonte separada não elimina extração do binário; usar identidade única e armazenamento protegido |

## Priorização

1. **F-05 / F-02:** desenhar provisionamento individual e confiança TLS por dispositivo; impedir reutilização/publicação de chaves de laboratório.
2. **F-01:** substituir API Key estática de demonstração por autorização adequada ao produto, com rotação/revogação.
3. **F-04:** adicionar reconexão limitada com backoff e observar o estado sem expor dados sensíveis.
4. **Interfaces físicas:** validar em placa autorizada a exposição UART/JTAG e restringir os modos de debug/download em produção.
5. **Atualização:** especificar atualização assinada, proteção contra downgrade e recuperação; não há implementação OTA identificada no código examinado.

As medidas de Secure Boot, Flash Encryption e controle de debug são propostas conceituais; não foram ativadas irreversivelmente durante a atividade.

## Limitações

Resultados baseados em fonte, configuração e simulação Wokwi. Não foram feitos testes físicos, captura de tráfego do ESP32, dump de flash ou validação de uma rede de produção. Para contexto e referências, consulte `findings/findings.md`.
