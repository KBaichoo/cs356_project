select
    t1.creation_year, cast(detection_count as float) / total_count
from (
     select
         substr(creation_date, 1, 4) as creation_year,
         count(*) as detection_count
     from detection_results
     where
         ([detection_tool_output.const_cast.detected] = 'yes' or
          [detection_tool_output.reinterpret_cast.detected] = 'yes' or
          [detection_tool_output.static_cast.detected] = 'yes' or
          [detection_tool_output.dynamic_cast.detected] = 'yes') and
         creation_year is not null
     group by creation_year
     order by creation_year
) as t1
join (
     select
         substr(creation_date, 1, 4) as creation_year,
         count(*) as total_count
     from detection_results
     where
         creation_year is not null
     group by creation_year
     order by creation_year
) t2 on t1.creation_year = t2.creation_year
order by t1.creation_year;
