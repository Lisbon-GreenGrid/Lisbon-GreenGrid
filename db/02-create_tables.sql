-- Table: sa.trees
DROP TABLE IF EXISTS sa.trees CASCADE;
CREATE TABLE IF NOT EXISTS sa.trees
(
    cod_sig_new INTEGER PRIMARY KEY,   -- Unique ID from the Lisbon City Council dataset
    nome_vulgar VARCHAR(255),          -- Common name
    especie_va VARCHAR(255),           -- Scientific name
    tipologia VARCHAR(100),            -- Tree type
    pap VARCHAR(50),                   -- Perimeter at breast height
    ocupacao VARCHAR(100),             -- Occupation
    local VARCHAR(255),                -- Location
    morada VARCHAR(255),               -- Address
    freg_2012 VARCHAR(100),            -- Parish name
    geometry GEOMETRY(Point, 20790)
);

-- Table: sa.maintenance
DROP TABLE IF EXISTS sa.maintenance CASCADE;
CREATE TABLE IF NOT EXISTS sa.maintenance
(
    maintenance_id SERIAL NOT NULL PRIMARY KEY, 	 	  -- Internal unique ID based on every maintenance done
    cod_sig_new INTEGER REFERENCES sa.trees(cod_sig_new), -- Links to the sa.tree table
    manutencao VARCHAR(255), 		   					  -- the authority in charge of maintenance for a tree
    operation VARCHAR(255),
    date DATE
);

-- Table: sa.parish_polygon
DROP TABLE IF EXISTS sa.parish_polygon CASCADE;
CREATE TABLE IF NOT EXISTS sa.parish_polygon
(
	id SERIAL NOT NULL PRIMARY KEY,
    freg_2012 VARCHAR(100) UNIQUE,
    geom GEOMETRY(Polygon, 20790) NOT NULL     -- Boundary shape
);

-- Table: sa.users
DROP TABLE IF EXISTS sa.users CASCADE;
CREATE TABLE IF NOT EXISTS sa.users
(
	username VARCHAR(50) NOT NULL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

-- Table: sa.comments
DROP TABLE IF EXISTS sa.comments CASCADE;
CREATE TABLE IF NOT EXISTS sa.comments
(
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    cod_sig_new INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Links the comment to a specific user
    CONSTRAINT fk_comment_user 
        FOREIGN KEY (username) 
        REFERENCES sa.users(username) 
        ON DELETE SET NULL,		-- if a user is deleted, the comment remains anonymous
        
    -- Links the comment to a specific tree
    CONSTRAINT fk_comment_tree 
        FOREIGN KEY (cod_sig_new) 
        REFERENCES sa.trees(cod_sig_new) 
        ON DELETE CASCADE		-- if a tree is deleted, comments are removed
);
