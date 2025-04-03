# Instalação E Uso Do Sistema
## 🐧 🐢 / 💻 📨 Usando o arquivo shell script (dockerscript.sh) ou batch (dockerscript.bat) para executar açoes de construção, modificação e acesso interativo do/ao ambiente docker:
```console
bash dockerscript.sh ACAO NUM
```
(Linux)
```console
.\dockerscript.bat ACAO NUM
```
(Windows)

### Utilize o comando no terminal Linux como descrito acima, sendo `ACAO` um paramêtro obrigatório para todas as ações, enquanto que `NUM` so é utilizado em uma destas.

### $${\color{yellow}"build"}$$  compila a imagem e cria a rede necessária.

- Formato fixo:
```console
bash dockerscript.sh build
```
(Linux)
```console
.\dockerscript.bat build
```
(Windows)

### $${\color{green}"run"}$$ instancia os containers para a aplição (1 de servidor, 2 de estações e 4 de veículos).

- Formato fixo:
```console
bash dockerscript.sh run
```
 (Linux)
```console
.\dockerscript.bat run
```
(Windows)

### $${\color{orange}"stop"}$$ apaga os containers instanciados.

- Formato fixo:
```console
bash dockerscript.sh stop
```
(Linux)
```console
.\dockerscript.bat stop
```
(Windows)

### $${\color{lightgreen}"update"}$$ copia os varios arquivos da aplicação para os containers em execução. Pode e deve ser utilizado toda vez que houver alguma mudança nos arquivos da própria aplicacão (para atualizar os arquivos gerados durante a execução da aplicação, utilize o comando ´export´ como descrito mais abaixo).

- Formato fixo:
```console
bash dockerscript.sh update
```
(Linux)
```console
.\dockerscript.bat update
```
(Windows)

### $${\color{black}"control"}$$ Assume o controle do terminal do container especificado no parâmetro `NUM`, sendo 0 referente ao container do servidor, 1-2 referente aos containers das estações, e 3-6 referente aos containers dos veículos.

- Exemplo:
```console
bash dockerscript.sh control 2
```
(Linux)
```console
.\dockerscript.bat control 2
```
(Windows)

### $${\color{blue}"import"}$$ Copia os arquivos e/ou diretórios gerados pelas aplicações em execução nos containers para a pasta `/files/imported`.

- Formato fixo:
```console
bash dockerscript.sh import
```
(Linux)
```console
.\dockerscript.bat import
```
(Windows)

### $${\color{lightblue}"export"}$$ Copia os arquivos da pasta `/files/export` para suas respectivas pastas em seus respectivos containers, de acordo com a organização dentro da própria pasta `/files/export`.
Para re-inserir arquivos modificados nos containers, certifique-se de que a hierarquia em `/files/export` é a mesma encontrada em `/files/imported`, ou seja, tal como encontrado após o processo de importação.

- Formato fixo:
```console
bash dockerscript.sh export
```
(Linux)
```console
.\dockerscript.bat export
```
(Windows)

### $${\color{blue}"scrap"}$$ Apaga todos os containers, redes e imagens criadas pelas ações `build` e `run`.

- Formato fixo:
```console
bash dockerscript.sh scrap
```
(Linux)
```console
.\dockerscript.bat scrap
```
(Windows)

# Bibliografia

## 🔧 📚 Paginas web consultadas para instalacao, solucao de problemas e aprendizado:
- **Instalacao:**
  - [_Install Docker Engine on Ubuntu_](https://docs.docker.com/engine/install/ubuntu)
- **Como resolver problemas ao executar o Docker**:
  - [_Cannot connect to the Docker daemon at unix:/var/run/docker.sock. Is the docker daemon running?_](https://stackoverflow.com/questions/44678725/cannot-connect-to-the-docker-daemon-at-unix-var-run-docker-sock-is-the-docker)
  - [_Is it possible to use docker without sudo?_](https://askubuntu.com/questions/1165877/is-it-possible-to-use-docker-without-sudo)
- **Tutoriais**:
  - [_Docker Containers: IPC using Sockets — Part 2_](https://medium.com/techanic/docker-containers-ipc-using-sockets-part-2-834e8ea00768)
  - [_How to get bash or ssh into a running container in background mode?_](https://askubuntu.com/questions/505506/how-to-get-bash-or-ssh-into-a-running-container-in-background-mode/543057#543057)
