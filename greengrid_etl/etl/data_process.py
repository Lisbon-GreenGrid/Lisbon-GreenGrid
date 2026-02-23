# Import required modules and libraries
from .logs import die, info
from .config import read_config
import requests
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
import re

# Extract database info from the configuration file
config = read_config("./config/00.yml")
username= config["database"]["username"]
password= config["database"]["password"]
host= config["database"]["host"]
port= config["database"]["port"]
database= config["database"]["database"]


# ------------------------------------
# -------Download Data Function-------

def download_data(url: str, fname: str) -> None:
    """
    Download data from a given URL and save it to a local file.

    This function performs an HTTP GET request to fetch the content from the 
    specified URL and writes it to a local file in binary mode. If an error 
    occurs during the download or file writing, the function calls `die()` 
    with the exception message.

    Args:
        url (str): The URL of the data to download.
        fname (str): The local filename (including path) where the downloaded 
            data will be saved.
    Returns:
        None

    Raises:
        Exception: Any exception encountered during the HTTP request or file 
            write operation is propagated via the `die()` function.

    """
    try:
        r = requests.get(url, allow_redirects=True)
        with open(fname, "wb") as f:
            f.write(r.content)
    except Exception as e:
        die(f"{e}")


# ------------------------------------
# --------Read GeoJSON Function-------

def read_geojson(fname: str,) -> gpd.GeoDataFrame:
    """
    Read a GeoJSON file into a GeoPandas GeoDataFrame.

    This function loads a GeoJSON file from disk and returns it
    as a GeoDataFrame. If the file cannot be read or is invalid,
    the function will terminate execution via the `die` handler.

    Args:
        fname (str): Path to the GeoJSON file to read.

    Return:
        gpd.GeoDataFrame: A GeoPandas GeoDataFrame containing the features from the file.

    Raises:
        SystemExit: If reading the GeoJSON file fails, the `die` function is called
        and the program exits with an error message.
    """
    try:
        gdf = gpd.read_file(fname)
    except Exception as e:
        die(f"read_geojson: {e}")
    return gdf


# ------------------------------------
# -------Write GeoJSON Function-------

def write_geojson(gdf: gpd.GeoDataFrame, fname: str) -> None:
    """
    Writes a GeoPandas GeoDataFrame to a GeoJSON file.

    This function serializes the provided GeoDataFrame into a GeoJSON
    format file on disk. If the write operation fails, the function
    logs the error and terminates execution via the `die` function.

    Args:
        gdf (gpd.GeoDataFrame): The GeoDataFrame to write to disk.
        fname (str): The full file path (including filename) where
            the GeoJSON should be saved.

    Raises:
        SystemExit: If an exception occurs during the file write,
            the function calls `die()` and exits the program.

    Example:
        >>> import geopandas as gpd
        >>> gdf = gpd.read_file("input.csv")
        >>> write_geojson(gdf, "output.geojson")
    """
    try:
        gdf.to_file(
            fname,
            driver="GeoJSON",
        )
    except Exception as e:
        die(f"write_geojson: {e}")
        

# ------------------------------------
# -------Load Shapefile Function------

def load_shapefile(fname: str, config: dict):
     """
    Load a Shapefile into a PostgreSQL/PostGIS table.

    This function reads a Shapefile using GeoPandas, transforms its coordinate
    reference system to EPSG:4326, and loads the data into the 
    "pa.parish" table in the configured PostgreSQL/PostGIS database.
    Existing data in the table will be replaced.

    Args:
        fname (str): Path to the Shapefile (.shp) to load.
        config (dict): Configuration dictionary containing database connection
            parameters.

    Raises:
        Exception: If reading the file, transforming, or loading into the
            database fails. Errors are logged before being raised.
            
    """
    try:
        info("Starting shapefile load into 'parish' table.")
        gdf = gpd.read_file(fname)

        # Transform shapefile data (similar to trees)
        gdf = gdf.to_crs('EPSG:4326')

        # Establish connection and load to database
        engine = create_engine(
           f"postgresql://{username}:{password}@{host}:{port}/{database}"
        )
        with engine.begin() as connection:
            gdf.to_postgis(
                name="parish",
                con=connection,
                schema="pa",
                if_exists="replace",
                index=False,
            )

        info("Parish shapefile loaded successfully.")
        info(f"Loaded {len(gdf)} records into 'parish' table.")

    except Exception as e:
        die(f"Error loading shapefile into 'parish' table: {e}")
        raise


# ------------------------------------
# ------Normalize Column Function-----

def normalize_column_name(column_name: str) -> str:
    """
    Normalize a column name to be PostgreSQL-compatible.

    This function converts the column name to lowercase, replaces 
    whitespace with underscores, and removes any non-alphanumeric 
    characters, ensuring the name is safe for use in PostgreSQL tables.

    Args:
        column_name (str): The original column name to normalize.

    Returns:
        str: A normalized column name compatible with PostgreSQL.
    
    Example:
        >>> normalize_column_name("User Name!")
        'user_name'
    """
    column_name = column_name.lower()   # Convert to lowercase
    column_name = re.sub(r"\s+", "_", column_name) # Replace any whitespace (spaces, tabs, etc.) with underscores
    column_name = re.sub(r"[^\w]", "", column_name) # Remove any character that is not a letter, number, or underscore
    return column_name
