-- Smart Pointer detection against C++11 or newer lang. versions!
SELECT "Yes", count(*) AS smart_pointer_detected
FROM detection_results
WHERE "detection_tool_output.cpp_version" IN ('c++11', 'c++14', 'c++17', 'c++2a') AND (
	"detection_tool_output.unique_ptr.detected" = 'yes' OR
	"detection_tool_output.shared_ptr.detected" = 'yes' OR
	"detection_tool_output.weak_ptr.detected" = 'yes' OR
	"detection_tool_output.intrusive_ptr.detected" = 'yes' OR
	"detection_tool_output.scoped_ptr.detected" = 'yes' OR
	"detection_tool_output.shared_array.detected" = 'yes' OR
	"detection_tool_output.scoped_array.detected" = 'yes'
	)
;

select "No", count(*) as smart_pointer_detected
from detection_results
where "detection_tool_output.cpp_version" in ('c++11', 'c++14', 'c++17', 'c++2a') AND (
	"detection_tool_output.unique_ptr.detected" = 'no' AND
	"detection_tool_output.shared_ptr.detected" = 'no' AND
	"detection_tool_output.weak_ptr.detected" = 'no' AND
	"detection_tool_output.intrusive_ptr.detected" = 'no' AND
	"detection_tool_output.scoped_ptr.detected" = 'no' AND
	"detection_tool_output.shared_array.detected" = 'no' AND
	"detection_tool_output.scoped_array.detected" = 'no'
	)
;
