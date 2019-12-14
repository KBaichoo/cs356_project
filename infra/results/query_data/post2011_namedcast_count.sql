SELECT "Yes", count(*) AS named_cast_detected_count
FROM detection_results
WHERE ("detection_tool_output.dynamic_cast.detected" = 'yes' OR
	"detection_tool_output.static_cast.detected" = 'yes' OR
	"detection_tool_output.reinterpret_cast.detected" = 'yes' OR
	"detection_tool_output.const_cast.detected" = 'yes'
	)
	AND (
		creation_date like '2012%' OR
		creation_date like '2013%' OR
		creation_date like '2014%' OR
		creation_date like '2015%' OR
		creation_date like '2016%'
	)
	
;

SELECT "No", count(*) AS named_cast_detected_count
FROM detection_results
WHERE ("detection_tool_output.dynamic_cast.detected" = 'no' AND
	"detection_tool_output.static_cast.detected" = 'no' AND
	"detection_tool_output.reinterpret_cast.detected" = 'no' AND
	"detection_tool_output.const_cast.detected" = 'no'
	)
		AND (
		creation_date like '2012%' OR
		creation_date like '2013%' OR
		creation_date like '2014%' OR
		creation_date like '2015%' OR
		creation_date like '2016%'
	)
;
