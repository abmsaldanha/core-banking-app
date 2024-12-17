from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from flask_cors import CORS
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import sys
 
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "chave-secreta-para-jwt"  # Altera para uma chave segura
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
 
# -----------------------------
# Função: Conexão com a Base de Dados
# -----------------------------
def connect_to_database():
    try:
        connection = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="BiaNatixis9624",
            database="bank_simulation"
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar à base de dados: {e}")
        return None
 
# -----------------------------
# Endpoint: Criar Utilizador
# -----------------------------
@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    nif = data.get("nif")
    birth_date = data.get("birth_date")
    address = data.get("address")
    phone = data.get("phone")
 
    if not all([name, email, password, nif, birth_date, address, phone]):
        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400
 
    password_hash = generate_password_hash(password)
 
    connection = connect_to_database()
    if not connection:
        return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
    try:
        with connection.cursor() as cursor:
            query = """
            INSERT INTO users (name, email, password_hash, nif, birth_date, address, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (name, email, password_hash, nif, birth_date, address, phone))
            connection.commit()
            return jsonify({"message": f"Utilizador {name} criado com sucesso!"}), 201
    except Exception as e:
        print(f"Erro ao criar utilizador: {e}")
        return jsonify({"error": "Erro ao criar utilizador."}), 500
    finally:
        connection.close()
 
# -----------------------------
# Endpoint: Login
# -----------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
 
    connection = connect_to_database()
    if not connection:
        return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and check_password_hash(user[1], password):
                access_token = create_access_token(identity=user[0])
                return jsonify({"message": "Login bem-sucedido!", "token": access_token}), 200
            else:
                return jsonify({"error": "Email ou password inválidos!"}), 401
    except Exception as e:
        print(f"Erro ao efetuar login: {e}")
        return jsonify({"error": "Erro ao efetuar login."}), 500
    finally:
        connection.close()
 
# -----------------------------
# Endpoint: Logout (Opcional)
# -----------------------------
# Com JWT, o logout no backend é opcional, pois o token expira automaticamente.
# No entanto, se quiseres implementar uma lista de tokens revogados, podes fazê-lo.
 
# -----------------------------
# Endpoint: Obter Utilizadores (Protegido)
# -----------------------------
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    connection = connect_to_database()
    if not connection:
        return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT user_id, name, email, nif FROM users;")
            users = cursor.fetchall()
            return jsonify(users), 200
    except Exception as e:
        print(f"Erro ao buscar utilizadores: {e}")
        return jsonify({"error": "Erro ao buscar utilizadores."}), 500
    finally:
        connection.close()
 
# -----------------------------
# Endpoint: Realizar Transferência (Protegido)
# -----------------------------
@app.route('/transactions', methods=['GET', 'POST'])
@jwt_required()
def manage_transactions():
    raise Exception("Sorry, no numbers below zero")

    user_id = get_jwt_identity()
 
    if request.method == 'GET':
        # Obter histórico de transações
        connection = connect_to_database()
        if not connection:
            return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                query = """
                SELECT transaction_id, to_iban, amount, transaction_date 
                FROM transactions 
                WHERE user_id = %s 
                ORDER BY transaction_date DESC;
                """
                cursor.execute(query, (user_id,))
                transactions = cursor.fetchall()
                return jsonify(transactions), 200
        except Exception as e:
            print(f"Erro ao buscar transações: {e}")
            return jsonify({"error": "Erro ao buscar transações."}), 500
        finally:
            connection.close()
 
    elif request.method == 'POST':
        # Realizar nova transferência
        data = request.json
        raise Exception(data)

        to_iban = data.get("to_iban")
        amount = data.get("amount")
 
        if not all([to_iban, amount]):
            return jsonify({"error": "Todos os campos são obrigatórios!"}), 400
 
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({"error": "O montante deve ser positivo."}), 400
        except ValueError:
            return jsonify({"error": "Montante inválido."}), 400
 
        connection = connect_to_database()
        if not connection:
            return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
        try:
            with connection.cursor() as cursor:
                # Verificar saldo do utilizador
                cursor.execute("SELECT balance FROM users WHERE user_id = %s;", (user_id,))
                result = cursor.fetchone()
                if not result:
                    return jsonify({"error": "Utilizador não encontrado."}), 404
 
                balance = result[0]
                if balance < amount:
                    return jsonify({"error": "Saldo insuficiente."}), 400
 
                # Atualizar saldo
                cursor.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s;", (amount, user_id))
 
                # Registar transação
                cursor.execute("""
                    INSERT INTO transactions (user_id, to_iban, amount)
                    VALUES (%s, %s, %s);
                """, (user_id, to_iban, amount))
 
                connection.commit()
                return jsonify({"message": "Transferência realizada com sucesso!"}), 201
        except Exception as e:
            connection.rollback()
            print(f"Erro ao realizar transferência: {e}")
            return jsonify({"error": "Erro ao realizar transferência."}), 500
        finally:
            connection.close()
 
# -----------------------------
# Endpoint: Depósito (Protegido)
# -----------------------------
@app.route('/deposits', methods=['POST'])
@jwt_required()
def deposit():
    try:
        data = request.get_json()
        print("### Dados recebidos:", data)
 
        amount = data.get("amount")
        if not amount or not isinstance(amount, (int, float)) or float(amount) <= 0:
            return jsonify({"error": "O montante do depósito deve ser um número positivo."}), 422
 
        user_id = get_jwt_identity()
 
        # Conexão com a base de dados
        connection = connect_to_database()
        if not connection:
            return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
        try:
            with connection.cursor() as cursor:
                # Atualizar saldo do utilizador
                cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s;", (amount, user_id))
 
                # Registar depósito na tabela de depósitos
                cursor.execute("""
                    INSERT INTO deposits (user_id, amount)
                    VALUES (%s, %s);
                """, (user_id, amount))
 
                connection.commit()
                return jsonify({"message": "Depósito realizado com sucesso!"}), 201
        except Exception as e:
            connection.rollback()
            print(f"Erro ao processar depósito: {e}")
            return jsonify({"error": "Erro ao processar depósito."}), 500
        finally:
            connection.close()
 
    except Exception as ex:
        print(f"Erro inesperado: {ex}")
        return jsonify({"error": "Erro interno no servidor."}), 500


# -----------------------------
# Inicialização da Aplicação
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)