from .logs import die, info
import requests
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
import re


def download_data(url: str, fname: str) -> None:
    """Downloads data from URL and store it in a local file

    Args:
        url: url with location of the original data
        fname (str): the name of the data file to save locally

    Returns:
        None
    """
    try:
        r = requests.get(url, allow_redirects=True)
        with open(fname, "wb") as f:
            f.write(r.content)
    except Exception as e:
        e.die(f"{e}")


def read_geojson(fname: str,) -> gpd.DataFrame:
    """Reads a GeoJSON file into a GeoPandas dataframe

    Args:
        fname (str): the name of the GeoJSON file

    Returns:
        gpd.DataFrame: a geodataframe
    """
    try:
        gdf = gpd.read_file(fname)
    except Exception as e:
        die(f"read_geojson: {e}")
    return gdf


def write_geojson(gdf: gpd.GeoDataFrame, fname: str) -> None:
    """ Writes a GeoPandas dataframe into a GeoJSON

    Args:
        gdf (gpd.GeoDataFrame): the geodataframe
        fname (str): the file name
    """
    try:
        gdf.to_file(
            fname,
            driver="GeoJSON",
        )
    except Exception as e:
        die(f"write_geojson: {e}")


        
def load_shapefile(fname: str, config: dict):
    """
    Reads a Shapefile into and Geopandas dataframe
    Transforms the data and Load the data into the table.

    Args:
        fname (str): the file name
    """
    try:
        info("Starting shapefile load into 'parish' table.")
        gdf = gpd.read_file(fname)

        # Transform shapefile data (similar to trees)
        gdf = gdf.to_crs('EPSG:4326')
      
        engine = create_engine(
           "postgresql://postgres:20250854@localhost:5432/lisbon_greengrid"
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


def normalize_column_name(column_name: str) -> str:
    """
    Normalize column names for PostgreSQL compatibility.

    Args:
        column_name (str): the initial column name

    Return:
        column_name (str): postgresql normalized column name
    """
    column_name = column_name.lower()
    column_name = re.sub(r"\s+", "_", column_name)
    column_name = re.sub(r"[^\w]", "", column_name)
    return column_name

