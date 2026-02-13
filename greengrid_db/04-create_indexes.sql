-- These will allow the map to zoom and find trees or parishes instantly
CREATE INDEX IF NOT EXISTS idx_trees_geom 
    ON pa.trees USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_parish_geom 
    ON pa.parish USING GIST (geom);


-- These will help access the pa.maintenance and pa.comments tables quickly
CREATE INDEX IF NOT EXISTS idx_maint_tree_id 
    ON pa.maintenance (tree_id);

CREATE INDEX IF NOT EXISTS idx_comm_tree_id 
    ON pa.comments (tree_id);


-- These will help with text-based searches or filters
CREATE INDEX IF NOT EXISTS idx_trees_freguesia 
    ON pa.trees (freguesia);

CREATE INDEX IF NOT EXISTS idx_trees_especie 
    ON pa.trees (especie);