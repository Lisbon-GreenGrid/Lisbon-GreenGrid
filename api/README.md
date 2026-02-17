This documentation provides a comprehensive overview of the Lisbon GreenGrid API, a specialized RESTful service designed for urban forest management. Developed using Flask and PostGIS, the system facilitates the management of spatial and attribute data for trees located within the municipality of Lisbon.



## Technical Architecture

The system utilizes a Python-based Flask framework to interface with a PostgreSQL database. Spatial capabilities are provided by the PostGIS extension, allowing for geographic coordinate storage and proximity-based queries using the ETRS89 / Portugal TM06 (interpreted here as WGS 84, EPSG:4326) coordinate system.

Tech Stack:
* **Backend: Flask 3.x
* Database: PostgreSQL 15+ with PostGIS 3.x
* Database Adapter: Psycopg2 (RealDictCursor)
* Spatial Functions: ST_AsGeoJSON, ST_DWithin, ST_MakePoint



## Installation and Deployment

1. Database Initialization

Execute the SQL scripts located in the `/greengrid_db` directory in the following order:

1. Schema Definition: Establishes the `pa` schema and associated tables.
2. Seed Data: Populates the `pa.operations` lookup table.
3. Dummy Data: Optional script to populate the database for testing purposes.

2. Environment Configuration

```bash
# Windows
conda create -n greengrid_api_venv

conda activate greengrid_api_venv

# Dependencies
conda install --file requirements.txt

```

3. Execution

Run the application via the Python interpreter:

```bash
python api/api.py

```

The service defaults to `http://127.0.0.1:5000`.



## API Reference

## Tree Management

| Method | Endpoint | Description |
| GET | `/trees` | Returns a collection of all trees with GeoJSON geometry. |
| GET | `/tree/<id>` | Returns detailed attributes for a specific tree ID. |
| POST | `/tree` | Creates a new tree record. Requires JSON with coordinates. |
| PUT | `/tree/<id>` | Updates non-spatial attributes of an existing tree. |
| DELETE | `/tree/<id>` | Permanently removes a tree record and associated maintenance logs. |

## Maintenance and Operations

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/tree/<id>/maintenance` | Retrieves the maintenance history, including officer and observations. |
| POST | `/tree/<id>/maintenance` | Records a new maintenance event (linked to op_code). |

## Spatial and Filter Queries

| Method | Endpoint | Description |
| GET | `/trees/near` | Proximity search. Params: `lat`, `lon`, `radius` (in meters). |
| GET | `/trees/freguesia/<name>` | Case-insensitive search by Lisbon parish name. |
| GET | `/trees/species/<name>` | Search by botanical or common species name. |



## Testing Protocol (Postman)

To ensure consistent testing across development environments, use the following configuration:

1. Base URL Variable: Define `{{base_url}}` as `http://127.0.0.1:5000`.
2. Headers: Ensure `Content-Type: application/json` is set for all POST and PUT requests.
3. Spatial Example:
* URL: `{{base_url}}/trees/near?lat=38.7137&lon=-9.1594&radius=500`



## Directory Structure

* /api: Contains `api.py` (application entry point).
* /greengrid_db: SQL scripts for schema management and data persistence.
* /greengrid_web: Static frontend assets for the web interface.
