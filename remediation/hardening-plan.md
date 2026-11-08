# Plano de hardening — versão comercial

As medidas abaixo são propostas de engenharia para uma futura versão de produção. O protótipo Wokwi não foi submetido a programação irreversível de eFuses, testes em placa física ou implantação comercial.

## Prioridade 1 — Identidade, credenciais e comunicação

- Remover segredos de fontes, binários distribuídos, capturas e documentação pública. Gerar uma identidade criptográfica única por dispositivo durante fabricação/provisionamento; não usar API Key comum a todos.
- Usar TLS com certificado verificável pelo cliente (ou pinning com ciclo de rotação definido). Não tratar `-k`, certificados autoassinados sem distribuição de confiança, ou chave privada compilada e reutilizada como configuração de produção.
- Aplicar autorização por dispositivo, expiração/rotação e revogação. Limitar privilégios e dados expostos por rota.
- Usar WPA2/WPA3 e mecanismo de provisionamento que não exponha senhas no firmware-fonte, logs ou repositório.

## Prioridade 2 — Boot, flash e atualização

- Avaliar Secure Boot e Flash Encryption em modo de produção, com chaves únicas por dispositivo quando aplicável. Planejar geração, custódia, backup e rotação de chaves.
- Implementar atualização OTA autenticada, assinada e validada antes de instalar; proteger contra downgrade e manter um mecanismo de recuperação testado.
- Definir ciclo de suporte, inventário de componentes/dependências, monitoramento de avisos de segurança e processo de atualização.
- Tratar os eFuses como decisão de fabricação irreversível: testar todo o fluxo em placas de desenvolvimento e aprovar procedimento de recuperação antes de habilitá-los em produto.

## Prioridade 3 — Interfaces, depuração e disponibilidade

- Desabilitar ou controlar JTAG e modos de download UART em produção de acordo com o processo de serviço e recuperação.
- Remover informações de depuração desnecessárias; não imprimir dados sensíveis ou credenciais.
- Manter timeout de conexão e implementar reconexão com backoff, estado observável e comportamento seguro sem rede.
- Revisar a margem de flash do protótipo (99,4% do limite de aplicação no build atual) antes de incorporar OTA, armazenamento de certificados ou atualizações futuras.

## Referências de apoio

- NISTIR 8259A: capacidades de identificação, configuração, proteção de dados, controle de interfaces, atualização e estado de segurança.
- ETSI EN 303 645 V3.1.3: credenciais, atualizações, comunicação segura, proteção da integridade e redução da superfície de ataque.
- Espressif ESP-IDF Security: Secure Boot, Flash Encryption, JTAG/UART e segurança de rede.
- MITRE EMB3D: seleção de ameaças conforme propriedades do dispositivo e interfaces observáveis.

Nenhuma recomendação acima é declarada implementada apenas por estar neste plano. A versão atual implementa TLS de laboratório, verificação de API Key e timeout inicial de Wi-Fi; os riscos residuais estão registrados em `findings/findings.md`.
