select
    'Immediate binding',
    count(case when c = 'yes' then 1 end),
    count(case when c like 'no%' then 1 end)
from (
     select
         [detection_tool_output.immediate-binding] as c
     from detection_results
)

UNION ALL

select
    'Read-only relocation',
    count(case when c = 'yes' then 1 end),
    count(case when c like 'no%' then 1 end)
from (
     select
         [detection_tool_output.ro-relocation] as c
     from detection_results
)

UNION ALL

select
    'PIE',
    count(case when c = 'yes' then 1 end),
    count(case when c like 'no%' then 1 end)
from (
     select
         [detection_tool_output.PIE] as c
     from detection_results
)

UNION ALL

select
    'Stack protection',
    count(case when c = 'yes' then 1 end),
    count(case when c like 'no%' then 1 end)
from (
     select
         [detection_tool_output.stack-protector] as c
     from detection_results
);
