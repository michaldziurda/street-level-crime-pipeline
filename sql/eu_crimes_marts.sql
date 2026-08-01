SET client_encoding = 'UTF8';


-- Total crimes per category in selected country
select "iccs", round(sum(crime_count),0) as "crime_count"
from eu_crime_staging_view
where "country" = 'FR'
group by "iccs", "country"
order by "crime_count" desc
;

-- Hottest countries per year
WITH ranked_countries AS (
    SELECT 
        year, 
        country, 
        SUM(crime_count) AS total_crime_count,
        ROW_NUMBER() OVER (
            PARTITION BY year 
            ORDER BY SUM(crime_count) DESC
        ) AS rn
    FROM eu_crime_staging_view
    WHERE crime_count IS NOT NULL
      AND crime_count != 'NaN'
    GROUP BY year, country
)
SELECT 
    year,
    country, 
    round(total_crime_count,0)
FROM ranked_countries
WHERE rn <= 3
ORDER BY year DESC, rn ASC
;

-- Select country over years
select "year", sum("crime_count")
from eu_crime_staging_view
where "country" = 'FR'
group by "year"
;