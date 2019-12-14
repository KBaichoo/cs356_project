select
    julianday(introduction_year) - julianday(creation_date) as diff
from (
     select
         creation_date,
         case
             when unique_ptr <= shared_ptr and unique_ptr <= weak_ptr then unique_ptr
             when shared_ptr <= unique_ptr and shared_ptr <= weak_ptr then shared_ptr
             else weak_ptr
         end as introduction_year
     from (
          select
             creation_date,
             case when unique_ptr is null then '3000-01-01' else unique_ptr end as unique_ptr,
             case when shared_ptr is null then '3000-01-01' else shared_ptr end as shared_ptr,
             case when weak_ptr is null then '3000-01-01' else weak_ptr end as weak_ptr
          from (
               select
                  creation_date,
                  [git_bisection_data.features.unique_ptr.timestamp] as unique_ptr,
                  [git_bisection_data.features.shared_ptr.timestamp] as shared_ptr,
                  [git_bisection_data.features.weak_ptr.timestamp] as weak_ptr
               from detection_results
               where coalesce(unique_ptr, shared_ptr, weak_ptr) is not null and
                     creation_date is not null
          )
     )
)
where diff > 0
order by diff;
