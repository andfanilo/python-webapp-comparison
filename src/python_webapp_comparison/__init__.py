from datetime import date

import plotly.express as px
import polars as pl


def __load_data():
    shows = pl.read_csv(
        "data/shows.csv",
        ignore_errors=True,
    )
    movies = pl.read_csv(
        "data/movies.csv",
        ignore_errors=True,
    )

    shows = shows.with_columns(
        pl.lit("show").alias("type"),
    )
    movies = movies.with_columns(
        pl.lit("movie").alias("type"),
    )

    df = shows.vstack(movies)

    df = (
        df.with_columns(
            pl.col("report").str.replace(r"^(\d{4})([A-Za-z0-9-]+)$", r"${1} - ${2}"),
            pl.col("available_globally").replace("Yes", 1).replace("No", 0),
            pl.col("views").fill_null(0),
            pl.col("hours_viewed").fill_null(0),
        )
        .with_columns(
            pl.col("report")
            .map_elements(
                lambda r: {
                    "2025 - Jan-Jun": date(2025, 6, 30),
                    "2024 - Jul-Dec": date(2024, 12, 31),
                    "2024 - Jan-Jun": date(2024, 6, 30),
                    "2023 - Jul-Dec": date(2023, 12, 31),
                }.get(r, None),
                return_dtype=pl.Date,
            )
            .alias("last_report_date")
        )
        .with_columns(
            (
                pl.col("last_report_date")
                - pl.col("release_date").str.to_date(strict=False)
            )
            .dt.total_days()
            .alias("days_since_release"),
        )
        .with_columns(
            (pl.col("views") / pl.col("days_since_release"))
            .floor()
            .alias("mean_views_per_day"),
        )
    )

    df = (
        df.with_columns(
            # 1. Extract Hours
            pl.col("runtime")
            .str.extract(r"(\d+)H", 1)
            .cast(pl.Int64)
            .fill_null(0)
            .alias("runtime_hours"),
            # 2. Extract Minutes
            pl.col("runtime")
            .str.extract(r"(\d+)M", 1)
            .cast(pl.Int64)
            .fill_null(0)
            .alias("runtime_minutes"),
            # 3. Extract Seconds (optional, but good for completeness)
            pl.col("runtime")
            .str.extract(r"(\d+)S", 1)
            .cast(pl.Int64)
            .fill_null(0)
            .alias("runtime_seconds"),
        )
        .with_columns(
            # 4. Calculate total minutes
            (
                pl.col("runtime_hours") * 60
                + pl.col("runtime_minutes")
                + pl.col("runtime_seconds") / 60
            ).alias("runtime_minutes")
        )
        .drop(["runtime_hours", "runtime_seconds", "source"])
    )

    return df


_data = __load_data()


def get_data():
    return _data.clone()


def get_periods():
    return _data.get_column("report").unique().sort(descending=True)


def get_num_elements(period: str, content_type: str):
    n_movies = (
        _data.filter(
            pl.col("report") == period,
            pl.col("type") == content_type,
        )
        .unique(pl.col("title"))
        .height
    )
    return n_movies


def get_num_views(period: str, content_type: str):
    n_views = f"{
        (
            _data.filter(
                pl.col('report') == period,
                pl.col('type') == content_type,
            )
            .get_column('views')
            .sum()
            / 1_000_000_000
        ):.1f} B"
    return n_views


def get_hours_watch(period: str, content_type: str):
    n_views = f"{
        (
            _data.filter(
                pl.col('report') == period,
                pl.col('type') == content_type,
            )
            .get_column('hours_viewed')
            .sum()
            / 1_000_000_000
        ):.1f} B"
    return n_views


def plot_velocity(period: str, content_type: str):
    fig = px.scatter(
        _data.filter(
            pl.col("mean_views_per_day").is_not_null(),
            pl.col("report") == period,
            pl.col("type") == content_type,
        ),
        x="days_since_release",
        y="mean_views_per_day",
        title="Show Velocity",
        hover_name="title",
        labels={
            "days_since_release": "Days Since Release",
            "mean_views_per_day": "Mean Views per Day",
        },
        height=550,
    )
    fig.update_layout(
        yaxis_type="log",
    )
    return fig


def plot_detail_per_titles(titles):
    group_df = _data.filter(pl.col("title").is_in(titles))
    res = (
        group_df.group_by(pl.col("report"))
        .agg(
            pl.sum("views").alias("total_views"),
            pl.sum("hours_viewed").alias("total_watch_hours"),
        )
        .sort(
            pl.col("report"),
        )
        .unpivot(
            index="report",
            on=["total_views", "total_watch_hours"],
            variable_name="metric",
            value_name="value",
        )
    )
    if res.get_column("report").n_unique() > 1:
        fig = px.area(
            res,
            x="report",
            y="value",
            facet_row="metric",
            title="Views / Hours analytics",
            height=550,
        )
        fig.update_yaxes(matches=None)
    else:
        fig = px.bar(
            res,
            x="report",
            y="value",
            facet_row="metric",
            title="Views / Hours analytics",
            height=550,
        )
        fig.update_yaxes(matches=None)
    return fig
