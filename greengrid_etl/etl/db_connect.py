# Import required modules and libraries
from .logs import die
import sqlalchemy as sql
import geoalchemy2
import pandas as pd
import geopandas as gpd


class DBController:
    def __init__(self, host: str, port: str, database: str, username: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

    def select_data(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL SELECT query and return the results as a Pandas DataFrame.

        This method abstracts the database querying process by:
        1. Establishing a connection to the database using SQLAlchemy.
        2. Executing the provided SELECT query.
        3. Returning the results as a DataFrame.

        Args:
            query (str): The SQL SELECT query to execute.

        Returns:
            pd.DataFrame: A Pandas DataFrame containing the query results.

        Raises:
            SystemExit: If the query execution fails, the function calls `die()` with the error message.
            
        """
        try:
            con = sql.create_engine(self.uri)
            df = pd.read_sql(query, con)
        except Exception as e:
            die(f"select_data: {e}")
        return df

    
    def insert_data(self, gdf: gpd.GeoDataFrame, schema: str, table: str, chunksize: int=100) -> None:
        """
        Insert a GeoDataFrame into a PostGIS table, truncating the table beforehand.

        This function abstracts the INSERT operation for PostGIS, handling
        database connection, transaction management, and chunked insertion.
        The target table is cleared before insertion while keeping database triggers intact.

        Args:
            gdf (gpd.GeoDataFrame): The GeoDataFrame containing spatial data to insert.
            schema (str): The database schema where the table resides.
            table (str): The name of the target table.
            chunksize (int): Number of rows to insert per batch. Default is 100.

        Raises:
            Exception: If any database operation fails, the transaction is rolled back
        and the exception is raised.
        
        """
        try:
            engine = sql.create_engine(self.uri)
            with engine.connect() as con:
                tran = con.begin()
                con.execute(sql.text(f"TRUNCATE TABLE {schema}.{table} CASCADE;")) # Clears table without dropping it. Keeps the trigger alive
                gdf.to_postgis(
                    name=table, schema=schema,
                    con=con, if_exists="append", index=False,
                    chunksize=chunksize
                )
                tran.commit()
        except Exception as e:
            if 'tran' in locals():
                tran.rollback()
            die(f"{e}")
