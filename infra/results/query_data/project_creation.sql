create table empty_years (empty_year integer);
insert into empty_years values
    (1996),
    (1997),
    (1998),
    (1999),
    (2000),
    (2001),
    (2002),
    (2003),
    (2004),
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
    (2016);

select
    empty_year,
    case when count is null then 0 else count end
from
empty_years
LEFT JOIN (
     select
         cast(substr([creation_date], 1, 4) as decimal) as creation_year,
         count(*) as count
     from detection_results
     where creation_year is not null
     group by creation_year
)
on creation_year = empty_year
order by empty_year asc;

drop table empty_years;
