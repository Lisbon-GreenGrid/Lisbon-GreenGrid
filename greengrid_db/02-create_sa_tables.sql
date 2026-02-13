-- Table: sa.trees
DROP TABLE IF EXISTS sa.trees CASCADE;
CREATE TABLE IF NOT EXISTS sa.trees
(
    tree_id INTEGER PRIMARY KEY,   	   -- Unique ID from the Lisbon City Council dataset
    nome_vulga VARCHAR(255),          -- Common name
    especie VARCHAR(255),              -- Scientific name
    tipologia VARCHAR(100),            -- Tree type
    pap NUMERIC(10, 2),                -- Perimeter at breast height (to 2 decimal places)
	manutencao VARCHAR(100),		   -- Authority in charge of its maintenance
    ocupacao VARCHAR(100),             -- Occupation
    local VARCHAR(255),                -- Location
    morada VARCHAR(255),               -- Address
    freguesia VARCHAR(100),            -- Parish name
    geom GEOMETRY(Point, 4326)
);