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

    df = df.with_columns(
        pl.col("available_globally").replace("Yes", 1).replace("No", 0),
    ).with_columns(
        pl.col("views").fill_null(0),
        pl.col("hours_viewed").fill_null(0),
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


def get_num_movies(period: str = "2025Jan-Jun"):
    n_movies = (
        _data.filter(
            pl.col("type") == "movie",
            pl.col("report") == period,
        )
        .unique(pl.col("title"))
        .height
    )
    return n_movies


def get_num_shows(period: str = "2025Jan-Jun"):
    n_shows = (
        _data.filter(
            pl.col("type") == "show",
            pl.col("report") == period,
        )
        .unique(pl.col("title"))
        .height
    )
    return n_shows


def get_num_views(period: str = "2025Jan-Jun"):
    n_views = f"{
        (
            _data.filter(
                pl.col('report') == period,
            )
            .get_column('views')
            .sum()
            / 1_000_000_000
        ):.1f} B"
    return n_views


def get_hours_watch(period: str = "2025Jan-Jun"):
    n_views = f"{
        (
            _data.filter(
                pl.col('report') == period,
            )
            .get_column('hours_viewed')
            .sum()
            / 1_000_000_000
        ):.1f} B"
    return n_views


def plot_top_show_hours(period: str = "2025Jan-Jun"):
    max_char_limit = 25
    top_15_shows = (
        _data.filter(
            pl.col("report") == period,
        )
        .with_columns(
            pl.col("title")
            .map_elements(
                lambda s: (s[:max_char_limit] + "...")
                if len(s) > max_char_limit
                else s,
                return_dtype=pl.String,
            )
            .alias("truncated_title"),
        )
        .sort(
            "hours_viewed",
            descending=True,
        )
        .head(15)
    )

    fig = px.bar(
        top_15_shows,
        x="hours_viewed",
        y="truncated_title",
        orientation="h",
        title="Top 10 Shows by Hours Watch",
        labels={"hours_viewed": "Hours Watched", "truncated_title": "Show Title"},
        hover_name="title",
        height=550,
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
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
