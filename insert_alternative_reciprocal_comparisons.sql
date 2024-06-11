-- FUNCTION: public.insert_alternative_reciprocal_comparisons(text)

-- DROP FUNCTION IF EXISTS public.insert_alternative_reciprocal_comparisons(text);

CREATE OR REPLACE FUNCTION public.insert_alternative_reciprocal_comparisons(
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

    -- Insert reciprocal comparisons
    INSERT INTO alternative_comparisons (alternative1_id, alternative2_id, criteria_id, value)
    SELECT alternative2_id, alternative1_id, input_criteria_id, 1/value
    FROM alternative_comparisons
    WHERE alternative1_id < alternative2_id AND criteria_id = input_criteria_id
    ON CONFLICT DO NOTHING;

	RAISE NOTICE 'Insert reciprocal comparisons was done successfuly';
END;
$BODY$;

ALTER FUNCTION public.insert_alternative_reciprocal_comparisons(text)
    OWNER TO postgres;
