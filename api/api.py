from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# Database configuration based on your setup
DB_CONFIG = {
    "database": "lisbon_greengrid",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# 1. GET ALL TREES
@app.route('/trees', methods=['GET'])
def get_all_trees():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT *, ST_AsGeoJSON(geometry) as geometry FROM pa.trees")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

# 2. GET TREE DETAILS BY ID
@app.route('/tree/<int:id>', methods=['GET'])
def get_tree_details(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT *, ST_AsGeoJSON(geometry) as geometry 
        FROM pa.trees 
        WHERE tree_id = %s
    """, (id,))
    tree = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(tree if tree else {"error": "Tree not found"})

# 3. GET COMMENT HISTORY BY TREE ID (with optional 'limit' parameter)
@app.route('/tree/<int:id>/comments', methods=['GET'])
def get_comment_history(id):
    # default limit is 10 if not provided
    limit = request.args.get('limit', default=10, type=int)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT username, comment, created_at 
        FROM pa.comments 
        WHERE tree_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
    """, (id, limit))
    comments = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(comments)

# 4. GET MAINTENANCE HISTORY BY TREE ID (with optional 'limit' parameter)
@app.route('/tree/<int:id>/maintenance', methods=['GET'])
def get_maintenance_history(id):
    # default limit is 5 if not provided
    limit = request.args.get('limit', default=5, type=int)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.maint_date, o.op_description, m.observation, m.officer, t.manutencao AS maintenance_authority
        FROM pa.maintenance m
        JOIN pa.operations o ON m.op_code = o.op_code
        JOIN pa.trees t ON m.tree_id = t.tree_id
        WHERE m.tree_id = %s 
        ORDER BY m.maint_date DESC
        LIMIT %s
    """, (id, limit))
    history = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(history)

# 5. DELETE A TREE
@app.route('/tree/<int:id>', methods=['DELETE'])
def delete_tree(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM pa.trees WHERE tree_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": f"Tree {id} and its associated records deleted."})

# 6. EDIT TREE DETAILS
@app.route('/tree/<int:id>', methods=['PUT'])
def edit_tree(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Check if the tree exists first
        cur.execute("SELECT tree_id FROM pa.trees WHERE tree_id = %s", (id,))
        if cur.fetchone() is None:
            return jsonify({"error": f"Tree ID {id} does not exist. Cannot update."}), 404

        # 2. Proceed with the update if it exists
        cur.execute("""
            UPDATE pa.trees 
            SET nome_vulga = %s, especie = %s, tipologia = %s, local = %s, morada = %s, pap = %s, manutencao = %s, ocupacao = %s, freguesia = %s
            WHERE tree_id = %s
        """, (data.get('nome_vulga'), data.get('especie'), data.get('tipologia'), 
              data.get('local'), data.get('morada'), data.get('pap'), data.get('manutencao'), 
              data.get('ocupacao'), data.get('freguesia'), id))
        
        conn.commit()
        return jsonify({"message": f"Tree {id} updated successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# 7. ADD A NEW COMMENT
@app.route('/tree/<int:id>/comment', methods=['POST'])
def add_comment(id):
    data = request.json
    # Validation: Ensuring required fields are present
    if not data.get('username') or not data.get('comment'):
        return jsonify({"error": "Missing username or comment text"}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO pa.comments (username, tree_id, comment) 
            VALUES (%s, %s, %s)
        """, (data['username'], id, data['comment']))
        
        conn.commit()
        return jsonify({"message": "Comment added successfully"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# 8. ADD NEW MAINTENANCE STATUS
@app.route('/tree/<int:id>/maintenance', methods=['POST'])
def add_maintenance(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO pa.maintenance (tree_id, op_code, observation, officer, maint_date) 
            VALUES (%s, %s, %s, %s, %s)
        """, (id, data['op_code'], data.get('observation', ''), data.get('officer', ''), data['maint_date']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    return jsonify({"message": "Maintenance record added"})

# 9. GET TREES WITHIN A FREGUESIA
@app.route('/trees/freguesia/<string:name>', methods=['GET'])
def get_trees_by_freguesia(name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT *, ST_AsGeoJSON(geometry) as geometry FROM pa.trees WHERE freguesia ILIKE %s", (f"%{name}%",))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

# 10. GET TREES BY SPECIES
@app.route('/trees/species/<string:species>', methods=['GET'])
def get_trees_by_species(species):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT *, ST_AsGeoJSON(geometry) as geometry FROM pa.trees WHERE especie ILIKE %s", (f"%{species}%",))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

# 11. GET TREES WITHIN BUFFER (Radius in meters)
@app.route('/trees/near', methods=['GET'])
def get_trees_near():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', default=100, type=float) # in meters
    
    conn = get_db_connection()
    cur = conn.cursor()
    # Use ST_DWithin with geography for meter-based radius
    cur.execute("""
        SELECT *, ST_AsGeoJSON(geometry) as geometry 
        FROM pa.trees 
        WHERE ST_DWithin(geometry::geography, ST_MakePoint(%s, %s)::geography, %s)
    """, (lon, lat, radius))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

# 12. CREATE NEW TREE
@app.route('/tree', methods=['POST'])
def create_tree():
    data = request.json
    tree_id = data.get('tree_id')

    # Basic Validation
    if not tree_id:
        return jsonify({"error": "Missing Tree ID"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check if the Tree ID already exists
        cur.execute("SELECT tree_id FROM pa.trees WHERE tree_id = %s", (tree_id,))
        if cur.fetchone():
            return jsonify({"error": f"Tree ID {tree_id} already exists in the database."}), 409

        # If it doesn't exist, proceed with the INSERT
        cur.execute("""
            INSERT INTO pa.trees (tree_id, especie, nome_vulga, tipologia, local, morada, pap, manutencao, ocupacao, freguesia, geometry)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        """, (tree_id, data.get('especie'), data.get('nome_vulga'), data.get('tipologia'), 
              data.get('local'), data.get('morada'), data.get('pap'), data.get('manutencao'), 
              data.get('ocupacao'), data.get('freguesia'), data.get('lon'), data.get('lat')))
        
        conn.commit()
        return jsonify({"message": "Tree created successfully"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)