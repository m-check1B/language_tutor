from sqlalchemy import create_engine, text

# Connection string for local development
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/language_tutor"

def test_connection():
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Successfully connected to database!")
            
    except Exception as e:
        print("❌ Failed to connect to database:")
        print(e)

if __name__ == "__main__":
    test_connection()
