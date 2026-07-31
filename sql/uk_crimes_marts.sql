SET client_encoding = 'UTF8';

-- Total crimes per month in selecte aeras
select region, month, count("category") as crimes_commited
from uk_crime_stg_view
where region in ('London', 'Birmingham', 'Coventry')
group by region, month
order by region, month asc
limit 10
;

-- Breakdown of total registerd crimes by category for selected area
select "region", "category", count("persistent_id") from uk_crime_stg_view
where 1=1 and
"region" = 'London'
group by "region", "category"
limit 30
;

-- Percentage of crimes solved by category
select "category", 
    count(*) as category_count,
    round(count(*) * 100.0 / sum(count(*)) OVER (), 4) as "category_pct",
    round(count(*) filter (Where "outcome_simplified" = 'Solved') * 100. / count(*), 4) as "solve_rate"
from uk_crime_stg_view
group by "category"
order by "solve_rate" desc
;

-- Hottest streets
select "street_name", "region", 
count(*) as "crime_count"
from uk_crime_stg_view
group by "street_name", "region"
order by "crime_count" desc
limit 30
;


-- Seasonal pattern in London
SET lc_numeric = 'French_France.1252';

select "month", count(*) as crime_count
from uk_crime_stg_view
group by "month"
order by "month" asc
;