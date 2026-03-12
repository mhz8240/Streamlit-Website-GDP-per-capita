create index if not exists idx_gdp_country_name
on public.gdp_per_capita_wide (country_name);

create index if not exists idx_gdp_continent_name
on public.gdp_per_capita_wide (continent_name);

create index if not exists idx_gdp_country_continent
on public.gdp_per_capita_wide (country_name, continent_name);