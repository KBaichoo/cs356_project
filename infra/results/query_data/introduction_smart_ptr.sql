create table empty_years (empty_year integer);
insert into empty_years values
    (2005),
    (2006),
    (2007),
    (2008),
    (2009),
    (2010),
    (2011),
    (2012),
    (2013),
    (2014),
    (2015),
    (2016),
    (2017),
    (2018),
    (2019);

select
    empty_year,
    case when count is null then 0 else count end
from
empty_years
LEFT JOIN (
     select
         case
             when unique_ptr <= shared_ptr and unique_ptr <= weak_ptr then unique_ptr
             when shared_ptr <= unique_ptr and shared_ptr <= weak_ptr then shared_ptr
             else weak_ptr
         end as introduction_year,
         count(*) as count
     from (
          select
             case when unique_ptr is null then 3000 else unique_ptr end as unique_ptr,
             case when shared_ptr is null then 3000 else shared_ptr end as shared_ptr,
             case when weak_ptr is null then 3000 else weak_ptr end as weak_ptr
          from (
               select
                  cast(substr([git_bisection_data.features.unique_ptr.timestamp], 1, 4) as decimal) as unique_ptr,
                  cast(substr([git_bisection_data.features.shared_ptr.timestamp], 1, 4) as decimal) as shared_ptr,
                  cast(substr([git_bisection_data.features.weak_ptr.timestamp], 1, 4) as decimal) as weak_ptr
               from detection_results
               where coalesce(unique_ptr, shared_ptr, weak_ptr) is not null
          )
     )
     group by introduction_year
) as introduction_years
on introduction_year = empty_year
order by empty_year asc;

drop table empty_years;
