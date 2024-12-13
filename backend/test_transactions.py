from db_connection import connect_to_database
from models.transactions import transfer_funds
 
if __name__ == "__main__":
    connection = connect_to_database()
    print(connection)
 
    if connection:
        print("Ligação ao MySQL estabelecida para testes.")
 
        # Testar a transferência de fundos
        try:
            transfer_funds(
                connection,
                from_account=1,  # Certifica-te de que esta conta existe na tabela accounts
                to_account=2,    # Certifica-te de que esta conta existe na tabela accounts
                amount=50.0      # Define uma quantia para transferir
            )
            print("Teste de transferência de fundos: SUCESSO")
        except Exception as e:
            print(f"Teste de transferência de fundos: FALHA - {e}")
        finally:
            # Fechar a conexão no final, garantindo que seja encerrada
            connection.close()
            print("Conexão encerrada.")
    else:
        print("Falha na ligação ao MySQL para testes.")