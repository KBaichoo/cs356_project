SELECT "Yes", count(*) AS named_cast_detected_count
FROM detection_results
WHERE ("detection_tool_output.dynamic_cast.detected" = 'yes' OR
	"detection_tool_output.static_cast.detected" = 'yes' OR
	"detection_tool_output.reinterpret_cast.detected" = 'yes' OR
	"detection_tool_output.const_cast.detected" = 'yes'
	)
;

SELECT "No", count(*) AS named_cast_detected_count
FROM detection_results
WHERE ("detection_tool_output.dynamic_cast.detected" = 'no' AND
	"detection_tool_output.static_cast.detected" = 'no' AND
	"detection_tool_output.reinterpret_cast.detected" = 'no' AND
	"detection_tool_output.const_cast.detected" = 'no'
	)
;
