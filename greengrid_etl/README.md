# Lisbon GreenGrid ETL

Production Extract–Transform–Load (ETL) pipeline for the Lisbon GreenGrid platform.

## Overview

This package implements a modular Extract–Transform–Load (ETL) pipeline, separating configuration, data processing, database interaction, and logging concerns. It is responsible for:

- Extracting raw data in GeoJSON format
- Cleaning and transforming the dataset
- Loading structured data into a POSTGIS database
- Logging pipeline execution


## Structure
              ┌──────────────┐
              │   config/    │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │   main.py    │
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   logs.py     db_connect.py   data_process.py
                    │               │
                    │               ▼
                    │         Transform / Clean
                    │               │
                    ▼               │
               Target Database ◄────┘


## Module and Script Responsibilities

| Module                          | Description                       |
| ------------------------------- | --------------------------------- |
| `etl/__init__.py`               | Marks `etl` as a Python package and allows structured imports across modules|
| `etl/config.py`                 | Central configuration handler|
| `etl/db_connect.py`             | Database connection management and transaction control|
| `etl/data_process.py`           | data processing logic|
| `etl/logs.py`                   | Logging configuration and pipeline monitoring|
| `main.py`                       | Pipeline orchestrator|
| `config/`                       | Contains YAML configuration file|
| `data/`                         | Working data directory|
| `environment.yml`               | Defines the Conda environment required to run the ETL pipeline|
| `etl_requirements.txt/`         | Defines the required packages required to run the ETL pipeline|


## Installation and Deployment

1. ### Database Initialization

- Execute the SQL scripts located in the `/greengrid_db` directory.

2. ### Environment Configuration

- Download and install MiniForge
- Open the MiniForge Prompt

```cmd
# Windows
Method1:
conda env create --file environment.yml

conda activate etl_environment

Method2:
conda create -n "environment name"

conda activate "environment name"

cd to target directory:

conda install --file etl_requirements.txt

```

3. Execution

Run the application via the Python interpreter/VScode cmd terminal:

```cmd
python main.py

```
