import pymysql


def connect_to_database():
    try:
        connection = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='BiaNatixis9624',
        database='bank_simulation'
        )

        if connection:
            print("Conexão com o MySQL bem-sucedida!")

        return connection
 
        # Criar um cursor para executar consultas
        #cursor = connection.cursor()
 
        # Exemplo de consulta SQL
        #cursor.execute("SELECT * FROM users LIMIT 10;")
       
        # Obter os resultados
        #resultados = cursor.fetchall()
 
        # Mostrar os resultados
        #for linha in resultados:
         #   print(linha)
    except pymysql.MySQLError as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None