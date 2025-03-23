## 🐧 🐢 Usando o arquivo shell script (dockerscript.sh) para executar açoes de construcao, modificacao e acesso interativo do ambiente docker
```console
bash dockerscript.sh ACAO NUM
```
Utilize o comando no terminal Linux como descrito acima, sendo `ACAO` obrigatorio para todas as acoes, enquanto que `NUM` so e utilizado para uma das acoes.

`build` compila a imagem e cria a rede necessaria.

- Formato fixo:
```console
bash dockerscript.sh build
```

`run` Instancia os containers para a aplicacao (1 de servidor e 4 de veiculos).

- Formato fixo:
```console
bash dockerscript.sh run
```

`stop` Apaga os containers instanciados.

- Formato fixo:
```console
bash dockerscript.sh stop
```

`update` Copia os varios arquivos da aplicacao para os containers que farao uso deles. Pode e deve ser utilizado toda vez que houver modificacao nos arquivos da aplicacao.

- Formato fixo:
```console
bash dockerscript.sh update
```

`control` Assume o controle do terminal do container especificado no parametro `NUM`, com 0 referente ao container do servidor e 1-4 referente aos containers dos veiculos.

- Exemplo:
```console
bash dockerscript.sh control 3
```

`import` Copia os arquivos e/ou diretorios gerados pelas aplicacao em execucao nos containers para a pasta `/files/imported`.

- Formato fixo:
```console
bash dockerscript.sh import
```

`export` Copia os arquivos da pasta `/files/export` para suas respectivas pastas em seus respectivos containers, de acordo com a organizacao dentro da propria pasta `/files/export`.
Para re-inserir arquivos modificados nos containers, certifique-se de que a hierarquia em `/files/export` e a mesma encontrada em `/files/imported` (apos o processo de importacao).

- Formato fixo:
```console
bash dockerscript.sh export
```


`scrap` Apaga todos os containers, redes e imagens criadas pelas acoes `build`, e `run`.

- Formato fixo:
```console
bash dockerscript.sh scrap
```
