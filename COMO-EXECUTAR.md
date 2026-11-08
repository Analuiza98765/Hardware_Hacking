# Como instalar, configurar e executar o NexaSense

Este guia reproduz a compilação e os testes do protótipo no VS Code com PlatformIO e Wokwi. A simulação não exige uma placa física.

## 1. Instalações necessárias

1. Instale o [Visual Studio Code](https://code.visualstudio.com/).
2. No VS Code, abra **Extensões** (`Ctrl+Shift+X`) e instale:
   - **PlatformIO IDE** (`platformio.platformio-ide`) — compila o firmware e instala as dependências do projeto.
   - **Wokwi Simulator** (`wokwi.wokwi-vscode`) — simula o ESP32 e o DHT22. Se solicitado, entre na sua conta Wokwi.
3. Instale o [Python 3](https://www.python.org/downloads/) e habilite a opção de adicionar Python ao `PATH` durante a instalação.
4. Abra no VS Code a pasta do projeto que contém `platformio.ini`, `diagram.json` e `wokwi.toml`.

O primeiro build precisa de acesso à Internet para baixar a plataforma e as bibliotecas indicadas em `platformio.ini`.

O arquivo `requirements.txt` fixa as dependências Python usadas pelos scripts. As dependências do firmware são gerenciadas separadamente pelo PlatformIO, conforme `platformio.ini`.

## 2. Preparação local das credenciais e do certificado

Abra um terminal PowerShell na pasta do projeto:

```powershell
if (-not (Test-Path src\secrets.h)) {
    Copy-Item src\secrets.example.h src\secrets.h
} else {
    Write-Output "src\secrets.h ja existe; arquivo local preservado."
}
python -m pip install -r requirements.txt
```

Edite `src\secrets.h` e substitua o texto de exemplo por uma chave aleatória exclusiva para este laboratório. Se quiser gerar uma no terminal:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copie o valor gerado diretamente para `src\secrets.h`. Não o envie em mensagens, capturas ou repositórios. Esse arquivo é ignorado pelo Git.

Gere o certificado autoassinado de laboratório e o cabeçalho usado pelo firmware:

```powershell
python certificates\generate_certificate.py
```

Isso cria arquivos locais em `certificates\` e `src\certificates.h`. A chave privada e os binários resultantes não devem ser distribuídos. Se gerar um certificado novo, use também o mesmo `certificates\server-cert.der` no teste HTTPS, pois ele compara o certificado apresentado pelo simulador com essa cópia local.

## 3. Compilar e iniciar a simulação

No terminal do VS Code:

```powershell
pio run
```

Também é possível compilar com o botão **Build** da extensão PlatformIO. Depois:

1. Abra a paleta de comandos com `Ctrl+Shift+P`.
2. Execute **Wokwi: Start Simulator**.
3. Aguarde no monitor serial as mensagens de conexão ao Wi-Fi e de inicialização do servidor HTTPS.

O diagrama já conecta o DHT22 ao GPIO 15 e a UART ao monitor serial. O encaminhamento local do Wokwi usa `localhost:8443` para acessar a porta HTTPS 443 do dispositivo simulado.

## 4. Executar os testes

Com a simulação ativa e o servidor HTTPS iniciado:

```powershell
python network\test_api_https.py
```

O resultado esperado inclui HTTP 401 sem chave, HTTP 401 com chave incorreta, HTTP 200 com a chave local, HTTP 200 na rota `/` e HTTP 404 em uma rota inexistente. O script também verifica a estrutura do JSON e compara o certificado recebido com o certificado DER local. O pinning e o certificado autoassinado são exclusivos deste teste local, não uma configuração para produção.

Para repetir o teste controlado de falha do sensor:

1. Remova temporariamente as conexões do DHT22 em `diagram.json`.
2. Pare e inicie a simulação para carregar a alteração.
3. Execute:

```powershell
python network\test_api_https.py --expect-sensor-error
```

4. Restaure as três conexões do DHT22, pare e inicie a simulação novamente e rode o teste normal.

O experimento HTTP independente, restrito ao loopback do computador, é executado com:

```powershell
python network\teste_http.py
```

## 5. Limites

Esta atividade foi realizada a distância (EAD), e o equipamento físico não foi fornecido. Assim, os resultados de execução são da simulação Wokwi; não representam medições elétricas, acesso real a UART/JTAG ou extração da Flash de uma placa.

## Solução de problemas

- **`pio` não é reconhecido:** aguarde a inicialização do PlatformIO no VS Code, use o botão **Build** ou abra o terminal PlatformIO integrado.
- **`ConnectionRefusedError` em `localhost:8443`:** inicie o Wokwi e aguarde o servidor HTTPS no monitor serial; confira a regra em `wokwi.toml`.
- **Erro de certificado no teste:** confirme que `certificates\server-cert.der` corresponde ao certificado usado para gerar `src\certificates.h`; execute novamente o gerador e recompile se necessário.
- **Erro de segredo:** confirme que `src\secrets.h` existe e não contém o texto `REPLACE_WITH_...`.
