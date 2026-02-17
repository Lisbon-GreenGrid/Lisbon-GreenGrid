🌳 Lisbon-GreenGrid: Database Architecture
This directory contains the SQL implementation for the Lisbon-GreenGrid urban forestry management system. The database is built on PostgreSQL with the PostGIS extension to handle spatial data for over 50,000 trees in Lisbon.

🏗️ The Staging-to-Production (SA/PA) Pattern
We utilize a Medallion Architecture (Staging and Production layers) to ensure data integrity:

SA (Staging Area): Where raw data from APIs and GeoJSON files land first.

PA (Production Area): The "clean" schema that feeds the web map frontend.

📄 File Descriptions
01-create_schemas.sql
Purpose: Environment Initialization.

Enables the PostGIS extension.

Establishes the namespaces: sa (Staging) and pa (Production).

Ensures a clean separation between raw data imports and the final application tables.

02-create_sa_tables.sql
Purpose: Raw Data Ingestion.

Defines tables that match the structure of external sources (Lisbon Open Data API).

Contains the trees_raw and parish_raw tables.

Uses flexible data types to allow the ETL process to land data before transformation.

03-create_pa_tables.sql
Purpose: Application Foundation.

Defines the final, optimized schema for the Lisbon-GreenGrid app.

Implements Primary Keys and Foreign Keys to link trees to their respective parishes.

Enforces data integrity (e.g., ensuring tree_id is unique and geom is in SRID 4326).

04-create_indexes.sql
Purpose: Performance Optimization.

Spatial Indexes (GIST): Implemented on all geom columns to allow the web map to query thousands of trees in milliseconds.

B-Tree Indexes: Applied to frequently searched attributes like freguesia and especie to speed up filtering on the frontend.
