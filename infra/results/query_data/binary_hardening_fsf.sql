select
    case
        when fsf like 'no%' then 'no'
        when fsf like '%some%' then 'some'
        when fsf like 'unknown%' then 'unknown'
        else fsf
    end
    as fsf,
    count(*)
from (
    select [detection_tool_output.fortify-source] as fsf
    from detection_results
)
where fsf is not null
group by fsf
order by
      case
        when fsf like '%some%' then 5000
        else count(*)
      end desc;
