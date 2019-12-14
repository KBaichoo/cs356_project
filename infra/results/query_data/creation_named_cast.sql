select
    julianday(introduction_year) - julianday(creation_date) as diff
from (
     select
         creation_date,
         case
             when reinterpret_cast <= const_cast and
                  reinterpret_cast <= static_cast and
                  reinterpret_cast <= dynamic_cast then reinterpret_cast
             when const_cast <= reinterpret_cast and
                  const_cast <= static_cast and
                  const_cast <= dynamic_cast then const_cast
             when static_cast <= reinterpret_cast and
                  static_cast <= const_cast and
                  static_cast <= dynamic_cast then static_cast
             else dynamic_cast
         end as introduction_year
     from (
          select
             creation_date,
             case when reinterpret_cast is null then '3000-01-01' else reinterpret_cast end as reinterpret_cast,
             case when const_cast is null then '3000-01-01' else const_cast end as const_cast,
             case when static_cast is null then '3000-01-01' else static_cast end as static_cast,
             case when dynamic_cast is null then '3000-01-01' else dynamic_cast end as dynamic_cast
          from (
               select
                  creation_date,
                  [git_bisection_data.features.reinterpret_cast.timestamp] as reinterpret_cast,
                  [git_bisection_data.features.const_cast.timestamp] as const_cast,
                  [git_bisection_data.features.static_cast.timestamp] as static_cast,
                  [git_bisection_data.features.dynamic_cast.timestamp] as dynamic_cast
               from detection_results
               where coalesce(reinterpret_cast, const_cast, static_cast, dynamic_cast) is not null and
                     creation_date is not null
          )
     )
)
where diff > 0
order by diff;
