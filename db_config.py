import mysql.connector
from mysql.connector import pooling


db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "barangay_db"
}


pool = None

def initialize_pool():
    global pool
    try:
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="barangay_pool",
            pool_size=10,
            pool_reset_session=True,
            **db_config
        )
        print("Database pool initialized successfully.")
    except mysql.connector.Error as err:
        print(f"POOL ERROR: {err}")
        pool = None

initialize_pool()


def get_db_connection():
    try:
        if pool:
            conn = pool.get_connection()
            if conn.is_connected():
                return conn

       
        print("Re-initializing pool...")
        initialize_pool()

        if pool:
            conn = pool.get_connection()
            if conn.is_connected():
                return conn

        return mysql.connector.connect(**db_config)

    except mysql.connector.Error as err:
        print(f"DB CONNECTION ERROR: {err}")
        return None

    except Exception as e:
        print(f"GENERAL DB ERROR: {e}")
        return None


def test_connection():
    conn = get_db_connection()
    if conn and conn.is_connected():
        print(" Database connection test successful!")
        conn.close()
        return True
    return False