import etl as e
import argparse
import time
import pandas as pd
import sys
from datetime import datetime



DB_SCHEMA = "sa"
TABLE = "trees"
DOWNLOAD_DIR = "data/original"
PROCESSED_DIR = "data/processed"
STATIC_DIR = "data/static"
TARGET_SRID = 4326

def extraction(config: dict) -> None:
    """ Runs extraction

        Args:
            config (dict): configuration dictionary
    """
    e.info("EXTRACTION: START DATA EXTRACTION")
    url = config["url"]
    fname = config["fname"]
    fname = f"{DOWNLOAD_DIR}/{fname}"
    e.info("EXTRACTION: DOWNLOADING DATA")
    e.download_data(url, fname)
    e.info("EXTRACTION: COMPLETED")


def transformation(config: dict) -> None:
    """Runs transformation

    Args:
        config (dict): configuration dictionary
    """
    e.info("TRANSFORMATION: START TRANSFORMATION")
    e.info("TRANSFORMATION: READING DATA")
    fname = config["fname"]
    gdf = e.read_geojson(f"{DOWNLOAD_DIR}/{fname}")
    e.info("TRANSFORMATION: DATA READING COMPLETED")

    e.info("TRANSFORMATION: START DATA CLEANING")
    # Normalize column names for postgresql
    gdf.columns = [e.normalize_column_name(col) for col in gdf.columns]

    # Ensure CRS matches that of database
    if gdf.crs is None:
        e.info("CRS not defined. Setting to EPSG:4326.")
        gdf.set_crs(epsg=TARGET_SRID, inplace=True)

    if gdf.crs.to_epsg() != 4326:
        e.info("Reprojecting to EPSG:%s.", 4326)
        gdf = gdf.to_crs(epsg=4326)

    # For specific columns, Replace empty records with a better word
    gdf["manutencao"]= gdf["manutencao"].replace("", "Não identificada")
    gdf["local"]= gdf["local"].replace("", "Não identificado")
    gdf["tipologia"]= gdf["tipologia"].replace("", "Não identificada")

    # Fill NaN with better word
    gdf["ocupacao"]= gdf["ocupacao"].fillna("Não identificada")
    gdf["local"]= gdf["local"].fillna("Não identificado")
    gdf["tipologia"]= gdf["tipologia"].fillna("Não identificada")
    gdf["nome_vulga"]= gdf["nome_vulga"].fillna("Não identificado")

    # Convert "pap" column to numeric
    gdf["pap"] = (pd.to_numeric(gdf["pap"], errors="coerce"))

    # Rename columns to match the database model
    gdf= gdf.rename(
    columns={
        "cod_sig_new" : "tree_id",
        "especie_va" : "especie",
        "freg_2012" : "freguesia",
        "geometry" : "geometry"
        }
    )
    gdf.set_geometry("geometry", inplace=True)

    cols = config["columns"]
    gdf = gdf[cols]

    e.info("TRANSFORMATION: DATA CLEANING COMPLETED")
    
    e.info("TRANSFORMATION: SAVING TRANSFORMED DATA")
    
    e.write_geojson(gdf, fname=f"{PROCESSED_DIR}/{fname}")
    e.info("TRANSFORMATION: SAVED")
    e.info("TRANSFORMATION: COMPLETED")


def load(config: dict, chunksize: int=1000) -> None:
    """Runs load

    Args:
        config (dict): configuration dictionary
        chunksize (int): the number of rows to be inserted at one time
    """
    try:
        fname = config["fname"]
        db = e.DBController(**config["database"])
        e.info("LOAD: READING DATA")
        gdf = e.read_geojson(f"{PROCESSED_DIR}/{fname}")
        e.info("LOAD: DATA READ")
        e.info("LOAD: INSERTING DATA INTO DATABASE")
        db.insert_data(gdf, DB_SCHEMA, TABLE, chunksize=chunksize)
        e.load_shapefile(fname=f"{STATIC_DIR}/lisbon_parishes.shp", config=config)
        e.done("LOAD: DONE")
    except Exception as err:
        e.die(f"LOAD: {err}")


def parse_args() -> str:
    """ Reads command line arguments

        Returns:
            the name of the configuration file
    """
    parser = argparse.ArgumentParser(description="Runnning Lisbon_GreenGrid")
    parser.add_argument("--config_file", required=False, help="The configuration file", default="./config/00.yml")
    args = parser.parse_args()
    return args.config_file


def time_this_function(func, **kwargs) -> str:
    """ Times function `func`

        Args:
            func (function): the function we want to time

        Returns:
            a string with the execution time
    """
    import time
    t0 = time.time()
    func(**kwargs)
    t1 = time.time()
    return f"'{func.__name__}' EXECUTED IN {t1-t0:.3f} SECONDS"


def main(config_file: str) -> None:
    """Main function for ETL

    Args:
        config_file (str): configuration file
    """
    config = e.read_config(config_file)
    # extraction(config)
    msg = time_this_function(extraction, config=config)
    e.info(msg)
    # transformation(config)
    msg = time_this_function(transformation, config=config)
    e.info(msg)
    # load(config, chunksize=10000)
    msg = time_this_function(load, config=config, chunksize=1000)
    e.info(msg)


if __name__ == "__main__":
    config_file = parse_args()
    main(config_file)
