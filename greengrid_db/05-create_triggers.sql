-- To move trees data from sa to pa
CREATE OR REPLACE FUNCTION sa.insert_trees_in_pa() -- starts the operation in the staging area
RETURNS TRIGGER
AS
$$
BEGIN
	-- Check if it exists in production
    IF NOT EXISTS (SELECT 1 FROM pa.trees WHERE tree_id = new.tree_id) THEN
		INSERT INTO pa.trees (
	    	tree_id, nome_vulga, especie, tipologia, pap,
			manutencao, ocupacao, local, morada, freguesia, geometry
		)
		VALUES (
			new.tree_id,   	   
	    	new.nome_vulga,          
	    	new.especie,              
	    	new.tipologia,            
	    	new.pap,
			new.manutencao,
	    	new.ocupacao,             
	    	new.local,                
	    	new.morada,               
	    	new.freguesia,            
	    	new.geometry
		);
	ELSE
		-- If it exists, update the record
		UPDATE pa.trees SET
        	pap = new.pap,
            manutencao = new.manutencao,
            ocupacao = new.ocupacao
        WHERE tree_id = new.tree_id;
	END IF;
	RETURN NEW;
END;
$$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS insert_trees_in_pa ON sa.trees;

CREATE TRIGGER insert_trees_in_pa
AFTER INSERT ON sa.trees
FOR EACH ROW 
EXECUTE FUNCTION sa.insert_trees_in_pa();

