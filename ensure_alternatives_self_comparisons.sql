-- FUNCTION: public.ensure_alternatives_self_comparisons(text)

-- DROP FUNCTION IF EXISTS public.ensure_alternatives_self_comparisons(text);

CREATE OR REPLACE FUNCTION public.ensure_alternatives_self_comparisons(
	criteria_name text)
    RETURNS void
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    input_criteria_id INT;
BEGIN
    BEGIN
        input_criteria_id := CAST(criteria_name AS INT);
    EXCEPTION WHEN invalid_text_representation THEN
        -- If input is not an integer, treat it as a criteria name
        SELECT id INTO input_criteria_id FROM criteria WHERE name = criteria_name;
        
        -- Raise an exception if the criteria name is not found
        IF input_criteria_id IS NULL THEN
            RAISE EXCEPTION 'Criteria "%" not found', criteria_name;
        END IF;
    END;

    -- Insert self-comparisons
    INSERT INTO alternative_comparisons (alternative1_id, alternative2_id, criteria_id, value)
    SELECT id, id, input_criteria_id, 1
    FROM alternatives
    CROSS JOIN (SELECT DISTINCT criteria_id FROM alternative_comparisons WHERE criteria_id = input_criteria_id) AS c
    ON CONFLICT DO NOTHING;

	-- RAISE NOTICE 'self comparisons was done successfuly'; 

	 
END;
$BODY$;

ALTER FUNCTION public.ensure_alternatives_self_comparisons(text)
    OWNER TO postgres;
