from flask import Flask, request, jsonify, session
from functools import wraps
from flask_cors import CORS
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import cross_origin
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "chave-secreta-para-sessao"  # Muda para algo mais seguro em produção
app.permanent_session_lifetime = timedelta(minutes=30)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}}, supports_credentials=True)
 
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
        print(f"### Sessão ativa: {session.get('user_id')} ###") 
        if 'user_id' not in session:  # Verifica se há um `user_id` na sessão
            return jsonify({"error": "Autenticação necessária!"}), 401
        return func(*args, **kwargs)  # Executa a função original se o utilizador estiver autenticado
    return wrapper


# Endpoint para login
@app.route('/login', methods=['POST'])
@cross_origin(supports_credentials=True)
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
                session['user_id'] = user[0]  # Guarda a sessão
                print(f"### Sessão Criada: user_id={session['user_id']} ###")  # Log claro da sessão
                return jsonify({"message": "Login bem-sucedido!"}), 200
            else:
                return jsonify({"error": "Email ou password inválidos!"}), 401
    finally:
        connection.close()
 
# -----------------------------
# Endpoint: Logout
# -----------------------------

@app.route('/logout', methods=['POST'])
@cross_origin(supports_credentials=True)
def logout():
    session.clear()  # Remove todas as informações da sessão
    return jsonify({"message": "Logout realizado com sucesso!"}), 200

# -----------------------------
# Endpoint: Criar Utilizador
# -----------------------------
@app.route('/users', methods=['POST'])
@cross_origin(supports_credentials=True)
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
@cross_origin(supports_credentials=True)
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
# Endpoint: Realizar Transferência
# -----------------------------
@app.route('/transactions', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
@login_required
def manage_transactions():
    # Obter o ID do utilizador autenticado
    user_id = session['user_id']

 
    # Método GET: Obter o histórico de transações do utilizador logado
    if request.method == 'GET':
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
 
    # Método POST: Realizar uma nova transferência
    elif request.method == 'POST':
        # Garantir que o corpo da requisição é JSON
        if not request.is_json:
            return jsonify({"error": "Requisição deve conter JSON válido."}), 415
 
        # Obter dados da requisição
        data = request.get_json()
        to_iban = data.get("to_iban")
        amount = data.get("amount")
 
        # Validar os campos obrigatórios
        if not all([to_iban, amount]):
            return jsonify({"error": "Todos os campos são obrigatórios!"}), 400
 
        # Conectar à base de dados
        connection = connect_to_database()
        if not connection:
            return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
        try:
            with connection.cursor() as cursor:
                # Verificar o saldo do utilizador logado
                cursor.execute("SELECT balance FROM users WHERE user_id = %s;", (user_id,))
                user_balance = cursor.fetchone()
 
                if not user_balance or user_balance[0] < float(amount):
                    return jsonify({"error": "Saldo insuficiente."}), 400
 
                # Atualizar saldo do utilizador logado
                cursor.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s;", (amount, user_id))
 
                # Registar a transação
                cursor.execute("""
                    INSERT INTO transactions (user_id, to_iban, amount) 
                    VALUES (%s, %s, %s);
                """, (user_id, to_iban, amount))
 
                # Commit para salvar as alterações
                connection.commit()
 
                print(f"### Transferência de {amount} realizada com sucesso para IBAN {to_iban}. ###")
                return jsonify({"message": "Transferência realizada com sucesso!"}), 201
 
        except Exception as e:
            # Em caso de erro, desfaz as alterações
            connection.rollback()
            print(f"### Erro ao realizar transação: {e} ###")
            return jsonify({"error": "Erro ao realizar transação."}), 500
 
        finally:
            # Fechar a conexão com a base de dados
            connection.close()



@app.route('/deposits', methods=['POST'])
@cross_origin(supports_credentials=True)
@login_required
def deposit():
    data = request.get_json()
    amount = data.get("amount")
    user_id = session['user_id']
 
    if not amount or float(amount) <= 0:
        return jsonify({"error": "O montante do depósito deve ser maior que zero."}), 400
 
    connection = connect_to_database()
    if not connection:
        return jsonify({"error": "Erro ao conectar à base de dados."}), 500
 
    try:
        with connection.cursor() as cursor:
            # Atualizar saldo do utilizador
            cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s;", (amount, user_id))
            # Registar transação
            cursor.execute("""
                INSERT INTO transactions (user_id, to_iban, amount)
                VALUES (%s, %s, %s);
            """, (user_id, 'Depósito', amount))
            connection.commit()
            return jsonify({"message": "Depósito realizado com sucesso!"}), 201
    except Exception as e:
        connection.rollback()
        print(f"Erro ao processar depósito: {e}")
        return jsonify({"error": "Erro ao processar depósito."}), 500
    finally:
        connection.close()


 
# -----------------------------
# Inicialização da Aplicação
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)