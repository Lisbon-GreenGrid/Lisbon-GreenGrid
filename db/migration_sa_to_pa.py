import psycopg2
import os

def run_migration():
    """
    Handles the movement of the cleaned geospatial data from the Staging schema (sa) 
    to the Production schema (pa). Also ensures the web application reads 
    from a high-performance, validated table.

    Args:
        None:
        
    Returns:
        None:
    """
    # Directory containing the SQL file
    sql_folder = r"C:\Users\Victus\Documents\GitHub\Lisbon-GreenGrid\db"  # Update with your folder path 
    migration_file = "06-migration.sql" # The migration SQL file

    db_params = {
        "database": "lisbon_greengrid", # Ensure this DB is already created manually
        "user": "postgres",
        "password": "polarIS123$", # Use appropriate password
        "host": "localhost", # Change if your DB is on another server
        "port": "5432", # Default PostgreSQL port
        "options": "-c client_encoding=UTF8"
    }

    # The full file path
    full_path = os.path.join(sql_folder, migration_file)

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        if os.path.exists(full_path):
            print(f"Starting Migration: {full_path}")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                cur.execute(f.read())
            
            # Data being moved from sa to pa
            conn.commit()
            print("Migration Complete! Data is now in Production Schema (pa).")
        else:
            print(f"Error: Migration file not found at {full_path}")

    except Exception as e:
        print(f"Migration Failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == "__main__":
    run_migration()