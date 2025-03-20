## 🐧 🐢 Usando o arquivo shell script (dockerscript.sh) para executar açoes de construcao e modificacao do ambiente docker
```console
bash dockerscript.sh ACAO NUM
```
Utilize o comando no terminal Linux como descrito acima, sendo ACAO obrigatorio para todas as acoes, enquanto que NUM so e utilizado para uma das acoes.

- `build` compila a imagem, cria a rede necessaria e instacia os containers para a aplicacao (1 de servidor e 4 de veiculos).

Formato fixo: `bash dockerscprit.sh build`

- `transfer` copia os varios arquivos da aplicacao para os containers que farao uso deles. Pode e deve ser utilizado toda vez que houver modificacao nos arquivos da aplicacao.

Formato fixo: `bash dockerscprit.sh transfer`

- `control` Assume controle do terminal do container especificado no parametro NUM, com 0 referente ao container do servidor e 1-4 referente aos containers dos veiculos.

Exemplo: `bash dockerscprit.sh control 3`

- `scrap` remove todos os containers, redes e imagens criadas pela acao `build`.

Formato fixo: `bash dockerscprit.sh scrap`
