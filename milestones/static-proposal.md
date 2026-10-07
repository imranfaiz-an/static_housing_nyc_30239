# Muhammad Faizan Imran

## Description

My static project will be looking at housing in New York City over the years. A recent
[article](https://www.nytimes.com/2026/08/19/nyregion/nyc-housing-shortage.html)
in New York Times said that the city currently faces a shortage of housing by
over 290,000 units and that the city would need to build 700,000 units over the
next decade to keep up with the demand. Building new housing
is also a major [agenda](https://www.nytimes.com/2026/05/26/nyregion/mamdani-housing-plan-nycha.html) by the current NYC adminsitration.

I will be working on visualizations that convey this policy problem effectively, I intend to include
visuals on the historic construction of housing in the city, it's population growth over the years and by
how much the supply has not been able to keep with with the demand. I will also have by borough and neighbordhood
analysis and will include information on the construction of affordable housing units, which some districts in
New York are [notorious](https://www.nytimes.com/2026/10/01/nyregion/nyc-affordable-housing-neighborhoods.html) for restricting
the supply of.

Lastly, I plan on bringing in the Census data on the census block or census tract level to visualize how housing shortage impacts
different racial/ethnic minority groups.


## Data Sources

### Data Source 1: Department of City Planning - DCP Housing Database

[URL](https://www.nyc.gov/content/planning/pages/resources/datasets/housing-project-level)
Size: 83,769 Rows, 66 Columns

This dataset will allow me to  track how many new housing units have been added or are under construction currently in NYC.
I plan on focusing more on rows where the column ```Job_Type == "New Building"```, to track new housing construction.

### Data Source 2: DCP - New York City Population by Borough, 1950 - 2040

[URL](https://data.cityofnewyork.us/City-Government/New-York-City-Population-by-Borough-1950-2040/xywu-7bv9/about_data)
Size: 6 Rows, 22 Columns

This dataset will allow me to bring in the past-present and future estimates for the 
population of NYC. Allowing me to trace historic housing supply-demand and make some statements about the future.

On top of population by Boroughs the city also publishes data on [Neighborhood](https://data.cityofnewyork.us/City-Government/New-York-City-Population-By-Neighborhood-Tabulatio/swpk-hqdp/about_data) and [Community Districts](https://data.cityofnewyork.us/City-Government/New-York-City-Population-By-Community-Districts/xi7c-iiu2/about_data) level,
which would allow me to do a more granular analysis if needed.

### Data Source 3: American Community Survey 2023

[URL](https://data.census.gov/table/ACSDT1Y2024.B25031?q=B25031:+Median+Gross+Rent+by+Bedrooms)
Size: The API allows data to be fetched on different levels of aggregations (state, census tract, census block etc.)

I will be bringing in the ACS data to bring in numbers on rent estimates, and get demographic level breakdowns on the 
population. The Census also publishes [Tiger shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) that I will bring in to do spatial analysis.

## Questions:

1- Is there a way to make Flowmaps using Altair. An idea for a visualization that I had was to show how
housing shortage in NYC causes people to move out using PUMS data. 


## Similar Projects:
- [Conversions](https://www.nytimes.com/2026/08/30/nyregion/nyc-conversions-analysis-pfizer.html)
