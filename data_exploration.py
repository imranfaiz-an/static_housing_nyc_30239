import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import geopandas as gpd
    import marimo as mo
    import polars as pl
    import altair as alt
    from dotenv import load_dotenv
    import requests
    import os
    import pandas as pd
    import io
    from census import Census
    from us import states
    import pyarrow

    return Census, alt, gpd, io, load_dotenv, mo, os, pd, pl, requests, states


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Loading in DCP's Housing Database Data

    [Source](https://www.nyc.gov/content/planning/pages/resources/datasets/housing-project-level)

    Our dataset has 83,739 rows in total - grouping by Job-Type we can get a sense of the breakdown.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cleaning the Data
    The Dataset includes three main categories:
    - New Building
    - Alteration
    - Demolition

    Since our main focus is the construction of housing over the years we will be dropping rows where ```Job_Type == Alteration and ClassANet == 0``` i.e., where a building was altered but there was no impact on the number of Class A housing units that were added or removed. This change brings our total rows down from around 85,000 to 64,468.
    """)
    return


@app.cell
def _(pl):
    nyc_orange = "#F68933"
    nyc_blue = "#005299"
    borough_key = {
        1: "Manhattan",
        2: "Bronx",
        3: "Brooklyn",
        4: "Queens",
        5: "Staten Island"
    }

    housing_df = pl.read_csv(
        "data/nychdb_26q2.1_csv/HousingDB_post2010.csv", 
        ignore_errors=True
        ).filter(
            ~((pl.col("Job_Type")=="Alteration") & (pl.col("ClassANet")==0)) 
        ).with_columns(
            pl.col("Boro").replace_strict(borough_key)
        )

    #housing_df.filter(pl.col("Job_Type")=="Alteration").sort(pl.col("DateLstUpd"), descending=True)
    return housing_df, nyc_blue, nyc_orange


@app.cell
def _(housing_df, pl):
    df_year = housing_df.filter(pl.col("Job_Type")=="New Building").group_by("PermitYear").len()
    return (df_year,)


@app.cell
def _(alt, df_year, pl):
    # Visualzing Distribution Over Time
    _base_chart = alt.Chart(df_year.filter(pl.col("PermitYear").is_not_null()))
    _bar = _base_chart.mark_bar(color="#F68933").encode(
        alt.X("PermitYear:O").title("Permit Issued Year").axis(labelAngle=0),
        alt.Y("len:Q").title("N"),
    ).properties(
        width=750
    )

    _bar = _bar.properties(title="New Building Construction - Permits Issued")
    _bar
    return


@app.cell
def _(housing_df, pl):
    #housing_df_new= housing_df.with_columns(pl.col("CompltYear").cast(pl.String).replace(None, "Under Construction"))
    completed_housing_df = housing_df.filter(pl.col("Job_Type")=="New Building").group_by("CompltYear").len()
    return (completed_housing_df,)


@app.cell
def _(alt, completed_housing_df, pl):
    # Visualzing Distribution Over Time
    _base_chart = alt.Chart(completed_housing_df.filter(pl.col("CompltYear").is_not_null()))
    _bar = _base_chart.mark_bar(color="#005299").encode(
        alt.X("CompltYear:O").title("New Buildings Contructed").axis(labelAngle=0),
        alt.Y("len:Q").title("N"),
    )

    _bar = _bar.properties(
        title="New Buildings - Construction Complete",
        width=600,
        height=400
    )
    _bar
    return


@app.cell
def _(alt, housing_df, pl):
    # Total Class A units added over time
    #total_units_added = 
    net_housing = housing_df.filter(pl.col("PermitYear").is_not_null()).group_by("Job_Type", "PermitYear").agg(pl.col("ClassANet").sum())

    _base_chart = alt.Chart(net_housing)
    _line_chart = _base_chart.mark_line().encode(
        alt.X("PermitYear:O").title("Year").axis(labelAngle=0),
        alt.Y("ClassANet:Q").title("Change in Housing Units"),
        alt.Color("Job_Type").title("What Drives the Change")
    ).properties(
        width=800
    )
    _line_chart
    return (net_housing,)


@app.cell
def _(alt, net_housing, nyc_orange, pl):
    # Focusing on Alterations
    _base = alt.Chart(net_housing.filter((pl.col("Job_Type")=="Alteration") & (pl.col("PermitYear") > 2010)))
    _bar_alterations = _base.mark_bar(color=nyc_orange).encode(
        alt.X("PermitYear:O").title("Year").axis(labelAngle=0),
        alt.Y("ClassANet:Q").title("Housing Added")
    ).properties(
        width=600,
        title="Total Housing Units Added Through Conversion/Alteration"
    )

    _bar_alterations
    return


@app.cell
def _(alt, net_housing, nyc_blue, nyc_orange, pl):
    net_housing_percent = net_housing.with_columns(
        (pl.col("ClassANet") / pl.col("ClassANet").sum().over("PermitYear")).alias("percent_cat")
    )

    _base = alt.Chart(net_housing_percent.filter((pl.col("Job_Type")=="Alteration") & (pl.col("PermitYear") > 2010)))

    _bar_alt_pct = _base.mark_bar(color=nyc_blue).encode(
        alt.X("PermitYear:O").title("Year").axis(labelAngle=0),
        alt.Y("percent_cat:Q").title("Percent Housing Added").axis(format='%')
    ).properties(
        width=600,
        title="Conversions/Alteration as Percent of Total New Housing Added"
    )

    _bar_text = _base.mark_text(
        text="47% through\n August 2026",
        align="center",
        dy=-22,
        lineBreak="\n",
        fontSize=12,
        fontWeight="bold",
        color=nyc_orange
    ).transform_filter(
        alt.datum.PermitYear == 2026
    ).encode(
        alt.X("PermitYear:O"),
        alt.Y("percent_cat:Q")
    )


    _bar_alt_pct + _bar_text
    return


@app.cell
def _(alt, net_housing, nyc_blue, nyc_orange, pl):
    cum_units_df = net_housing.group_by(
        "PermitYear"
        ).agg(pl.col("ClassANet").sum().alias("net_units")).sort("PermitYear").with_columns(
        pl.col("net_units").cum_sum().alias("cum_units")
        )

    _base_chart = alt.Chart(cum_units_df)
    _line_chart = _base_chart.mark_line(color=nyc_blue).encode(
        alt.X("PermitYear:O").axis(labelAngle=0),
        alt.Y("cum_units:Q").title("Cumulative Housing Units")
    ).properties(
        title="Cumulative New Housing Built From 1998-2026",
        width=1000
    )

    _bar_chart = _base_chart.mark_bar(
        color=nyc_orange,
        stroke="white"
        ).encode(
        alt.X("PermitYear:O"),
        alt.Y("net_units:Q")
    )

    _vline = alt.Chart(pl.DataFrame({"PermitYear": [2008]})).mark_rule(color="red", strokeDash=[4, 4]).encode(
        alt.X("PermitYear:O"),
    )

    _vtext = alt.Chart(pl.DataFrame({"PermitYear": [2008]})).mark_text(
        text="2008 Financial Crisis",
        align="left",
        dx=5,
        dy=-33,
    ).encode(
        alt.X("PermitYear:O")
    )

    _line_chart  + _bar_chart + _vline + _vtext
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # NYC Population Data
    """)
    return


@app.cell
def _(io, pl, requests):
    #load_dotenv("apis.env")
    #API_TOKEN = os.environ["nyc_open_portal_key"]

    URL="https://data.cityofnewyork.us/api/v3/views/xywu-7bv9/query.json"
    NYC_FIPS="https://data.ny.gov/api/v3/views/79vr-2kdi/query.json"

    resp = requests.get(URL)
    resp.raise_for_status()

    resp_fips = requests.get(NYC_FIPS)
    resp.raise_for_status()

    pop_df = pl.read_json(io.BytesIO(resp.content))
    fips_df = pl.read_json(io.BytesIO(resp_fips.content))
    return fips_df, pop_df


@app.cell
def _(pl, pop_df):
    #pop_df_clean = 
    pop_df_clean = pop_df.with_columns(pl.col("borough").str.strip_chars())
    return (pop_df_clean,)


@app.cell
def _(pl, pop_df_clean):
    pop_df_long = pop_df_clean.unpivot(
        index="borough",
        variable_name="Year",
        on=["_1950", "_1960", "_1970", "_1980", "_1990", "_2000", "_2010", "_2020", "_2030", "_2040"],
        value_name="Population"    
    ).with_columns(pl.col("Year").str.replace("_", ""))
    return (pop_df_long,)


@app.cell
def _(alt, nyc_orange, pl, pop_df_long):
    _base_chart = alt.Chart(pop_df_long)
    _line_chart = _base_chart.mark_line().encode(
        alt.X("Year:O").title("Year").axis(labelAngle=0),
        alt.Y("Population:Q"),
        alt.Color("borough").title("Borough")
    ).properties(
        width=700,
        height=500,
        title="NYC Population Growth 1950-2040"
    )

    _rect_overlay = alt.Chart(pl.DataFrame({
        "Start_Year": "2020",
        "End_Year": "2040"
        })).mark_rect(opacity=0.3, color=nyc_orange, stroke="#000000").encode(
        alt.X("Start_Year:O").title(""),
        alt.X2("End_Year:O").title("")
    )

    _rect_text = alt.Chart(pl.DataFrame(
        {
            "x": "2030"
        }
        )).mark_text(
            text="Projected Population Growth",
            dx=0,
            dy=-20,
            fontSize=10,
            fontWeight="bold",
            color="#000000"
        ).encode(alt.X("x")

    )


    _rect_overlay + _line_chart  + _rect_text
    return


@app.cell
def _(fips_df, pl):
    nyc_boroughs=["Brooklyn", "Bronx", "Manhattan", "Queens", "Staten Island"]
    fips_to_boroughs = {
        '005': 'Bronx', 
        '047': 'Brooklyn', 
        '061': 'Manhattan', 
        '081': 'Queens', 
        '085': 'Staten Island'
    }

    county_fips_code = (
        fips_df.filter(pl.col("city_name").is_in(nyc_boroughs))
            .get_column("county_fips").str.slice(-3)
            .to_list()
      )

    str(county_fips_code)[2:-2]
    return (fips_to_boroughs,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Ideas:
    - A cool thing to visualize would be how the population across the city and in boroughs has increased since 1940 and in parallel show the increase in housing units. [Resource](https://www.nyc.gov/assets/planning/download/pdf/data-maps/nyc-population/historical-population/nyc_total_hu_1940-2010.pdf)
    - Show where new housing units are being built in NYC - use lat,long columns
    """)
    return


@app.cell
def _(pl):
    _years = list(range(1940, 2030, 10))
    total_housing_units_df = pl.DataFrame(
        {"year":_years,
        "total_housing_units": [2218372, 2433465, 2758116, 2924384, 2946410, 2992169, 3200912, 3371062, 3519595]}
    )
    return (total_housing_units_df,)


@app.cell
def _(pl, pop_df_long, total_housing_units_df):
    pop_df_long_total = pop_df_long.filter(pl.col("borough")=="NYC Total").with_columns(pl.col("Year").cast(pl.Int32).alias("year"))
    pop_housing_df = pop_df_long_total.join(
        other=total_housing_units_df.filter(pl.col("year")!=1940),
        on="year",
        how="full"
    )
    return (pop_housing_df,)


@app.cell
def _(pl, pop_housing_df):
    slope = pop_housing_df.select(pl.cov("year_right", "total_housing_units") / pl.col("year_right").var()).item()
    intercept = pop_housing_df.select(pl.col("total_housing_units").mean() - slope * pl.col("year_right").mean()).item()

    slope, intercept

    pop_housing_projected_df = pop_housing_df.with_columns(
        projected=pl.col("total_housing_units").is_null(),
        total_housing_units=pl.coalesce(
            "total_housing_units",
            (pl.col("year") * slope + intercept).round().cast(pl.Int64)
        )
    ).drop("year_right")

    _continuous = pl.DataFrame({
        "year": [2020],
        "total_housing_units": [3519595],
        "Population": ["8550971"],
        "projected": [True]
    })

    pop_housing_proj_dupl_df = pl.concat([pop_housing_projected_df, _continuous.with_columns(pl.col("year").cast(pl.Int32))], how="diagonal")
    return pop_housing_proj_dupl_df, pop_housing_projected_df


@app.cell
def _(pl, pop_housing_projected_df):
    pop_housing_ratio = pop_housing_projected_df.with_columns(
        pop_housing_ratio=(pl.col("Population").cast(pl.Int32) / pl.col("total_housing_units")).round(2)
    )
    return (pop_housing_ratio,)


@app.cell
def _(alt, nyc_blue, nyc_orange, pop_housing_proj_dupl_df):
    # housing_population_df
    _base_chart = alt.Chart(pop_housing_proj_dupl_df)
    _pop_line_chart = _base_chart.mark_line(color=nyc_orange).encode(
        alt.X("year:O").title("Year").axis(labelAngle=0),
        alt.Y("Population:Q").title("N"),
    ).properties(
        height=500,
        width=500,
        title="NYC Population and Total Housing Growth Over Time"
    )

    _housing_line_chart = _base_chart.mark_line(color=nyc_blue).encode(
        alt.X("year:O"),
        alt.Y("total_housing_units:Q").title(""),
        alt.StrokeDash("projected:N").title("Linear Projection").legend(None)
    )

    _pop_label = _base_chart.mark_text(
        text="Population",
        dy=-10,
        color=nyc_blue,
        fontSize=12,
        fontWeight="bold"
    ).transform_filter(
        alt.datum.year == 2040
    ).encode(
        alt.X("year:O"),
        alt.Y("Population:Q")
    )

    _housing_label = _base_chart.mark_text(
        text="Housing",
        dy=230,
        color=nyc_orange,
        fontSize=12,
        fontWeight="bold"
    ).transform_filter(
        alt.datum.year == 1990
    ).encode(
        alt.X("year:O"),
        alt.Y("Population:Q")
    )

    _housing_projected_label = _base_chart.mark_text(
        text="Housing Projected",
        dy=245,
        dx=-5,
        color=nyc_orange,
        fontSize=12,
        fontWeight="bold"
    ).transform_filter(
        alt.datum.year == 2040
    ).encode(
        alt.X("year:O"),
        alt.Y("Population:Q")
    )


    (_pop_line_chart + _housing_line_chart + _pop_label + _housing_label + _housing_projected_label)
    return


@app.cell
def _(alt, pop_housing_ratio):
    # Pop housing ratio

    _base_chart = alt.Chart(pop_housing_ratio)
    _step_chart = _base_chart.mark_area(
        color="lightblue",
        line=True
    ).encode(
        alt.X("year:O").title("Year").axis(labelAngle=0),
        alt.Y("pop_housing_ratio").title("People / Housing Unit"),
        #alt.Color("projected").title("Projected")
    ).properties(
        title="Number of People per Housing Unit",
        width=500
    )

    _step_chart
    return


@app.cell
def _(Census, load_dotenv, os, states):
    load_dotenv("keys.env")
    CENSUS_API = os.environ["census"]
    ny_state = states.NY
    ny_fips = ny_state.fips

    census = Census(CENSUS_API, year=2024)
    return census, ny_fips


@app.cell
def _(census, fips_to_boroughs, ny_fips, pl):
    census_columns = {
        "B25001_001E": "total_housing_units",
        "B25003_002E": "total_owner_occupied",
        "B25003_003E": "total_renter_occupied"
    }

    housing_census_data = census.acs5.get(
        ["NAME"] + list(census_columns.keys()),
        geo={
            "for": "county:005,047,081,085,061",
            "in": f"state:{ny_fips}"
        }
    )

    housing_census_data = pl.DataFrame(housing_census_data).rename(census_columns).with_columns(pl.col("county").replace_strict(fips_to_boroughs))

    housing_pd_df = housing_census_data.to_pandas()
    return (housing_pd_df,)


@app.cell
def _(gpd, housing_pd_df):
    borough_nyc = gpd.read_file("https://data.cityofnewyork.us/resource/gthc-hcne.geojson")
    housing_by_borough = borough_nyc.merge(housing_pd_df, left_on="boroname", right_on="county")
    return (housing_by_borough,)


@app.cell
def _(alt, housing_by_borough):
    alt.Chart(housing_by_borough).mark_geoshape().encode(
        alt.Color("total_housing_units:Q", scale=alt.Scale(scheme="viridis", reverse=True)).title("Count of Housing Units"),
        alt.Tooltip(['boroname', 'total_housing_units'])
    ).interactive().properties(
        width=500,
        height=500,
        title = "Count of Housing Units by Borough"
    )
    return


@app.cell
def _(housing_by_borough, pd):
    housing_by_borough["area_sq_mile"] = pd.to_numeric(housing_by_borough["shape_area"]) / 27878400
    housing_by_borough["housing_units_sq_mile"] = round(housing_by_borough["total_housing_units"] / housing_by_borough["area_sq_mile"])
    return


@app.cell
def _(alt, housing_by_borough):
    alt.Chart(housing_by_borough).mark_geoshape().encode(
        alt.Color("housing_units_sq_mile:Q", scale=alt.Scale(scheme="viridis", reverse=True)).title("Housing Per Sq. Mile"),
        alt.Tooltip(['boroname', 'total_housing_units', 'housing_units_sq_mile'])
    ).interactive().properties(
        width=500,
        height=500,
        title = "Housing Units / Sq. Mile by Borough"
    )
    return


if __name__ == "__main__":
    app.run()
