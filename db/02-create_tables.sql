-- Table: sa.trees
DROP TABLE IF EXISTS sa.trees;
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
