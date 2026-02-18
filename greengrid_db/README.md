# 🌳Lisbon-GreenGrid: Database Architecture

This directory contains the SQL implementation for the Lisbon-GreenGrid urban forestry management system. The database is built on PostgreSQL with the PostGIS extension to handle spatial data for the trees in Lisbon.

# 🏗️ The Staging-to-Production (SA/PA) Pattern

We utilize a Medallion Architecture (Staging and Production layers) to ensure data integrity:

SA (Staging Area): Where raw data from the Lisbon City Council website land first.

PA (Production Area): The "clean" schema that feeds the web map frontend.

# 📄 File Descriptions

`00-create_db.sql`: Creates the physical database container on the PostgreSQL server. Standardizes the database name (`lisbon_greengrid`) and sets the default encoding to `UTF-8` to support Portuguese special characters.

`01-create_schemas.sql`: Establishes the sa (Staging) and pa (Production) schemas, and enables the PostGIS extension.
The sa and pa schemas ensure a clean separation between raw data imports and the final application tables.

`02-create_sa_tables.sql`: Defines tables that match the structure of tress data source (Lisbon Open Data API). It contains the sa.trees table which allows the ETL process to land data.

`03-create_pa_tables.sql`: This defines the final, optimized schema for the Lisbon-GreenGrid web app.

Implements Primary Keys and Foreign Keys to link trees to their respective parishes.

Enforces data integrity (e.g., ensuring tree_id is unique and geometry is in SRID 4326).

`04-create_indexes.sql`: Enhances performance optimization by creating Spatial and B-tree indexes.

Spatial Indexes (GIST): Implemented on all 'geometry' columns to allow the web map to query thousands of trees in milliseconds.

B-Tree Indexes: Applied to frequently searched attributes like 'freguesia' and 'especie' to speed up filtering on the frontend.

`05-create_triggers.sql`: This implements the Procedural Logic (PL/pgSQL) that bridges the Staging Area (`sa`) and the Production Area (`pa`). It contains the `AFTER INSERT` trigger that detects new trees landing in the staging table and automatically "migrates" them to the production table.

`06-data.sql`: This populates the users, maintenance, and comments tables with synthetic data

*`Note`: This file should be executed after the ETL process is complete to ensure that foreign key relationships (linking maintenance tasks to specific trees) are valid*

`07-queries.sql`: Contains the SQL logic that the **Flask API** backend will eventually use to fetch data for the web map. It also helps troubleshoot spatial joins, ensuring trees are correctly associated with their respective parishes.

`create_db.py`: A Python automation script that handles the execution of `01-create_schemas`, `02-create_sa_tables`, `03-create_pa_tables`, `04-create_indexes`, and `05-create_triggers` SQL files, accordingly.

# 🚀 Execution Procedure

To set up the database from scratch, follow this specific order to respect data dependencies and constraints:

1. **Database Initialization**
Run `00-create_db.sql` manually in pgAdmin while connected to the default postgres database. This creates the lisbon_greengrid container.

2. **Automated Architecture Setup**
Run the Python automation script to build the schemas, tables, and triggers:

```bash
python create_db.py
```
3. **Data Ingestion (ETL)**
Run the Python ETL Script ([`main.py`](https://github.com/Lisbon-GreenGrid/Lisbon-GreenGrid/blob/main/greengrid_etl/main.py)).

The data will land in `sa.trees`.

The `05-create_triggers` logic will automatically migrate the data into `pa.trees`.

4. **Mock Data & Validation**
Once the trees are loaded, populate the related tables and verify the API logic:

- Run `06-data.sql` to add users and maintenance records.

- Use `07-queries.sql` to verify the spatial joins and data counts.

# 🛠️ Technical Stack

`Database`: PostgreSQL 16+

`Spatial Extension`: PostGIS 3.4+

`Language`: Python 3.x

`Coordinate Reference System`: WGS '84 (EPSG:4326)

*`Troubleshooting`: If the production table (pa.trees) is empty after the ETL, ensure the Python script is using `if_exists="append"` and that a `TRUNCATE` command was issued to preserve the triggers.*