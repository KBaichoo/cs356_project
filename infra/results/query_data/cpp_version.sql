select
    (case when cpp_version is null then 'unknown' else cpp_version end), count(*)
from
    (select
        (case when [detection_tool_output.cpp_version] in (null, 'none') then null
              else [detection_tool_output.cpp_version] end) as cpp_version
     from detection_results)
group by cpp_version
order by case
      when cpp_version = 'c++98' then 'c++00'
      when cpp_version is null then 'c++33'
      else cpp_version end;
