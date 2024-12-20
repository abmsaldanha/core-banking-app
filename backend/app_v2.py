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
CORS(app)
 
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
            # Inserção do utilizador na base de dados
            query = """
            INSERT INTO users (name, email, password_hash, nif, birth_date, address, phone, balance)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0);
            """
            cursor.execute(query, (name, email, password_hash, nif, birth_date, address, phone))
            connection.commit()
            # Obtenção do ID do utilizador recém-criado
            user_id = cursor.lastrowid
            # Criação do token JWT
            access_token = create_access_token(identity=str(user_id))
            return jsonify({
                "message": f"Utilizador {name} criado com sucesso!",
                "token": access_token
            }), 201
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
                id = str(user[0])
                access_token = create_access_token(identity=id)
                return jsonify({"message": "Login bem-sucedido!", "token": access_token}), 200
            else:
                return jsonify({"error": "Email ou password inválidos!"}), 401
    except Exception as e:
        print(f"Erro ao efetuar login: {e}")
        return jsonify({"error": "Erro ao efetuar login."}), 500
    finally:
        connection.close()


 
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
 
                balance = float(result[0])
                print("balance", balance)
                print("amount", amount)
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
    


@app.route('/movements', methods=['GET'])
@jwt_required()
def get_movements():
    print("### Início da função get_movements")
    try:
        user_id = get_jwt_identity()
        print(f"### User ID obtido: {user_id}")
 
        # Conexão com a base de dados
        connection = connect_to_database()
        if not connection:
            print("### Erro na conexão à base de dados.")
            return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
        try:
            cur = connection.cursor()
            print("### Cursor da base de dados criado.")
 
            # Query
            query = """
            SELECT transaction_id AS id, 'transfer' AS type, amount, COALESCE(date, NOW()) AS date
            FROM transactions
            WHERE user_id = %s
            UNION
            SELECT deposit_id AS id, 'deposit' AS type, amount, COALESCE(deposit_date, NOW()) AS date
            FROM deposits
            WHERE user_id = %s
            ORDER BY date DESC;
            """
            print("### Query a ser executada:", query)
 
            cur.execute(query, (user_id, user_id))
            print("### Query executada com sucesso.")
 
            movements = cur.fetchall()
            print(f"### Movimentos obtidos: {movements}")
 
            result = [{"type": row[1], "amount": row[2], "date": row[3]} for row in movements]
            print(f"### Resultado formatado: {result}")
 
            cur.close()
            return jsonify(result)
 
        except Exception as e:
            print(f"### Erro ao executar a query: {e}")
            connection.rollback()
            return jsonify({"error": "Erro ao obter movimentos."}), 500
        finally:
            connection.close()
            print("### Conexão à base de dados fechada.")
 
    except Exception as ex:
        print(f"### Erro inesperado: {ex}")
        return jsonify({"error": "Erro interno no servidor."}), 500
 
@app.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    try:
        user_id = get_jwt_identity()
        print(f"### User ID: {user_id}")
 
        connection = connect_to_database()
        if not connection:
            return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
        try:
            with connection.cursor() as cursor:
                query = "SELECT balance FROM users WHERE user_id = %s;"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                if result:
                    balance = result[0]
                    print(f"### Saldo devolvido: {balance}")
                    return jsonify({"balance": balance})
                else:
                    return jsonify({"error": "Utilizador não encontrado."}), 404
 
        except Exception as e:
            print(f"Erro ao calcular saldo: {e}")
            return jsonify({"error": "Erro ao calcular saldo."}), 500
        finally:
            connection.close()
    except Exception as ex:
        print(f"Erro inesperado: {ex}")
        return jsonify({"error": "Erro interno no servidor."}), 500
 
    except Exception as ex:
        print(f"Erro inesperado: {ex}")
        return jsonify({"error": "Erro interno no servidor."}), 500
    


# -----------------------------
# Inicialização da Aplicação
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)