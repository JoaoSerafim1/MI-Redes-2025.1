## 🐧 🐢 Usando o arquivo shell script (dockerscript.sh) para executar açoes de construcao, modificacao e acesso interativo do ambiente docker
```console
bash dockerscript.sh ACAO NUM
```
Utilize o comando no terminal Linux como descrito acima, sendo ACAO obrigatorio para todas as acoes, enquanto que NUM so e utilizado para uma das acoes.

- `build` compila a imagem e cria a rede necessaria.

Formato fixo: `bash dockerscript.sh build`

- `run` Instancia os containers para a aplicacao (1 de servidor e 4 de veiculos).

Formato fixo: `bash dockerscript.sh run`

- `stop` Apaga os containers instanciados.

Formato fixo: `bash dockerscript.sh stop`

- `transfer` copia os varios arquivos da aplicacao para os containers que farao uso deles. Pode e deve ser utilizado toda vez que houver modificacao nos arquivos da aplicacao.

Formato fixo: `bash dockerscript.sh transfer`

- `control` Assume o controle do terminal do container especificado no parametro NUM, com 0 referente ao container do servidor e 1-4 referente aos containers dos veiculos.

Exemplo: `bash dockerscript.sh control 3`

- `scrap` Apaga todos os containers, redes e imagens criadas pelas acoes `build`, e `run`.

Formato fixo: `bash dockerscript.sh scrap`
