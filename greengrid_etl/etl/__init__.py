"""
ETL Package Initialization

This module initializes the ETL package and exposes core functions and classes
for data processing, database operations, logging, and configuration management.

Modules Imported:
- logs: Provides logging utilities and helper functions for error, info, and completion messages.
- data_process: Handles data extraction, transformation, and loading, including reading/writing
  GeoJSON, shapefile operations, and normalization utilities.
- config: Provides functions to read and manage pipeline configuration files.
- db_connect: Provides the database controller for establishing and managing DB connections.
"""

from .logs import die, info, done, init_logger
from .data_process import write_geojson, read_geojson, load_shapefile, normalize_column_name, download_data
from .config import read_config
from .db_connect import DBController

# Initialize package-wide logger to ensure all modules log consistently
init_logger()
