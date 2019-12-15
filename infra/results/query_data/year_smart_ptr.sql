select
    t1.creation_year, cast(detection_count as float) / total_count
from (
     select
         substr(creation_date, 1, 4) as creation_year,
         count(*) as detection_count
     from detection_results
     where
         ([detection_tool_output.scoped_array.detected] = 'yes' or
          [detection_tool_output.intrusive_ptr.detected] = 'yes' or
          [detection_tool_output.weak_ptr.detected] = 'yes' or
          [detection_tool_output.scoped_ptr.detected] = 'yes' or
          [detection_tool_output.shared_array.detected] = 'yes' or
          [detection_tool_output.shared_ptr.detected] = 'yes' or
          [detection_tool_output.unique_ptr.occurrences] = 'yes') and
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
