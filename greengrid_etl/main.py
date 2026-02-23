# Import required packages and libraries
import etl as e
import argparse
import time
import pandas as pd
import sys
from datetime import datetime



DB_SCHEMA = "sa"   # For reproducibility replace with name of schema
TABLE = "trees"    # For reproducibility replace with name of table
DOWNLOAD_DIR = "data/original"  # For reproducibility replace with correct directory path
PROCESSED_DIR = "data/processed"  # For reproducibility replace with correct directory path
STATIC_DIR = "data/static"   # For reproducibility replace with correct directory path
TARGET_SRID = 4326    # For reproducibility replace with desired EPSG code.


def extraction(config: dict) -> None:
    """
    Download raw data in GEOJSON from an API into the .data/original directory.

    Args:
        config (dict): Dictionary containing:
            - "url" (str): Source API.
            - "fname" (str): Output filename.

    Raises:
        KeyError: If required configuration keys are missing.
        Exception: If the download operation fails.
    """
    e.info("EXTRACTION: START DATA EXTRACTION")
    url = config["url"]
    fname = config["fname"]
    fname = f"{DOWNLOAD_DIR}/{fname}"
    e.info("EXTRACTION: DOWNLOADING DATA")
    e.download_data(url, fname)
    e.info("EXTRACTION: COMPLETED")


def transformation(config: dict) -> None:
    """
    Execute the transformation stage of the ETL pipeline.

    This function performs data cleaning, normalization, schema alignment,
    CRS validation, and prepares a GeoDataFrame for database loading.
    The transformed dataset is written to the ./data/processed directory
    as a GeoJSON file.

    Args:
        config : dict
            Configuration dictionary containing:
            - "fname" (str): Name of the GeoJSON file to process.
            - "columns" (list[str]): Ordered list of columns to retain
              in the transformed dataset.

    Returns:
        None
            The function writes the transformed GeoDataFrame to disk and
            does not return a value.

    Raises:
        KeyError: If required keys ("fname", "columns") are missing from config.
        FileNotFoundError: If the specified input file does not exist.
        ValueError: If CRS transformation fails or required columns are missing.
    """
    
    e.info("TRANSFORMATION: START TRANSFORMATION")
    e.info("TRANSFORMATION: READING DATA")
    fname = config["fname"]
    # Read the GEOJSON file into a Geodatabase
    gdf = e.read_geojson(f"{DOWNLOAD_DIR}/{fname}")
    e.info("TRANSFORMATION: DATA READING COMPLETED")

    e.info("TRANSFORMATION: START DATA CLEANING")
    # Normalize column names for postgresql database
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
    # Ensure the geometry is taken from the geometry column
    gdf.set_geometry("geometry", inplace=True)

    # Obtain the desired columns from the configuration file
    cols = config["columns"]
    gdf = gdf[cols] # Create a geodataframe using the desired columns

    e.info("TRANSFORMATION: DATA CLEANING COMPLETED")
    
    e.info("TRANSFORMATION: SAVING TRANSFORMED DATA")

    # Write the Geodataframe into the .data/processed folder as a GEOJSON file
    e.write_geojson(gdf, fname=f"{PROCESSED_DIR}/{fname}")
    e.info("TRANSFORMATION: SAVED")
    e.info("TRANSFORMATION: COMPLETED")


def load(config: dict, chunksize: int=1000) -> None:
    """
    Executes the load phase of the ETL pipeline.
    
    This function reads the processed GeoJSON dataset and inserts it
    into the configured PostGIS trees table in the database.
    It also loads an auxiliary shapefile into the parish table in the database.

    Args:
        config : dict
            Configuration dictionary containing:
            - "fname" (str): Processed filename.
            - "database" (dict): Database connection parameters
              (host, port, user, password, database).
        chunksize : int, optional
        Number of rows inserted per batch (default: 1000).

    Returns:
        None
            The function inserts the transformed GEOJSON data into the database and
            does not return a value.
        
    Raises
        Exception: Any database or file I/O error triggers termination
        via the logging/exit handler.
    """
    try:
        fname = config["fname"]
        db = e.DBController(**config["database"])
        e.info("LOAD: READING DATA")
        gdf = e.read_geojson(f"{PROCESSED_DIR}/{fname}")
        e.info("LOAD: DATA READ")
        e.info("LOAD: INSERTING DATA INTO DATABASE")
        # Insert data into the trees table in the database
        db.insert_data(gdf, DB_SCHEMA, TABLE, chunksize=chunksize)
        # Insert the shapefile into the parish table in the database
        e.load_shapefile(fname=f"{STATIC_DIR}/lisbon_parishes.shp", config=config)
        e.done("LOAD: DONE")
    except Exception as err:
        e.die(f"LOAD: {err}")


def parse_args() -> str:
    """
    Parse command-line arguments for the Lisbon_GreenGrid application.

    This function defines and parses CLI arguments using argparse and
    returns the path to the configuration file provided by the user.
    If no configuration file is specified, a default path is used.

    Returns:
        str: Path to the configuration file to be used by the application.
    """
    parser = argparse.ArgumentParser(description="Runnning Lisbon_GreenGrid")
    parser.add_argument("--config_file", required=False, help="The configuration file", default="./config/00.yml")
    args = parser.parse_args()
    return args.config_file


def time_this_function(func, **kwargs) -> str:
    """
    Measure and report the execution time of a callable.

    Executes the provided function with the supplied keyword arguments
    and returns a formatted string containing the function name and
    total execution time in seconds.

    Args:
        func (Callable): The function to be executed and timed.
        **kwargs: Arbitrary keyword arguments passed to ``func``.

    Returns:
        str: A formatted string reporting the function name and its
        execution time in seconds (to three decimal places).

    Raises:
        Any exception raised by ``func`` is propagated to the caller.
        
    """
    import time
    t0 = time.time()
    func(**kwargs)
    t1 = time.time()
    return f"'{func.__name__}' EXECUTED IN {t1-t0:.3f} SECONDS"


def main(config_file: str) -> None:
    """
    Orchestrates the ETL pipeline: extraction, transformation, and loading of data.

    This function serves as the entry point for the ETL process. It performs the following steps in order:
    1. Reads configuration from the specified file.
    2. Executes the data extraction step and logs execution time.
    3. Executes the data transformation step and logs execution time.
    4. Executes the data loading step (with configurable chunk size) and logs execution time.

    Each ETL step is wrapped with `time_this_function` to measure execution duration and logged via the logger `e`.

    Args:
        config_file (str): Path to the configuration file used to parameterize the ETL pipeline.

    Returns:
        None

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        ValueError: If configuration is invalid or missing required parameters.
        Exception: Propagates exceptions raised by `extraction`, `transformation`, or `load` functions.
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
