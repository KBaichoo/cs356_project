-- This is only for maintainers who have a pkg that C++11 or newer, and
-- we detected a single binary.
DROP TABLE IF EXISTS maintainer_scores;

create table maintainer_scores AS
select maintainer, (smart_ptr_detected + named_cast_detected + fortified_source + stack_protector + PIE + ro_relocation + immediate_binding) as points from (
select package_name, maintainer,
CASE
    WHEN (
	"detection_tool_output.unique_ptr.detected" = 'yes' OR
	"detection_tool_output.shared_ptr.detected" = 'yes' OR
	"detection_tool_output.weak_ptr.detected" = 'yes' OR
	"detection_tool_output.intrusive_ptr.detected" = 'yes' OR
	"detection_tool_output.scoped_ptr.detected" = 'yes' OR
	"detection_tool_output.shared_array.detected" = 'yes' OR
	"detection_tool_output.scoped_array.detected" = 'yes'
	) THEN 1
    ELSE 0
END AS smart_ptr_detected,
CASE
    WHEN "detection_tool_output.dynamic_cast.detected" = 'yes' OR "detection_tool_output.static_cast.detected" = 'yes' OR "detection_tool_output.reinterpret_cast.detected" = 'yes' OR "detection_tool_output.const_cast.detected" = 'yes' THEN 1
    ELSE 0
END AS named_cast_detected,
CASE
	WHEN "detection_tool_output.fortify-source" LIKE '%yes%' then 1
	ELSE 0
END AS fortified_source,
CASE
	WHEN "detection_tool_output.stack-protector" LIKE '%yes%' then 1
	ELSE 0
END AS stack_protector,
CASE
	WHEN "detection_tool_output.PIE" LIKE '%yes%' then 1
	ELSE 0
END AS PIE,
CASE
	WHEN "detection_tool_output.ro-relocation" LIKE '%yes%' then 1
	ELSE 0
END AS ro_relocation,
CASE
	WHEN "detection_tool_output.immediate-binding" LIKE '%yes%' then 1
	ELSE 0
END AS immediate_binding
from detection_results
where "detection_tool_output.stack-protector" is not null AND "detection_tool_output.cpp_version" in ('c++11', 'c++14', 'c++17', 'c++2a')
);

select AVG(points) as pts from maintainer_scores group by maintainer order by pts;

DROP TABLE IF EXISTS maintainer_scores;
