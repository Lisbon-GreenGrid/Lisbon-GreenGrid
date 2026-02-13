-- 1. GET ALL TREES
SELECT *, ST_AsGeoJSON(geometry) as geometry FROM pa.trees;

-- 2. GET TREE DETAILS BY ID
SELECT *, ST_AsGeoJSON(geometry) as geometry FROM pa.trees WHERE tree_id = 1;

-- 3. GET COMMENT HISTORY BY TREE ID (with limit)
SELECT username, comment, created_at 
FROM pa.comments 
WHERE tree_id = 1 
ORDER BY created_at DESC 
LIMIT 4;

-- 4. GET MAINTENANCE HISTORY BY TREE ID (with limit)
SELECT m.maint_date, o.op_description, t.manutencao AS maintenance_authority
FROM pa.maintenance m
JOIN pa.operations o ON m.op_code = o.op_code
JOIN pa.trees t ON m.tree_id = t.tree_id
WHERE m.tree_id = 8 
ORDER BY m.maint_date DESC
LIMIT 2;

-- 5. DELETE A TREE
DELETE FROM pa.trees WHERE tree_id = 999;

-- 6. EDIT TREE DETAILS
UPDATE pa.trees 
SET nome_vulga = 'Oliveira Monumental', 
    especie = 'Olea europaea', 
    tipologia = 'Arvores de Interesse Público', 
    morada = 'Jardim da Estrela', 
    pap = 45.5 
WHERE tree_id = 1;

-- 7. ADD A NEW COMMENT
INSERT INTO pa.comments (username, tree_id, comment) 
VALUES ('nature_fan', 1, 'The shade under this olive tree is perfect for studying!');

-- 8. ADD NEW MAINTENANCE STATUS
INSERT INTO pa.maintenance (tree_id, op_code, maint_date) 
VALUES (8, 4, '2026-02-13');

-- 9. GET TREES WITHIN A FREGUESIA
SELECT *, ST_AsGeoJSON(geometry) as geometry FROM pa.trees WHERE freguesia ILIKE '%Ajuda%';

-- 10. GET TREES BY SPECIES
SELECT *, ST_AsGeoJSON(geometry) as geometry FROM pa.trees WHERE especie ILIKE '%m%';

-- 11. GET TREES WITHIN BUFFER (Radius in meters)
SELECT *, ST_AsGeoJSON(geometry) as geometry 
FROM pa.trees 
WHERE ST_DWithin(geometry::geography, ST_MakePoint(-9.1594, 38.7137)::geography, 500);

-- 12. CREATE NEW TREE
INSERT INTO pa.trees (tree_id, nome_vulga, especie, tipologia, freguesia, geometry)
VALUES (11, 'Pinheiro Manso', 'Pinus pinea', 'Isolada', 'Estrela', 
        ST_SetSRID(ST_MakePoint(-9.1601, 38.7140), 4326));
