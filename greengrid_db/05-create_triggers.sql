-- To move trees data from sa to pa
CREATE OR REPLACE FUNCTION sa.insert_trees_in_pa()
RETURNS TRIGGER
AS
$$
BEGIN
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
	    geometry
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
	    geometry
	FROM sa.trees sa
	WHERE NOT EXISTS(SELECT 1 FROM pa.trees pa WHERE pa.tree_id = sa.tree_id);
	
	
	UPDATE pa.trees AS pa SET
		pap = sa.pap,
		manutencao = sa.manutencao,
		ocupacao = sa.ocupacao
	FROM sa.trees AS sa
	WHERE sa.tree_id = pa.tree_id
		AND (pa.pap != sa.pap  OR pa.manutencao != sa.manutencao OR pa.ocupacao != sa.ocupacao);
	RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER insert_trees_in_pa
AFTER INSERT ON sa.trees
FOR EACH STATEMENT 
EXECUTE PROCEDURE sa.insert_trees_in_pa();

