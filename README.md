# Lisbon_GreenGrid

## 1. Introduction

Urban trees play a crucial role in improving air quality, mitigating urban heat, and enhancing the quality of life in cities. Municipal governments and urban planners often maintain detailed inventories of trees to monitor their condition and plan maintenance activities.

Lisbon_GreenGrid is an urban tree inventory & maintenance management system. This project aims to develop a simple yet robust system for managing urban trees in a city. The system stores spatial information about trees, their species, size, location, other relevant info, and the authority responsible for maintenance. It enables city planners or maintenance teams to efficiently query, insert, update, and manage tree-related data through an API.

---

## 2. Project Objectives

The main objectives of this project are:

* To design a relational spatial database for managing urban tree data
* To build an independent ETL module that loads open urban tree data into the database
* To expose database operations through an API
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
  API (Python)
```

Each component is independent and can be executed or tested separately.

---

## 4. Dataset

The project will use **open-access urban tree datasets**, typically provided by:

* Lisbon open data portal (Portal Dados Abertos): https://dados.cm-lisboa.pt/dataset/arvoredo 
* OpenStreetMap

The datasets include geographic coordinates, species information, and basic tree attributes. All datasets proposed are open source and free to use.

---

## 5. Database Design

The database will be implemented in **PostgreSQL with the PostGIS extension** and follows a relational model.

### 5.1 Main Tables

| Table Name           | Description                                  | Spatial Data |
| -------------------- | -------------------------------------------- | ------------ |
| `trees`              | Individual urban trees and their locations   | POINT        |
| `species`            | Reference table for tree species             | No           |
| `Location Type`      | Is the tree locate in a street, road or park | No           |
| `maintenance_Authority` | Is it maintained by the JF or CML         | No           |
| `districts`          | Administrative districts of the city         | POLYGON      |


### 5.2 Core Table: `trees`

Key attributes:

* `tree_id` (Primary Key)
* `species` (Foreign Key)
* `district` (Foreign Key)
* `PAP`
* `common_name`
* `household`
* `geom` (POINT geometry, SRID 4326)

---

## 6. ETL Module

### 6.1 Purpose

The ETL module will be responsible for extracting raw tree data, transforming it into a clean and consistent format, and loading it into the PostgreSQL/PostGIS database.

### 6.2 Execution

The ETL will run independently using a single command:

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

CRUD operations will be exposed through the API and executed against the relational database.

---

## 8. API Module

### 8.1 Technology Stack

Proposed technology include:
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

The spatial query endpoint demonstrates the proposed use of PostGIS for distance-based searches.


## 9. Authors

* Christian Oluoma (20250854)
* Saba Fatima (20250858)
* Adebola Adedayo (20250853)

