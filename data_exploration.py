import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import altair as alt
    from dotenv import load_dotenv
    import requests
    import os
    import pandas as pd
    import io

    return alt, io, load_dotenv, mo, os, pd, pl, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Loading in the Housing Database Data

    [Source](https://www.nyc.gov/content/planning/pages/resources/datasets/housing-project-level)

    Our dataset has 83,739 rows in total - grouping by Job-Type we can get a sense of the breakdown.
    """)
    return


@app.cell
def _(pl):
    df = pl.read_csv("data/nychdb_26q2.1_csv/HousingDB_post2010.csv", ignore_errors=True).with_columns(
        pl.date(pl.col("CompltYear"), 1, 1).alias("year")
    )
    df
    return (df,)


@app.cell
def _(df):
    df.group_by("Job_Type").len() # 29,166 new constructions have been added since 2016. 
    return


@app.cell
def _(df, pl):
    df_year = df.filter(pl.col("Job_Type")=="New Building").group_by("PermitYear").len()
    df_year
    return (df_year,)


@app.cell
def _(alt, df_year, pl):
    # Visualzing Distribution Over Time
    base_chart = alt.Chart(df_year.filter(pl.col("PermitYear").is_not_null()))
    bar = base_chart.mark_bar().encode(
        alt.X("PermitYear:O"),
        alt.Y("len:Q")
    )

    bar
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # NYC Population Data
    """)
    return


@app.cell
def _(io, load_dotenv, os, pl, requests):
    load_dotenv("apis.env")
    API_TOKEN = os.environ["nyc_open_portal_key"]

    URL="https://data.cityofnewyork.us/api/v3/views/xywu-7bv9/query.json"

    resp = requests.get(URL)
    resp.raise_for_status()

    pop_df = pl.read_json(io.BytesIO(resp.content))

    return URL, pop_df


@app.cell
def _(pop_df):
    pop_df
    return


@app.cell
def _(URL, pd):
    pd.read_json(URL)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The census variable to get the total number of housing units is: B25001_001

    Other useful ones are: B25003_002 Total Owner Occupied, and B25003_003 Total Renter Occupied

    ## Ideas:
    - A cool thing to visualize would be how the population across the city and in boroughs has increased since 1940 and in parallel show the increase in housing units. [Resource](https://www.nyc.gov/assets/planning/download/pdf/data-maps/nyc-population/historical-population/nyc_total_hu_1940-2010.pdf)

    ### Pending Stuff
    - Start loading in ACS/Census data
    - Clean borough pop data above
    - The housing database has start year and complete year - for my case the start year would be better to look at.
        - Other fields to explore are: borogh, census tract/block info
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
