-- GET ALL TREES
SELECT *, ST_AsGeoJSON(geom) as geometry FROM pa.trees;

-- GET SPECIFIC TREE (Details + Latest Maintenance + Latest Comment)
SELECT t.*, ST_AsGeoJSON(t.geom) as geometry,
        (SELECT op_description FROM pa.maintenance m 
         JOIN pa.operations o ON m.op_code = o.op_code 
         WHERE m.tree_id = t.tree_id ORDER BY maint_date DESC LIMIT 1) as latest_maintenance,
        (SELECT comment FROM pa.comments c WHERE c.tree_id = t.tree_id ORDER BY created_at DESC LIMIT 1) as latest_comment
        FROM pa.trees t WHERE t.tree_id = 1;

-- GET COMMENT HISTORY BY TREE ID
SELECT * FROM pa.comments WHERE tree_id = 10 ORDER BY created_at DESC;

-- GET MAINTENANCE HISTORY BY TREE ID
SELECT m.maint_date, m.maint_date, o.op_description, t.manutencao AS maintenance_authority
        FROM pa.maintenance m
        JOIN pa.operations o ON m.op_code = o.op_code
        JOIN pa.trees t ON m.tree_id = t.tree_id
        WHERE m.tree_id = 10
        ORDER BY m.maint_date DESC;

-- DELETE A TREE
DELETE FROM pa.trees WHERE tree_id = 10;

-- GET TREES BY SPECIES
SELECT *, ST_AsGeoJSON(geom) as geometry FROM pa.trees WHERE especie ILIKE '%m%';

-- GET TREES WITHIN BUFFER (Radius in meters)
SELECT *, ST_AsGeoJSON(geom) as geometry 
        FROM pa.trees 
        WHERE ST_DWithin(geom::geography, ST_MakePoint(-9.1594, 38.7137)::geography, 500);



