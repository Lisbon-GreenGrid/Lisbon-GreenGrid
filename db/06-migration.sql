-- This maps the columns from sa.trees to pa.trees
TRUNCATE TABLE pa.trees CASCADE;
INSERT INTO pa.trees (
    tree_id,   	   
    nome_vulga,          
    especie,              
    tipologia,            
    pap,
	manutencao,
    ocupacao,             
    local,                
    morada,               
    freguesia,            
    geom
)
SELECT 
    tree_id,   	   
    nome_vulga,          
    especie,              
    tipologia,            
    pap,
	manutencao,
    ocupacao,             
    local,                
    morada,               
    freguesia,            
    geom
FROM sa.trees;

-- Verification Query (to check the count)
-- SELECT count(*) FROM pa.trees;