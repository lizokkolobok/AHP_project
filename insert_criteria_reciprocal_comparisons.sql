-- FUNCTION: public.insert_criteria_reciprocal_comparisons()

-- DROP FUNCTION IF EXISTS public.insert_criteria_reciprocal_comparisons();

CREATE OR REPLACE FUNCTION public.insert_criteria_reciprocal_comparisons(
	)
    RETURNS void
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$

BEGIN
 	

    INSERT INTO criteria_comparisons (criteria1_id, criteria2_id, value)
SELECT criteria2_id, criteria1_id, 1/value
FROM criteria_comparisons
WHERE criteria1_id < criteria2_id;
  
END;
$BODY$;

ALTER FUNCTION public.insert_criteria_reciprocal_comparisons()
    OWNER TO postgres;
