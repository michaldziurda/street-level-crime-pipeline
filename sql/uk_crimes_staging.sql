SET client_encoding = 'UTF8';

create or replace view uk_crime_stg_view as
select "persistent_id", "month", "region", "category", "street_name", "outcome_status_category",
    case 
        when "outcome_status_category" = 'Action to be taken by another organisation' then 'Solved'
        when "outcome_status_category" = 'Awaiting court outcome' then 'Solved'
        when "outcome_status_category" = 'Formal action is not in the public interest' then 'Unsolved'
        when "outcome_status_category" = 'Further action is not in the public interest' then 'Unsolved'
        when "outcome_status_category" = 'Further investigation is not in the public interest' then 'Unsolved'
        when "outcome_status_category" = 'Investigation complete; no suspect identified' then 'Unsolved'
        when "outcome_status_category" = 'Local resolution' then 'Solved'
        when "outcome_status_category" = 'NaN' then 'Unsolved'
        when "outcome_status_category" = 'Offender given a caution' then 'Solved'
        when "outcome_status_category" = 'Offender given a drugs possession warning' then 'Solved'
        when "outcome_status_category" = 'Offender given penalty notice' then 'Solved'
        when "outcome_status_category" = 'Status update unavailable' then 'Unsolved'
        when "outcome_status_category" = 'Suspect charged as part of another case' then 'Solved'
        when "outcome_status_category" = 'Unable to prosecute suspect' then 'Unsolved'
        when "outcome_status_category" = 'Under investigation' then 'Unsolved'
        else 'Unsolved'
    end as "outcome_simplified"
from db.uk_crime_data;