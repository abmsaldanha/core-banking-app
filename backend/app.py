from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
 
app = Flask(__name__)
CORS(app)  # Permite acesso de todas as origens (para desenvolvimento)
 
# Função para ligar à base de dados
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user="root",
            password="BiaNatixis9624",  # Atualiza para a tua senha MySQL
            database="bank_simulation"
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
    data = request.json
    print("Dados recebidos no endpoint /users:", data)
 
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
        print(f"Utilizador {name} criado com sucesso!")
        return jsonify({"message": f"Utilizador {name} criado com sucesso!"}), 201
    except Exception as e:
        print(f"Erro ao criar utilizador: {e}")
        return jsonify({"error": "Erro ao criar utilizador."}), 500
    finally:
        connection.close()
 
 
# -----------------------------
# Endpoint: Listar Utilizadores
# -----------------------------

"""
@app.route('/users', methods=['GET'])
def get_users():
    print("Pedido recebido no endpoint /users [GET]")
    connection = connect_to_database()
    if not connection:
        return jsonify({"error": "Erro ao ligar à base de dados."}), 500
 
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()
        print("Dados enviados:", users)
        return jsonify(users)
    except Exception as e:
        print(f"Erro ao buscar utilizadores: {e}")
        return jsonify({"error": "Erro ao buscar utilizadores."}), 500
    finally:
        connection.close()
"""

@app.route('/users', methods=['GET'])
def get_users():
    print("### Pedido recebido no endpoint /users [GET] ###")  # Log inicial
    try:
        print("### Tentando conectar à base de dados... ###")  # Log antes da conexão
        connection = connect_to_database()
        print("### Conexão à base de dados:", connection)  # Log do estado da conexão
        if not connection:
            return jsonify({"error": "Erro ao conectar à base de dados"}), 500
        return jsonify({"message": "Conexão bem-sucedida"}), 200
    except Exception as e:
        print(f"### Erro inesperado ao processar o endpoint: {e} ###")  # Log de erro
        return jsonify({"error": f"Erro inesperado: {e}"}), 500
 
 
# -----------------------------
# Endpoint: Criar Conta
# -----------------------------
@app.route('/accounts', methods=['POST'])
def add_account():
    data = request.json
    print("Dados recebidos no endpoint /accounts:", data)
 
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
        print(f"Conta criada com sucesso para o utilizador {user_id}.")
        return jsonify({"message": "Conta criada com sucesso!"}), 201
    except Exception as e:
        print(f"Erro ao criar conta: {e}")
        return jsonify({"error": "Erro ao criar conta."}), 500
    finally:
        connection.close()
 
 
# -----------------------------
# Endpoint: Listar Contas
# -----------------------------
@app.route('/accounts', methods=['GET'])
def get_accounts():
    print("Pedido recebido no endpoint /accounts [GET]")
    connection = connect_to_database()
    if not connection:
        return jsonify({"error": "Erro ao ligar à base de dados."}), 500
 
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM accounts;")
        accounts = cursor.fetchall()
        print("Dados enviados:", accounts)
        return jsonify(accounts)
    except Exception as e:
        print(f"Erro ao buscar contas: {e}")
        return jsonify({"error": "Erro ao buscar contas."}), 500
    finally:
        connection.close()
 
 
# -----------------------------
# Endpoint: Transferência
# -----------------------------
@app.route('/transactions/transfer', methods=['POST'])
def transfer_funds():
    data = request.json
    print("Dados recebidos no endpoint /transactions/transfer:", data)
 
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
 
        # Verifica saldo
        cursor.execute("SELECT balance FROM accounts WHERE account_id = %s;", (from_account,))
        result = cursor.fetchone()
        if not result or result[0] < amount:
            print("Erro: Saldo insuficiente ou conta inexistente.")
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
        print(f"Transferência de {amount} realizada com sucesso de {from_account} para {to_account}.")
        return jsonify({"message": "Transferência realizada com sucesso!"}), 201
    except Exception as e:
        print(f"Erro ao realizar transferência: {e}")
        return jsonify({"error": "Erro ao realizar transferência."}), 500
    finally:
        connection.close()
 
 
if __name__ == '__main__':
    app.run(debug=True)