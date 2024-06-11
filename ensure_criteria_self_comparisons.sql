-- FUNCTION: public.ensure_criteria_self_comparisons()

-- DROP FUNCTION IF EXISTS public.ensure_criteria_self_comparisons();

CREATE OR REPLACE FUNCTION public.ensure_criteria_self_comparisons(
	)
    RETURNS void
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$

BEGIN
 	

    INSERT INTO criteria_comparisons (criteria1_id, criteria2_id, value)
SELECT id, id, 1 FROM criteria
ON CONFLICT DO NOTHING;
  
END;
$BODY$;

ALTER FUNCTION public.ensure_criteria_self_comparisons()
    OWNER TO postgres;
