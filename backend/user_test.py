from flask import Flask, request, jsonify

from flask_cors import CORS

import mysql.connector

from mysql.connector import Error
 
app = Flask(__name__)

CORS(app)  # Permite acesso de todas as origens durante o desenvolvimento
 
# -----------------------------

# Função: Conexão com a Base de Dados

# -----------------------------

def connect_to_database():

    try:

        connection = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='BiaNatixis9624',
        database='bank_simulation'

        )

        if connection.is_connected():

            print("Ligação à base de dados estabelecida.")

            return connection

    except Error as e:

        print(f"Erro ao ligar à base de dados: {e}")

        return None
 
# -----------------------------

# Endpoint: Criar Utilizador

# -----------------------------

@app.route('/users', methods=['POST'])

def add_user():

    print("Pedido recebido no endpoint /users [POST]")  # Log inicial

    data = request.json

    print("Dados recebidos:", data)  # Log de dados recebidos
 
    if not data:

        return jsonify({"error": "Corpo da requisição está vazio!"}), 400
 
    name = data.get("name")

    email = data.get("email")

    nif = data.get("nif")

    birth_date = data.get("birth_date")

    address = data.get("address")

    phone = data.get("phone")
 
    if not all([name, email, nif, birth_date, address, phone]):

        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400
 
    connection = connect_to_database()

    if not connection:

        return jsonify({"error": "Erro ao ligar à base de dados."}), 500
 
    try:

        cursor = connection.cursor()

        query = """

        INSERT INTO users (name, email, nif, birth_date, address, phone)

        VALUES (%s, %s, %s, %s, %s, %s);

        """

        cursor.execute(query, (name, email, nif, birth_date, address, phone))

        connection.commit()

        print(f"Utilizador {name} criado com sucesso!")  # Log de sucesso

        return jsonify({"message": f"Utilizador {name} criado com sucesso!"}), 201

    except Exception as e:

        print(f"Erro ao criar utilizador: {e}")  # Log de erro

        return jsonify({"error": "Erro ao criar utilizador."}), 500

    finally:

        connection.close()

        print("Ligação à base de dados encerrada.")  # Log de encerramento
 
# -----------------------------

# Endpoint: Listar Utilizadores

# -----------------------------

@app.route('/users', methods=['GET'])

def get_users():

    print("Pedido recebido no endpoint /users [GET]")  # Log inicial

    connection = connect_to_database()

    if not connection:

        print("Erro: Conexão com a base de dados falhou.")  # Log de erro

        return jsonify({"error": "Erro ao ligar à base de dados."}), 500
 
    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users;")

        users = cursor.fetchall()

        print("Dados retornados da base de dados:", users)  # Log de dados recebidos

        return jsonify(users)  # Retorna utilizadores

    except Exception as e:

        print(f"Erro ao buscar utilizadores: {e}")  # Log de erro

        return jsonify({"error": "Erro ao buscar utilizadores."}), 500

    finally:

        connection.close()

        print("Ligação à base de dados encerrada.")  # Log de encerramento
 
# -----------------------------

# Endpoint: Criar Conta

# -----------------------------

@app.route('/accounts', methods=['POST'])

def add_account():

    print("Pedido recebido no endpoint /accounts [POST]")  # Log inicial

    data = request.json

    print("Dados recebidos:", data)  # Log de dados recebidos
 
    if not data:

        return jsonify({"error": "Corpo da requisição está vazio!"}), 400
 
    user_id = data.get("user_id")

    initial_balance = data.get("initial_balance")
 
    if not all([user_id, initial_balance]):

        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400
 
    connection = connect_to_database()

    if not connection:

        return jsonify({"error": "Erro ao ligar à base de dados."}), 500
 
    try:

        cursor = connection.cursor()

        query = """

        INSERT INTO accounts (user_id, balance)

        VALUES (%s, %s);

        """

        cursor.execute(query, (user_id, initial_balance))

        connection.commit()

        print(f"Conta criada com sucesso para o utilizador {user_id}.")  # Log de sucesso

        return jsonify({"message": "Conta criada com sucesso!"}), 201

    except Exception as e:

        print(f"Erro ao criar conta: {e}")  # Log de erro

        return jsonify({"error": "Erro ao criar conta."}), 500

    finally:

        connection.close()

        print("Ligação à base de dados encerrada.")  # Log de encerramento
 
# -----------------------------

# Endpoint: Realizar Transferência

# -----------------------------

@app.route('/transactions/transfer', methods=['POST'])

def transfer_funds():

    print("Pedido recebido no endpoint /transactions/transfer [POST]")  # Log inicial

    data = request.json

    print("Dados recebidos:", data)  # Log de dados recebidos
 
    if not data:

        return jsonify({"error": "Corpo da requisição está vazio!"}), 400
 
    from_account = data.get("from_account")

    to_account = data.get("to_account")

    amount = data.get("amount")
 
    if not all([from_account, to_account, amount]):

        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400
 
    connection = connect_to_database()

    if not connection:

        return jsonify({"error": "Erro ao ligar à base de dados."}), 500
 
    try:

        cursor = connection.cursor()
 
        # Verifica saldo da conta de origem

        cursor.execute("SELECT balance FROM accounts WHERE account_id = %s;", (from_account,))

        result = cursor.fetchone()

        if not result or result[0] < amount:

            print("Erro: Saldo insuficiente ou conta inexistente.")  # Log de erro

            return jsonify({"error": "Saldo insuficiente ou conta inexistente."}), 400
 
        # Deduz saldo da conta de origem

        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s;", (amount, from_account))
 
        # Adiciona saldo à conta de destino

        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s;", (amount, to_account))
 
        # Regista a transação

        cursor.execute("""

        INSERT INTO transactions (from_account, to_account, amount)

        VALUES (%s, %s, %s);

        """, (from_account, to_account, amount))
 
        connection.commit()

        print(f"Transferência de {amount} realizada com sucesso de {from_account} para {to_account}.")  # Log de sucesso

        return jsonify({"message": "Transferência realizada com sucesso!"}), 201

    except Exception as e:

        print(f"Erro ao realizar transferência: {e}")  # Log de erro

        return jsonify({"error": "Erro ao realizar transferência."}), 500

    finally:

        connection.close()

        print("Ligação à base de dados encerrada.")  # Log de encerramento
 
# -----------------------------

# Inicialização da Aplicação

# -----------------------------

if __name__ == '__main__':

    app.run(debug=True)

 