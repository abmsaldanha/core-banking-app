from flask import Flask, request, jsonify, session
from functools import wraps
from flask_cors import CORS
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
 
app = Flask(__name__)
app.secret_key = "chave-secreta-para-sessao"  # Muda para algo mais seguro em produção
CORS(app)  # Permite o acesso entre frontend e backend durante o desenvolvimento
 
# -----------------------------
# Função: Conexão com a Base de Dados
# -----------------------------
def connect_to_database():
    try:
        print("### Tentando conectar à base de dados... ###")  # Log inicial
        connection = pymysql.connect(
            host="127.0.0.1",         # Atualiza se necessário
            user="root",              # Atualiza com o teu utilizador MySQL
            password="BiaNatixis9624",   # Atualiza com a tua senha MySQL
            database="bank_simulation"  # Atualiza com o nome da tua base de dados
        )
        print("### Ligação à base de dados estabelecida com sucesso! ###")  # Log de sucesso
        return connection
    except pymysql.MySQLError as e:
        print(f"### Erro MySQL: {e} ###")  # Log de erros específicos do PyMySQL
        return None
    except Exception as ex:
        print(f"### Erro inesperado: {ex} ###")  # Log de erros gerais
        return None


def login_required(func):
    @wraps(func)  # Preserva o nome e documentação original da função decorada
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:  # Verifica se há um `user_id` na sessão
            return jsonify({"error": "Autenticação necessária!"}), 401
        return func(*args, **kwargs)  # Executa a função original se o utilizador estiver autenticado
    return wrapper


# Endpoint para login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
 
    if not email or not password:
        return jsonify({"error": "Email e password são obrigatórios!"}), 400
 
    connection = connect_to_database()
    if not connection:
        return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
    try:
        with connection.cursor() as cursor:
            query = "SELECT user_id, password_hash FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
 
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                return jsonify({"message": "Login bem-sucedido!"}), 200
            else:
                return jsonify({"error": "Email ou password inválidos!"}), 401
    except Exception as e:
        print(f"Erro ao processar login: {e}")
        return jsonify({"error": "Erro interno do servidor."}), 500
    finally:
        connection.close()
 
# -----------------------------
# Endpoint: Logout
# -----------------------------

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Remove todas as informações da sessão
    return jsonify({"message": "Logout realizado com sucesso!"}), 200

# -----------------------------
# Endpoint: Criar Utilizador
# -----------------------------
@app.route('/users', methods=['POST'])
def add_user():
    print("### Pedido recebido no endpoint /users [POST] ###")
    data = request.json
    print("### Dados recebidos:", data)
 
    if not data:
        return jsonify({"error": "Corpo da requisição está vazio!"}), 400
 
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")  # Recebe a password enviada
    nif = data.get("nif")
    birth_date = data.get("birth_date")
    address = data.get("address")
    phone = data.get("phone")
 
    if not all([name, email, password, nif, birth_date, address, phone]):
        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400
    
      # Gera o hash da password
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
            print(f"### Utilizador {name} criado com sucesso! ###")
            return jsonify({"message": f"Utilizador {name} criado com sucesso!"}), 201
    except Exception as e:
        print(f"### Erro ao criar utilizador: {e} ###")
        return jsonify({"error": "Erro ao criar utilizador."}), 500
    finally:
        connection.close()
        print("### Ligação à base de dados encerrada. ###")
 
# -----------------------------
# Endpoint: Listar Utilizadores
# -----------------------------
@app.route('/users', methods=['GET'])
def get_users():
    print("### Pedido recebido no endpoint /users [GET] ###")
    connection = connect_to_database()
    if not connection:
        print("### Erro: Conexão à base de dados falhou ###")
        return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM users;")
            users = cursor.fetchall()
            print("### Dados retornados da base de dados:", users)
            return jsonify(users)
    except Exception as e:
        print(f"### Erro ao buscar utilizadores: {e} ###")
        return jsonify({"error": "Erro ao buscar utilizadores."}), 500
    finally:
        connection.close()
        print("### Ligação à base de dados encerrada. ###")
 
# -----------------------------
# Endpoint: Criar Conta
# -----------------------------


@app.route('/accounts', methods=['GET', 'POST'])
@login_required
def manage_accounts():
    if request.method == 'GET':
        print("### Pedido recebido no endpoint /accounts [GET] ###")
        connection = connect_to_database()
        if not connection:
            return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM accounts;")
                accounts = cursor.fetchall()
                print("### Dados retornados da base de dados:", accounts)
                return jsonify(accounts)  # Retorna as contas no formato JSON
        except Exception as e:
            print(f"### Erro ao buscar contas: {e} ###")
            return jsonify({"error": "Erro ao buscar contas."}), 500
        finally:
            connection.close()
            print("### Ligação à base de dados encerrada. ###")
 
    elif request.method == 'POST':
        print("### Pedido recebido no endpoint /accounts [POST] ###")
        data = request.json
        print("### Dados recebidos:", data)
 
        if not data:
            return jsonify({"error": "Corpo da requisição está vazio!"}), 400
 
        user_id = data.get("user_id")
        initial_balance = data.get("initial_balance")
 
        if not all([user_id, initial_balance]):
            return jsonify({"error": "Todos os campos são obrigatórios!"}), 400
 
        connection = connect_to_database()
        if not connection:
            return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
        try:
            with connection.cursor() as cursor:
                query = """
                INSERT INTO accounts (user_id, balance)
                VALUES (%s, %s);
                """
                cursor.execute(query, (user_id, initial_balance))
                connection.commit()
                print(f"### Conta criada com sucesso para o utilizador {user_id}. ###")
                return jsonify({"message": "Conta criada com sucesso!"}), 201
        except Exception as e:
            print(f"### Erro ao criar conta: {e} ###")
            return jsonify({"error": "Erro ao criar conta."}), 500
        finally:
            connection.close()
            print("### Ligação à base de dados encerrada. ###")
 
# -----------------------------
# Endpoint: Realizar Transferência
# -----------------------------
@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def manage_transactions():
    if request.method == 'GET':
        print("### Pedido recebido no endpoint /transactions [GET] ###")
        connection = connect_to_database()
        if not connection:
            return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM transactions;")
                transactions = cursor.fetchall()
                print("### Dados retornados da base de dados:", transactions)
                return jsonify(transactions)  # Retorna as transações no formato JSON
        except Exception as e:
            print(f"### Erro ao buscar transações: {e} ###")
            return jsonify({"error": "Erro ao buscar transações."}), 500
        finally:
            connection.close()
            print("### Ligação à base de dados encerrada. ###")
 
    elif request.method == 'POST':
        print("### Pedido recebido no endpoint /transactions [POST] ###")
        data = request.json
        print("### Dados recebidos:", data)
 
        if not data:
            return jsonify({"error": "Corpo da requisição está vazio!"}), 400
 
        from_account = data.get("from_account")
        to_account = data.get("to_account")
        amount = data.get("amount")
 
        if not all([from_account, to_account, amount]):
            return jsonify({"error": "Todos os campos são obrigatórios!"}), 400
 
        connection = connect_to_database()
        if not connection:
            return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
        try:
            with connection.cursor() as cursor:
                # Verifica saldo da conta de origem
                cursor.execute("SELECT balance FROM accounts WHERE account_id = %s;", (from_account,))
                result = cursor.fetchone()
                if not result or result[0] < amount:
                    print("### Erro: Saldo insuficiente ou conta inexistente. ###")
                    return jsonify({"error": "Saldo insuficiente ou conta inexistente."}), 400
 
                # Deduz saldo da conta de origem
                cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s;", (amount, from_account))
 
                # Adiciona saldo à conta de destino
                cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s;", (amount, to_account))
 
                # Regista a transação
                query = """
                INSERT INTO transactions (from_account, to_account, amount)
                VALUES (%s, %s, %s);
                """
                cursor.execute(query, (from_account, to_account, amount))
                connection.commit()
                print(f"### Transferência de {amount} realizada com sucesso de {from_account} para {to_account}. ###")
                return jsonify({"message": "Transferência realizada com sucesso!"}), 201
        except Exception as e:
            print(f"### Erro ao realizar transação: {e} ###")
            return jsonify({"error": "Erro ao realizar transação."}), 500
        finally:
            connection.close()
            print("### Ligação à base de dados encerrada. ###")


 
# -----------------------------
# Inicialização da Aplicação
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)