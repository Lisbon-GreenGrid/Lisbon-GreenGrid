--To validate maintenance date
CREATE OR REPLACE FUNCTION pa.fn_check_maint_date()
RETURNS TRIGGER
AS
$$
BEGIN
    IF NEW.maint_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Maintenance date cannot be in the future!';
    END IF;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_validate_maint_date
BEFORE INSERT
ON pa.maintenance
FOR EACH ROW
EXECUTE FUNCTION pa.fn_check_maint_date();