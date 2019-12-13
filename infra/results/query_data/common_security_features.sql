select "Smart Pointer Points", SUM(smart_ptr_detected) from (
select package_name,
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

select "Named Cast Points", SUM(named_cast_detected) from (
select package_name,
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

select "Fortified Source Points", SUM(fortified_source) from (
select package_name,
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

select "Stack Protector Points", SUM(stack_protector) from (
select package_name,
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

select "PIE Points", SUM(PIE) from (
select package_name,
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

select "RO-Relocation Points", SUM(ro_relocation) from (
select package_name,
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

select "Immediate Binding Points", SUM(immediate_binding) from (
select package_name,
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
