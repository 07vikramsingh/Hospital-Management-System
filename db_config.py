import oracledb

def get_connection():
    connection = oracledb.connect(
        user="system",
        password="Vicky@2223",
        dsn="localhost:1521/FREEPDB1"
    )
    return connection
