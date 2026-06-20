from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from werkzeug.utils import secure_filename
import json
import csv
import io

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploaded_images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_data_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'json', 'csv'}

# Database configuration - load from environment variables
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "database": os.getenv("DB_NAME", "ncdc_greengrid"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
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

    if tree:
        cur.execute("SELECT image_id, file_name, file_path FROM pa.tree_images WHERE tree_id = %s ORDER BY uploaded_at DESC", (id,))
        images = cur.fetchall()
        for image in images:
            image["file_url"] = request.host_url.rstrip('/') + '/tree-images/' + image["file_path"]
        tree["images"] = images

    cur.close()
    conn.close()
    return jsonify(tree if tree else {"error": "Tree not found"})

# 3. GET TREE IMAGE LIST
@app.route('/tree/<int:id>/images', methods=['GET'])
def get_tree_images(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT image_id, file_name, file_path FROM pa.tree_images WHERE tree_id = %s ORDER BY uploaded_at DESC", (id,))
    images = cur.fetchall()
    cur.close()
    conn.close()

    for image in images:
        image["file_url"] = request.host_url.rstrip('/') + '/tree-images/' + image["file_path"]

    return jsonify(images)

# 4. UPLOAD A TREE IMAGE
@app.route('/tree/<int:id>/image', methods=['POST'])
def upload_tree_image(id):
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    filename = secure_filename(file.filename)
    tree_folder = os.path.join(UPLOAD_FOLDER, f'tree_{id}')
    os.makedirs(tree_folder, exist_ok=True)
    save_path = os.path.join(tree_folder, filename)

    file.save(save_path)

    relative_path = os.path.relpath(save_path, app.root_path).replace('\\', '/')
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO pa.tree_images (tree_id, file_name, file_path) VALUES (%s, %s, %s)",
                    (id, filename, relative_path))
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": str(e)}), 500

    cur.close()
    conn.close()
    return jsonify({"message": "Image uploaded successfully", "file_url": request.host_url.rstrip('/') + '/tree-images/' + relative_path}), 201

# 5. Static route for uploaded images
@app.route('/tree-images/<path:filename>', methods=['GET'])
def serve_tree_image(filename):
    return send_from_directory(app.root_path, filename)

# 6. GET COMMENT HISTORY BY TREE ID (with optional 'limit' parameter)
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
# 13. BULK IMPORT JSON
@app.route('/bulk-import/json', methods=['POST'])
def bulk_import_json():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_data_file(file.filename):
        return jsonify({"error": "Invalid file type. Only JSON and CSV are allowed."}), 400

    try:
        content = file.read().decode('utf-8')
        trees_data = json.loads(content)
        
        if not isinstance(trees_data, list):
            return jsonify({"error": "JSON must be an array of tree objects"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        inserted = 0
        errors = []

        for tree in trees_data:
            try:
                tree_id = tree.get('tree_id')
                if not tree_id:
                    errors.append("Missing tree_id")
                    continue

                lat = tree.get('lat')
                lon = tree.get('lon')
                if lat is None or lon is None:
                    errors.append(f"Tree {tree_id}: missing lat/lon")
                    continue

                cur.execute("""
                    INSERT INTO pa.trees (tree_id, especie, nome_vulga, tipologia, local, morada, pap, manutencao, ocupacao, freguesia, geometry)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                    ON CONFLICT (tree_id) DO NOTHING
                """, (tree_id, tree.get('especie', ''), tree.get('nome_vulga', f"Tree {tree_id}"),
                      tree.get('tipologia', ''), tree.get('local', ''), tree.get('morada', ''),
                      tree.get('pap'), tree.get('manutencao', ''), tree.get('ocupacao', ''),
                      tree.get('freguesia', ''), lon, lat))
                inserted += 1
            except Exception as e:
                errors.append(f"Tree {tree.get('tree_id', 'unknown')}: {str(e)}")

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": f"Imported {inserted} trees", "errors": errors[:10]}), 201
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 14. BULK IMPORT CSV
@app.route('/bulk-import/csv', methods=['POST'])
def bulk_import_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_data_file(file.filename):
        return jsonify({"error": "Invalid file type. Only JSON and CSV are allowed."}), 400

    try:
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        if csv_reader.fieldnames is None:
            return jsonify({"error": "Invalid CSV format"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        inserted = 0
        errors = []

        for row in csv_reader:
            try:
                tree_id = row.get('tree_id')
                if not tree_id:
                    errors.append("Missing tree_id in row")
                    continue

                lat = row.get('lat')
                lon = row.get('lon')
                if not lat or not lon:
                    errors.append(f"Tree {tree_id}: missing lat/lon")
                    continue

                try:
                    lat = float(lat)
                    lon = float(lon)
                except ValueError:
                    errors.append(f"Tree {tree_id}: lat/lon must be numeric")
                    continue

                pap = row.get('pap')
                if pap:
                    try:
                        pap = float(pap)
                    except ValueError:
                        pap = None

                cur.execute("""
                    INSERT INTO pa.trees (tree_id, especie, nome_vulga, tipologia, local, morada, pap, manutencao, ocupacao, freguesia, geometry)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                    ON CONFLICT (tree_id) DO NOTHING
                """, (tree_id, row.get('especie', ''), row.get('nome_vulga', f"Tree {tree_id}"),
                      row.get('tipologia', ''), row.get('local', ''), row.get('morada', ''),
                      pap, row.get('manutencao', ''), row.get('ocupacao', ''),
                      row.get('freguesia', ''), lon, lat))
                inserted += 1
            except Exception as e:
                errors.append(f"Row error: {str(e)}")

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": f"Imported {inserted} trees", "errors": errors[:10]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
