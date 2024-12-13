def transfer_funds(connection, from_account, to_account, amount):
    cursor = connection.cursor()
 
    # Verificar saldo
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (from_account,))
    from_balance = cursor.fetchone()[0]
    if from_balance < amount:
        print("Saldo insuficiente!")
        return
 
    # Atualizar saldos
    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, from_account))
    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, to_account))
 
    # Registar transação
    query = """
    INSERT INTO transactions (from_account, to_account, amount)
    VALUES (%s, %s, %s);
    """
    cursor.execute(query, (from_account, to_account, amount))
    connection.commit()
    print("Transferência realizada com sucesso.")