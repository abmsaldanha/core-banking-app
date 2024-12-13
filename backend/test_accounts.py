from db_connection import connect_to_database
from models.accounts import create_account
 
if __name__ == "__main__":
    connection = connect_to_database()
    print(connection)
 
    if connection:
        print("Ligação ao MySQL estabelecida para testes.")
 
        # Testar a criação de uma conta
        try:
            create_account(
                connection,
                user_id=1,  # Certifica-te de que este user_id existe na tabela users
                initial_balance=500.0
            )
            print("Teste de criação de conta: SUCESSO")
        except Exception as e:
            print(f"Teste de criação de conta: FALHA - {e}")
        finally:
            # Fechar a conexão no final, garantindo que seja encerrada
            connection.close()
            print("Conexão encerrada.")
    else:
        print("Falha na ligação ao MySQL para testes.")