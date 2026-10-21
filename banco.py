import os
from threading import Lock

import mysql.connector

_banco_preparado = False
_preparacao_lock = Lock()


def _configuracao():
    return {
        "host": os.getenv("EMPRESA_DB_HOST", "localhost"),
        "user": os.getenv("EMPRESA_DB_USER", "root"),
        "password": os.getenv("EMPRESA_DB_PASSWORD", ""),
        "database": os.getenv("EMPRESA_DB_NAME", "empresa_flask"),
    }


def conectar_banco():
    global _banco_preparado
    config = _configuracao()

    if not _banco_preparado:
        with _preparacao_lock:
            if not _banco_preparado:
                conexao_admin = mysql.connector.connect(
                    host=config["host"],
                    user=config["user"],
                    password=config["password"],
                )
                try:
                    cursor = conexao_admin.cursor()
                    cursor.execute(
                        f"CREATE DATABASE IF NOT EXISTS `{config['database']}` "
                        "CHARACTER SET utf8mb4"
                    )
                    cursor.close()
                finally:
                    conexao_admin.close()

                conexao = mysql.connector.connect(**config)
                try:
                    cursor = conexao.cursor()
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS empresa (
                            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            nome VARCHAR(150) NOT NULL,
                            cnpj VARCHAR(18) NULL,
                            email VARCHAR(150) NULL,
                            telefone VARCHAR(30) NULL,
                            endereco VARCHAR(255) NULL
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                        """
                    )
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS funcionario (
                            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            nome VARCHAR(150) NOT NULL,
                            email VARCHAR(150) NULL,
                            telefone VARCHAR(30) NULL,
                            cargo VARCHAR(100) NULL,
                            empresa_id INT NOT NULL,
                            CONSTRAINT fk_funcionario_empresa
                                FOREIGN KEY (empresa_id) REFERENCES empresa(id)
                                ON DELETE RESTRICT ON UPDATE CASCADE
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                        """
                    )
                    cursor.close()
                    conexao.commit()
                finally:
                    conexao.close()
                _banco_preparado = True

    return mysql.connector.connect(**config)
