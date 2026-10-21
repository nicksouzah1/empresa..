from flask import Flask
from cadastros import registrar_rotas_cadastros

from login import registrar_rotas_login

app = Flask(__name__)

registrar_rotas_login(app)
registrar_rotas_cadastros(app)

print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True)