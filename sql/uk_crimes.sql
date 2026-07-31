create or replace view uk_crime_stg_view as
select "persistent_id", "month", "region", "category", "outcome_status_category"
from db.uk_crime_data;

--select month, region, count("category")
--from uk_crime_stg_view
--group by region, month;

select region, month, count("category") as crimes_commited
from uk_crime_stg_view
where region in ('London', 'Birmingham', 'Coventry')
group by region, month
order by region, month asc;


--select month, count("region")
--from uk_crime_stg_view
--group by ;