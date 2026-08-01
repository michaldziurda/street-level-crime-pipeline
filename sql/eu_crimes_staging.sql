SET client_encoding = 'UTF8';

create or replace view eu_crime_staging_view as
select "id", "iccs", "unit", "country", "year", NULLIF("crime_count", 'NaN') as "crime_count"
from db.eu_crime_data;