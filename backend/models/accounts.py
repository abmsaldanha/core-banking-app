def create_account(connection, user_id, initial_balance=0):
    cursor = connection.cursor()
    query = """
    INSERT INTO accounts (user_id, balance)
    VALUES (%s, %s);
    """
    values = (user_id, initial_balance)
    cursor.execute(query, values)
    connection.commit()
    print("Conta criada com sucesso.")