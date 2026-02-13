-- Table: pa.trees
DROP TABLE IF EXISTS pa.trees CASCADE;
CREATE TABLE IF NOT EXISTS pa.trees
(
    tree_id INTEGER PRIMARY KEY,   	   
    nome_vulga VARCHAR(255),          
    especie VARCHAR(255),              
    tipologia VARCHAR(100),            
    pap NUMERIC(10, 2),
	manutencao VARCHAR(100),
    ocupacao VARCHAR(100),             
    local VARCHAR(255),                
    morada VARCHAR(255),               
    freguesia VARCHAR(100),            
    geom GEOMETRY(Point, 4326)
);	

-- Table: pa.operations
DROP TABLE IF EXISTS pa.operations CASCADE;
CREATE TABLE IF NOT EXISTS pa.operations
(
    op_code INTEGER PRIMARY KEY,			-- The tree operation code
	op_description VARCHAR(255) NOT NULL	-- The description of the operation done
);

-- SEED DATA: Pre-defined operation types
INSERT INTO pa.operations (op_code, op_description) 
VALUES
(1, 'Pruning (Poda)'),
(2, 'Pest Control (Controle de Pragas)'),
(3, 'Fertilization (Adubação)'),
(4, 'Visual Inspection (Inspeção Visual)'),
(5, 'Removal (Remoção)'),
(6, 'Planting (Plantação)')
ON CONFLICT (op_code) DO NOTHING;

-- Table: pa.maintenance
DROP TABLE IF EXISTS pa.maintenance CASCADE;
CREATE TABLE IF NOT EXISTS pa.maintenance
(
    maintenance_id SERIAL PRIMARY KEY, 	 	  		 					  -- Internal unique ID based on every maintenance done
    tree_id INTEGER REFERENCES pa.trees(tree_id) ON DELETE CASCADE, 	  -- Links to the pa.tree table
    op_code INTEGER REFERENCES pa.operations(op_code),					  -- Links to the pa.operations table
    maint_date DATE NOT NULL											  -- Date of maintenance operation
);

-- Table: pa.parish
DROP TABLE IF EXISTS pa.parish CASCADE;
CREATE TABLE IF NOT EXISTS pa.parish
( 
	id VARCHAR(100) PRIMARY KEY,  		  -- geopackage name (dtmnfr)
    freguesia VARCHAR(100) UNIQUE,			  -- parish name
    geom GEOMETRY(Polygon, 4326) NOT NULL     -- Boundary shape
);

-- Table: pa.users
DROP TABLE IF EXISTS pa.users CASCADE;
CREATE TABLE IF NOT EXISTS pa.users
(
	username VARCHAR(50) NOT NULL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

-- Table: pa.comments
DROP TABLE IF EXISTS pa.comments CASCADE;
CREATE TABLE IF NOT EXISTS pa.comments
(
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    tree_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Links the comment to a specific user
    CONSTRAINT fk_comment_user 
        FOREIGN KEY (username) 
        REFERENCES pa.users(username) 
        ON DELETE SET NULL,		-- if a user is deleted, the comment remains anonymous
        
    -- Links the comment to a specific tree
    CONSTRAINT fk_comment_tree 
        FOREIGN KEY (tree_id) 
        REFERENCES pa.trees(tree_id) 
        ON DELETE CASCADE		-- if a tree is deleted, comments are removed
);
