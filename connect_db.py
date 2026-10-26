import os
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

try:
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "securebank_analytics")
    )

    if connection.is_connected():
        print("MySQL Connection Successful!")
        print("Database: securebank_analytics")

        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")

        print("\nTables in database:")
        for table in cursor.fetchall():
            print(table[0])

        cursor.close()
        connection.close()
        print("\nDatabase connection closed successfully.")

except mysql.connector.Error as error:
    print("MySQL Connection Failed!")
    print(error)