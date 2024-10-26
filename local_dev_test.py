import psycopg2
from time import sleep

def test_db_connection(max_attempts=5):
    attempt = 0
    while attempt < max_attempts:
        try:
            # Connect to the PostgreSQL database running in Docker
            conn = psycopg2.connect(
                dbname="language_tutor",
                user="postgres",
                password="postgres",
                host="localhost",  # Using localhost since we're connecting from outside Docker
                port="5432"
            )
            
            # Create a cursor
            cur = conn.cursor()
            
            # Execute a simple test query
            cur.execute('SELECT version();')
            
            # Fetch the result
            version = cur.fetchone()
            print("Successfully connected to the database!")
            print(f"PostgreSQL version: {version[0]}")
            
            # Close communication with the database
            cur.close()
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            attempt += 1
            if attempt == max_attempts:
                print(f"Could not connect to the database after {max_attempts} attempts")
                print(f"Error: {e}")
                return False
            print(f"Attempt {attempt} failed. Retrying in 2 seconds...")
            sleep(2)

if __name__ == "__main__":
    print("Testing connection to Docker PostgreSQL database from local environment...")
    test_db_connection()
