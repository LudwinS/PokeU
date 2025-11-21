#Funcion para conectar con la base de datos
def connect_to_database(server_name :str, db_name :str, user_name :str, password :str):
     import pyodbc

     # ---Creacion de las variables de la conexion.---
     server = server_name
     username = user_name
     password = password
     database = db_name

     # ---Creacion de la conexion a la base de datos.---
     try:
          connexion = pyodbc.connect(
               f"DRIVER={{ODBC Driver 17 for SQL Server}};"
               f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
          )
          
          print(f"Conexion exitosa al server {server}, en la base de datos {database}")
     except Exception as e:
          print("ocurrio un error al conectarse, error:")
          print(f"\n{e}")
     finally:
          return 

connect_to_database(
     "localhost",
     "PokeU",
     "PokeU",
     "JKL_PokeU"
)