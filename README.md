# Sistema de gestão de empresas e funcionários

Aplicação Flask para cadastrar empresas e funcionários, mantendo cada funcionário
vinculado a uma empresa.

## Como executar

1. Instale/ative o Python e instale as dependências necessárias (`Flask` e
   `mysql-connector-python`).
2. Inicie o MySQL. Na primeira conexão, a aplicação cria o banco
   `empresa_flask` e as tabelas `empresa` e `funcionario`. O usuário do MySQL
   precisa ter permissão para criar o banco e as tabelas.
3. Se necessário, configure a conexão por meio das variáveis
   `EMPRESA_DB_HOST`, `EMPRESA_DB_USER`, `EMPRESA_DB_PASSWORD` e
   `EMPRESA_DB_NAME`. Os padrões são `localhost`, `root`, senha vazia e
   `empresa_flask`.
4. Execute `python app.py` e acesse `http://127.0.0.1:5000`.

O login existente utiliza uma tabela `usuario` com as colunas `id`, `nome`,
`email`, `senha` e `ativo`; essa tabela e os usuários devem estar previamente
cadastrados. Após entrar, use os módulos Empresas e Funcionários na página
inicial. As operações também estão disponíveis pelas rotas JSON `/api/empresa`
e `/api/funcionario`.
