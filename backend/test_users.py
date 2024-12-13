from db_connection import connect_to_database
from models.users import create_user

 
if __name__ == "__main__":
    connection = connect_to_database()
    print(connection)

    if connection:
        print("Ligação ao MySQL estabelecida para testes.")
 
        # Testar a criação de um utilizador
        try:
            create_user(
                connection,
                name="Joana Costa",
                email="joana.costa@email.com",
                nif="200400567",
                birth_date="2000-01-02",
                address="Rua Exemplo, 123",
                phone="913232345"
            )
            print("Teste de criação de utilizador: SUCESSO")
        except Exception as e:
            print(f"Teste de criação de utilizador: FALHA - {e}")
        
        finally:
            # Fechar a conexão no final, garantindo que seja encerrada
            connection.close()
            print("Conexão encerrada.")
    else:
        print("Falha na ligação ao MySQL para testes.")