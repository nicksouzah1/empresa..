from flask import jsonify, render_template, request
from mysql.connector import Error

from banco import conectar_banco

CADASTROS = {
    "empresa": {
        "titulo": "Empresas",
        "tabela": "empresa",
        "campos": ("nome", "cnpj", "email", "telefone", "endereco"),
        "rotulos": {
            "nome": "Nome",
            "cnpj": "CNPJ",
            "email": "E-mail",
            "telefone": "Telefone",
            "endereco": "Endereço",
        },
    },
    "funcionario": {
        "titulo": "Funcionários",
        "tabela": "funcionario",
        "campos": ("nome", "email", "telefone", "cargo", "empresa_id"),
        "rotulos": {
            "nome": "Nome",
            "email": "E-mail",
            "telefone": "Telefone",
            "cargo": "Cargo",
            "empresa_id": "Empresa",
        },
    },
}


def _resposta_erro(mensagem, status):
    return jsonify({"erro": mensagem}), status


def _normalizar_dados(tipo, dados):
    if not isinstance(dados, dict):
        return None, "Envie os dados do cadastro em formato JSON."

    cadastro = CADASTROS[tipo]
    valores = {}
    for campo in cadastro["campos"]:
        valor = dados.get(campo)
        if campo == "nome":
            valor = valor.strip() if isinstance(valor, str) else ""
            if not valor:
                return None, "O nome é obrigatório."
        elif campo == "empresa_id":
            try:
                valor = int(valor)
                if valor < 1:
                    raise ValueError
            except (TypeError, ValueError):
                return None, "Selecione uma empresa válida."
        elif valor is not None:
            valor = str(valor).strip() or None
        valores[campo] = valor
    return valores, None


def registrar_rotas_cadastros(app):
    @app.route("/empresa")
    @app.route("/funcionario")
    def pagina_cadastro():
        tipo = request.path.lstrip("/")
        return render_template(
            "cadastro.html",
            tipo=tipo,
            titulo=CADASTROS[tipo]["titulo"],
            campos=CADASTROS[tipo]["rotulos"],
        )

    @app.route("/api/<tipo>", methods=["GET", "POST"])
    def colecao_cadastro(tipo):
        if tipo not in CADASTROS:
            return _resposta_erro("Cadastro não encontrado.", 404)

        conexao = None
        cursor = None
        try:
            conexao = conectar_banco()
            cursor = conexao.cursor(dictionary=True)
            if request.method == "GET":
                if tipo == "funcionario":
                    cursor.execute(
                        """
                        SELECT f.id, f.nome, f.email, f.telefone, f.cargo,
                               f.empresa_id, e.nome AS empresa_nome
                        FROM funcionario f
                        JOIN empresa e ON e.id = f.empresa_id
                        ORDER BY f.nome
                        """
                    )
                else:
                    cursor.execute("SELECT * FROM empresa ORDER BY nome")
                return jsonify(cursor.fetchall()), 200

            valores, erro = _normalizar_dados(tipo, request.get_json(silent=True))
            if erro:
                return _resposta_erro(erro, 400)
            campos = CADASTROS[tipo]["campos"]
            colunas = ", ".join(campos)
            marcadores = ", ".join(["%s"] * len(campos))
            cursor.execute(
                f"INSERT INTO {CADASTROS[tipo]['tabela']} ({colunas}) "
                f"VALUES ({marcadores})",
                tuple(valores[campo] for campo in campos),
            )
            conexao.commit()
            return jsonify({"id": cursor.lastrowid, "mensagem": "Cadastro criado com sucesso."}), 201
        except Error as erro:
            if conexao:
                conexao.rollback()
            if getattr(erro, "errno", None) == 1452:
                return _resposta_erro("A empresa selecionada não existe.", 400)
            return _resposta_erro("Não foi possível acessar o banco de dados.", 500)
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    @app.route("/api/<tipo>/<int:registro_id>", methods=["PUT", "DELETE"])
    def item_cadastro(tipo, registro_id):
        if tipo not in CADASTROS:
            return _resposta_erro("Cadastro não encontrado.", 404)

        cadastro = CADASTROS[tipo]
        conexao = None
        cursor = None
        try:
            conexao = conectar_banco()
            cursor = conexao.cursor()
            if request.method == "DELETE":
                cursor.execute(
                    f"DELETE FROM {cadastro['tabela']} WHERE id = %s",
                    (registro_id,),
                )
                if cursor.rowcount == 0:
                    return _resposta_erro("Cadastro não encontrado.", 404)
                conexao.commit()
                return jsonify({"mensagem": "Cadastro removido com sucesso."}), 200

            valores, erro = _normalizar_dados(tipo, request.get_json(silent=True))
            if erro:
                return _resposta_erro(erro, 400)
            campos = cadastro["campos"]
            atribuicoes = ", ".join(f"{campo} = %s" for campo in campos)
            cursor.execute(
                f"UPDATE {cadastro['tabela']} SET {atribuicoes} WHERE id = %s",
                tuple(valores[campo] for campo in campos) + (registro_id,),
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    f"SELECT id FROM {cadastro['tabela']} WHERE id = %s",
                    (registro_id,),
                )
                if cursor.fetchone() is None:
                    return _resposta_erro("Cadastro não encontrado.", 404)
            conexao.commit()
            return jsonify({"mensagem": "Cadastro atualizado com sucesso."}), 200
        except Error as erro:
            if conexao:
                conexao.rollback()
            if getattr(erro, "errno", None) == 1451:
                return _resposta_erro(
                    "Não é possível remover uma empresa que possui funcionários vinculados.",
                    409,
                )
            if getattr(erro, "errno", None) == 1452:
                return _resposta_erro("A empresa selecionada não existe.", 400)
            return _resposta_erro("Não foi possível acessar o banco de dados.", 500)
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    @app.route("/api/empresas", methods=["GET"])
    def listar_empresas_para_funcionario():
        conexao = None
        cursor = None
        try:
            conexao = conectar_banco()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT id, nome FROM empresa ORDER BY nome")
            return jsonify(cursor.fetchall()), 200
        except Error:
            return _resposta_erro("Não foi possível carregar as empresas.", 500)
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()
