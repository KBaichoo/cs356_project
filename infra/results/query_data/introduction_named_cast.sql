create table empty_years (empty_year integer);
insert into empty_years values
    (2000),
    (2001),
    (2002),
    (2003),
    (2004),
    (2005),
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
         end as introduction_year,
         count(*) as count
     from (
          select
             case when reinterpret_cast is null then 3000 else reinterpret_cast end as reinterpret_cast,
             case when const_cast is null then 3000 else const_cast end as const_cast,
             case when static_cast is null then 3000 else static_cast end as static_cast,
             case when dynamic_cast is null then 3000 else dynamic_cast end as dynamic_cast
          from (
               select
                  cast(substr([git_bisection_data.features.reinterpret_cast.timestamp], 1, 4) as decimal)
                    as reinterpret_cast,
                  cast(substr([git_bisection_data.features.const_cast.timestamp], 1, 4) as decimal)
                    as const_cast,
                  cast(substr([git_bisection_data.features.static_cast.timestamp], 1, 4) as decimal)
                    as static_cast,
                  cast(substr([git_bisection_data.features.dynamic_cast.timestamp], 1, 4) as decimal)
                    as dynamic_cast
               from detection_results
               where coalesce(reinterpret_cast, const_cast, static_cast, dynamic_cast) is not null
          )
     )
     group by introduction_year
) as introduction_years
on introduction_year = empty_year
order by empty_year asc;

drop table empty_years;
