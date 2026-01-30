# Urban Tree Inventory & Maintenance Management System

## 1. Introduction

Urban trees play a crucial role in improving air quality, mitigating urban heat, and enhancing the quality of life in cities. Municipal governments and urban planners often maintain detailed inventories of trees to monitor their condition and plan maintenance activities.

This project implements an **Urban Tree Inventory & Maintenance Management System** that stores, manages, and exposes information about urban trees through a relational spatial database and a RESTful API.

The system is designed to be **simple, robust, and compliant with all course requirements**, while demonstrating practical usage of:

* Extract, Transform, Load (ETL) pipelines
* PostgreSQL with PostGIS
* CRUD operations
* Python-based REST APIs

---

## 2. Project Objectives

The main objectives of this project are:

* To design a relational spatial database for managing urban tree data
* To build an independent ETL module that loads open urban tree data into the database
* To expose database operations through a RESTful API
* To support full Create, Read, Update, and Delete (CRUD) operations
* To demonstrate spatial querying using PostGIS

---

## 3. System Architecture

The system follows a clear and modular architecture:

```
Open Data (CSV / GeoJSON)
        ↓
      ETL (Python)
        ↓
PostgreSQL + PostGIS
        ↓
   REST API (Python)
```

Each component is independent and can be executed or tested separately.

---

## 4. Dataset

The project uses **open-access urban tree datasets**, typically provided by:

* Municipal open data portals
* OpenStreetMap exports

The datasets include geographic coordinates, species information, and basic tree attributes. All datasets used are open source and free to use.

---

## 5. Database Design

The database is implemented in **PostgreSQL with the PostGIS extension** and follows a relational model.

### 5.1 Main Tables

| Table Name           | Description                                  | Spatial Data |
| -------------------- | -------------------------------------------- | ------------ |
| `trees`              | Individual urban trees and their locations   | POINT        |
| `species`            | Reference table for tree species             | No           |
| `health_inspections` | Tree health assessment records               | No           |
| `maintenance_events` | Maintenance actions (pruning, removal, etc.) | No           |
| `districts`          | Administrative districts of the city         | POLYGON      |

This design satisfies the requirement of **at least five entities**, including **spatial data**.

### 5.2 Core Table: `trees`

Key attributes:

* `tree_id` (Primary Key)
* `species_id` (Foreign Key)
* `district_id` (Foreign Key)
* `planting_date`
* `height_m`
* `geom` (POINT geometry, SRID 4326)

---

## 6. ETL Module

### 6.1 Purpose

The ETL module is responsible for extracting raw tree data, transforming it into a clean and consistent format, and loading it into the PostgreSQL/PostGIS database.

### 6.2 Execution

The ETL runs independently using a single command:

```bash
python etl/load_trees.py
```

### 6.3 ETL Workflow

1. Extract tree data from CSV or GeoJSON files
2. Clean and normalize species names
3. Validate geographic coordinates
4. Convert coordinates into PostGIS geometry objects
5. Insert unique species into the `species` table
6. Insert tree records into the `trees` table

---

## 7. CRUD Operations

The project supports full CRUD functionality:

* **Create** new tree records
* **Read** existing tree information
* **Update** tree attributes and maintenance records
* **Delete** obsolete or removed trees

CRUD operations are exposed through the API and executed against the relational database.

---

## 8. API Module

### 8.1 Technology Stack

* Python
* FastAPI or Flask
* psycopg2 or SQLAlchemy

### 8.2 Available Endpoints

| Method | Endpoint                        | Description                       |
| ------ | ------------------------------- | --------------------------------- |
| GET    | `/trees`                        | Retrieve all trees                |
| GET    | `/trees/{id}`                   | Retrieve a tree by ID             |
| POST   | `/trees`                        | Insert a new tree                 |
| PUT    | `/trees/{id}`                   | Update a tree                     |
| DELETE | `/trees/{id}`                   | Delete a tree                     |
| GET    | `/trees/near?lat=&lon=&radius=` | Find nearby trees (spatial query) |

The spatial query endpoint demonstrates the use of PostGIS for distance-based searches.

---

## 9. Project Structure

```
urban-tree-inventory/
├── etl/
│   ├── load_trees.py
│   └── README.md
├── api/
│   ├── main.py
│   ├── routes/
│   └── README.md
├── db/
│   ├── schema.sql
│   └── seed.sql
├── environment.yml
└── README.md
```

---

## 10. Installation & Setup

1. Create and activate the Conda environment:

   ```bash
   conda create -n gps_python_intro
   conda activate gps_python_intro
   ```

2. Install dependencies using the provided `environment.yml` file.

3. Ensure PostgreSQL and PostGIS are installed and running.

4. Create the database and enable PostGIS.

---

## 11. Results and Demonstration

The system successfully:

* Loads open urban tree data using the ETL pipeline
* Stores spatial data in PostGIS
* Exposes CRUD operations via a REST API
* Performs spatial queries to locate nearby trees

The project can be demonstrated using Postman and optionally visualized in QGIS.

---

## 12. Conclusions

This project demonstrates how ETL pipelines, relational spatial databases, and REST APIs can be combined to build a practical urban management application. The system is intentionally simple, robust, and extensible, making it suitable for real-world municipal use cases.

---

## 13. Future Work

Possible future improvements include:

* Web-based map visualization (Leaflet)
* Authentication and user roles
* Advanced spatial analytics
* Automated data updates

---

## 14. Authors

*Group members to be listed here*
