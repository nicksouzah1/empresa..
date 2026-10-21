from flask import request, jsonify, render_template
from banco import conectar_banco

def registrar_rotas_login(app):
    @app.route("/")
    def login():
        return render_template("login.html")

    @app.route("/api/login", methods=["POST"])
    def fazer_login():
        dados = request.get_json(silent=True) or {}
        email=dados.get("email")
        senha=dados.get("senha")

        try:
            conexao = conectar_banco()
            cursor = conexao.cursor(dictionary=True)
            sql = """
                SELECT id, nome, email,senha, ativo
                FROM usuario
                WHERE email = %s
            """
            cursor.execute(sql, (email,))
            usuario = cursor.fetchone()
            cursor.close()
            conexao.close()

            if not usuario or senha != usuario["senha"]:
                return jsonify({
                    "erro" : "E-mail ou senha inválidos!"
                }), 401
            return jsonify({
                "mensagem": "Login realizado com sucesso!",
                "usuario":{
                    "id":usuario["id"],
                    "nome":usuario["nome"],
                    "email":usuario["email"]
                }
            }), 200
        except Exception as erro:
            print("Erro:", erro)
            return jsonify({
                "erro":"Erro interno no servidor"
            }), 500
    @app.route("/sistema")
    def sistema():
        return render_template("index.html")
