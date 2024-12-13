def create_user(connection, name, email, nif, birth_date, address, phone):
    cursor = connection.cursor()
    query = """
    INSERT INTO users (name, email, nif, birth_date, address, phone)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    values = (name, email, nif, birth_date, address, phone)
    cursor.execute(query, values)
    connection.commit()
    print("Utilizador criado com sucesso.")