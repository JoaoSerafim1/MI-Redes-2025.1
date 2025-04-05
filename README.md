# Instalação e uso da aplicação
## Requisitos básicos
- Sistema Operacional compatível com protocolo TCP-IP e Python (ex: [Ubuntu](https://ubuntu.com/download), [Windows](https://www.microsoft.com/pt-br/windows/))
- [Python](https://www.python.org/downloads/) 3.9

## 📦 Instalando e utilizando as diferentes versões do sistema distribuído

As versões do sistema estão disponíveis individualmente neste repositório online em formato .zip, na sessão "Releases" (encontrada no canto direito da tela inicial do repositório na maioria dos navegadores)

#### AVISO: Antes de utilizar qualquer das interfaces gráficas presentes em alguns dos programas python, certifique-se de as bibliotecas "TKinter" e "Custom TKinter" estão instaladas diretamente na máquina que exibirá tais interfaces.
```console
sudo apt-get install python3-tk -y && \
pip3 install customtkinter --break-system-packages
```
##### (Instala as bibliotecas em sistemas tipo Linux, consulte documentação do Python para fazer o mesmo em outros sistemas operacionais)

### ☁️ Servidor

O arquivo .zip do servidor possui ```server``` antes de seu número de versão. Para iniciar o programa do servidor, execute o arquivo ```server.py```, encontrado no diretório principal da aplicação.

![Tela inicial](/imgs/server_start_screen.png?raw=true "Instruções do programa e informação do endereço do servidor e do ID para cadastro da próxima estação de carga")

Após o cadastro de uma estação de carga, o servidor automaticamente gerará um novo ID que deverá ser utilizado na próxima operação do tipo, e em seguida exibirá na tela tal informação.

![Tela inicial apos primeira carga](/imgs/server_after_first_station.png?raw=true "Resultado no terminal de uma operação de cadastro de estação de carga")

O recebimento de mensagens, bem como a execução de ações em cima do banco de dados do servidor, são todas operações registrados em arquivos de texto (logs), os quais podem ser encontrados nas pastas ```/logs/received/``` (mensagens recebidas) e ```logs/performed/``` (ações executadas pelo servidor).

Logs possuem o seguinte formato:
- Título: YYYY-MM-DDD = Data local
- Conteúdo:
  - [YYYY-MM-DDD hh-mm-ss.ssssss] => Data e horário locais (24 horas)
  - NAME:
  - NOME-DA-ENTRADA => Informação do nome da entrada no log
    - RVMSG:         Mensagem recebida
    - RGTSTATION:    Registrar nova estação
    - RGTVEHICLE:    Registrar novo veículo
    - GETBOOKED:     Obter informações acerca de possível veículo agendado (estação)
    - FREESPOT:      Liberar estação para agendamento
    - GETDISTANCE:   Obter e retornar informações da estação dispónível mais próxima de um veículo
    - PHCCHARGE:     Confirmar pagamento e agendar recarga
    - PCHDETAILS:    Obter e retornar informações de uma determinada compra (de acordo com o ID do veículo vinculado à compra e ao índice da compra)
  - TIPO-DA-ENTIDADE => Tipo do identificador da entidade que gerou a entrada
    - ADDRESS:       Endereço IP (tipo de usuário não-definido)
    - S_ID:          ID de estação de carga
    - V_ID:          ID de veículo
    - V_ADD:         Endereço IP de um usuário que supõe-se ser um veículo
  - IDENTIFICADOR-DA-ENTIDADE => Identificador da entidade que gerou a entrada

![Tela do arquivo de texto de um log](/imgs/server_log.png?raw=true "Log referentes às ações executadas pelo servidor no dia 04 de Abril de 2025, data local")

Pressionar a tecla ENTER durante a execução do servidor inicia o processo de encerramento da aplicação, como já explicitado anteriormente na saída do terminal.

![Tela de encerramento](/imgs/server_terminating.png?raw=true "Resultado da sequência de encerramento do servidor")

## 🐧 🐢 Como utilizar o arquivo shell script (dockerscript.sh) para executar ações de construção, modificação e acesso interativo do/ao ambiente docker:
```console
bash dockerscript.sh ACAO NUM
```

### Utilize o comando no terminal Linux como descrito acima, sendo `ACAO` um paramêtro obrigatório para todas as ações, enquanto que `NUM` so é utilizado em uma destas.

### $${\color{yellow}"build"}$$  compila a imagem e cria a rede necessária.

- Formato fixo:
```console
bash dockerscript.sh build
```

### $${\color{green}"run"}$$ instancia os containers para a aplição (1 de servidor, 2 de estações e 4 de veículos).

- Formato fixo:
```console
bash dockerscript.sh run
```

### $${\color{orange}"stop"}$$ apaga os containers instanciados.

- Formato fixo:
```console
bash dockerscript.sh stop
```

### $${\color{lightgreen}"update"}$$ copia os varios arquivos da aplicação para os containers em execução. Pode e deve ser utilizado toda vez que houver alguma mudança nos arquivos da própria aplicacão (para atualizar os arquivos gerados durante a execução da aplicação, utilize o comando ´export´ como descrito mais abaixo).

- Formato fixo:
```console
bash dockerscript.sh update
```

### $${\color{black}"control"}$$ Assume o controle do terminal do container especificado no parâmetro `NUM`, sendo 0 referente ao container do servidor, 1-2 referente aos containers das estações, e 3-6 referente aos containers dos veículos.

- Exemplo:
```console
bash dockerscript.sh control 2
```
#### AVISO: Antes de realizar um acesso remoto a interfaces gráficas, certifique-se de a biblioteca "x11 Server Utils" para Linux está instalada, e em seguida habilite a execução remota de programas.
```console
sudo apt-get install x11-xserver-utils -y
```
##### (Instala a biblioteca)
```console
xhost +
```
##### (Habilita a execução remota de programas, deve ser executado sempre que o sistema for reiniciado)

### $${\color{blue}"import"}$$ Copia os arquivos e/ou diretórios gerados pelas aplicações em execução nos containers para a pasta `/files/imported`.

- Formato fixo:
```console
bash dockerscript.sh import
```

### $${\color{lightblue}"export"}$$ Copia os arquivos da pasta `/files/export` para suas respectivas pastas em seus respectivos containers, de acordo com a organização dentro da própria pasta `/files/export`.
Para re-inserir arquivos modificados nos containers, certifique-se de que a hierarquia em `/files/export` é a mesma encontrada em `/files/imported`, ou seja, tal como encontrado após o processo de importação.

- Formato fixo:
```console
bash dockerscript.sh export
```

### $${\color{red}"scrap"}$$ Apaga todos os containers, redes e imagens criadas pelas ações `build` e `run`.

- Formato fixo:
```console
bash dockerscript.sh scrap
```

### NOTA: O kit de desenvolvimento inclui um arquivo DOS-batch (dockerscript.bat) com comandos idênticos, exceto aqueles relacionados a interfaces gráficas, os quais estão totalmente ausentes.

# Bibliografia

## 🔧 📚 Paginas web consultadas para instalacao, solucao de problemas e aprendizado:
- **Instalacao:**
  - [_Install Docker Engine on Ubuntu_](https://docs.docker.com/engine/install/ubuntu)
- **Como resolver problemas ao executar o Docker**:
  - [_Cannot connect to the Docker daemon at unix:/var/run/docker.sock. Is the docker daemon running?_](https://stackoverflow.com/questions/44678725/cannot-connect-to-the-docker-daemon-at-unix-var-run-docker-sock-is-the-docker)
  - [_Is it possible to use docker without sudo?_](https://askubuntu.com/questions/1165877/is-it-possible-to-use-docker-without-sudo)
  - [_can i install customtkinter on linux_](https://www.reddit.com/r/Tkinter/comments/15sqnvx/can_i_install_customtkinter_on_linux/)
  - [_docker \_tkinter.TclError: couldn't connect to display_](https://stackoverflow.com/questions/49169055/docker-tkinter-tclerror-couldnt-connect-to-display/49229627#49229627)
- **Tutoriais**:
  - [_Docker Containers: IPC using Sockets — Part 2_](https://medium.com/techanic/docker-containers-ipc-using-sockets-part-2-834e8ea00768)
  - [_How to get bash or ssh into a running container in background mode?_](https://askubuntu.com/questions/505506/how-to-get-bash-or-ssh-into-a-running-container-in-background-mode/543057#543057)
