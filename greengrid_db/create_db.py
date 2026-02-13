import psycopg2
import os

def build_structure():
    
    """
    Connects to the PostgreSQL database and builds the physical architecture 
    by executing a sequence of SQL files in a specific dependency order.

    Args:
        None:
        
    Returns:
        None:
    """
    # Database connection parameters
    db_params = {
        "database": "lisbon_greengrid", # Ensure this DB is already created manually on PostgreSQL
        "user": "postgres",
        "password": "postgres", # Use appropriate password
        "host": "localhost", # Change if your DB is on another server
        "port": "5432", # Default PostgreSQL port
        "options": "-c client_encoding=UTF8"
    }

    # Directory containing the SQL files
    sql_folder = r"C:\Users\Lisbon-GreenGrid\db"  # Update with your folder path
    
    # List of SQL files
    sql_files = [
        "01-create_schemas.sql",
        "02-create_sa_tables.sql",
        "03-create_pa_tables.sql",
        "04-create_indexes.sql",
        "05-create_triggers.sql"
    ]

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        print("Connected to PostgreSQL.")

        for file in sql_files:
            #Linking folder path and file name
            full_path = os.path.join(sql_folder, file)

            if os.path.exists(full_path):
                print(f"Executing: {full_path}")
                with open(full_path, 'r', encoding='utf-8') as f:
                    cur.execute(f.read())
                conn.commit()
            else:
                print(f"Warning: Could not find {full_path}")

        print("\n Database structure is ready!")

    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    build_structure()