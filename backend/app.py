from flask import Flask, request, jsonify

from db_connection import connect_to_database

from models.users import create_user

from models.accounts import create_account

from models.transactions import transfer_funds
 
app = Flask(__name__)
 
# Endpoint para criar utilizadores

@app.route("/users", methods=["POST"])

def add_user():

    """

    Endpoint para criar utilizadores.

    """

    data = request.json

    if not data:

        return jsonify({"error": "Corpo da requisição não enviado!"}), 400
 
    name = data.get("name")

    email = data.get("email")

    if not name or not email:

        return jsonify({"error": "Nome e email são obrigatórios!"}), 400
 
    connection = connect_to_database()

    try:

        create_user(

            connection,

            name=name,

            email=email,

            nif=data.get("nif"),

            birth_date=data.get("birth_date"),

            address=data.get("address"),

            phone=data.get("phone")

        )

        return jsonify({"message": f"Utilizador {name} criado com sucesso!"}), 201

    except Exception as e:

        return jsonify({"error": str(e)}), 500

    finally:

        connection.close()
 
# Endpoint para criar contas

@app.route("/accounts", methods=["POST"])

def add_account():

    """

    Endpoint para criar contas.

    """

    data = request.json

    if not data:

        return jsonify({"error": "Corpo da requisição não enviado!"}), 400
 
    user_id = data.get("user_id")

    initial_balance = data.get("initial_balance", 0)

    if not user_id:

        return jsonify({"error": "O ID do utilizador é obrigatório!"}), 400
 
    connection = connect_to_database()

    try:

        create_account(connection, user_id=user_id, initial_balance=initial_balance)

        return jsonify({"message": f"Conta criada com sucesso para o utilizador {user_id}!"}), 201

    except Exception as e:

        return jsonify({"error": str(e)}), 500

    finally:

        connection.close()
 
# Endpoint para criar uma transação (transferência)

@app.route("/transactions/transfer", methods=["POST"])

def transfer():

    """

    Endpoint para realizar uma transferência de fundos entre contas.

    """

    data = request.json

    if not data:

        return jsonify({"error": "Corpo da requisição não enviado!"}), 400
 
    from_account = data.get("from_account")

    to_account = data.get("to_account")

    amount = data.get("amount")
 
    if not from_account or not to_account or not amount:

        return jsonify({"error": "Os campos from_account, to_account e amount são obrigatórios!"}), 400
 
    connection = connect_to_database()

    try:

        transfer_funds(connection, from_account, to_account, amount)

        return jsonify({"message": "Transferência realizada com sucesso!"}), 201

    except Exception as e:

        return jsonify({"error": str(e)}), 500

    finally:

        connection.close()
 
if __name__ == "__main__":

    app.run(debug=True)

 