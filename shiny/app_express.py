from python_webapp_comparison import get_data
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_shows
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_detail_per_titles
from python_webapp_comparison import plot_velocity

import plotly.graph_objects as go
import polars as pl
from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_widget  

df = get_data()

ui.page_opts(
    title="Movie Analytics Dashboard",
    window_title="Movie Analytics",
    full_width=True,
)

click_reactive = reactive.value() 

def on_bar_selection(trace, points, state): 
    click_reactive.set() 

with ui.layout_columns(
    col_widths=(4, 8), 
    gap="1rem",
    class_="align-items-end"
):
    ui.input_text("name", label=None)

    @render.text
    def greeting():
        name = input.name()
        if not name:
            return "Enter your name"
        else:
            return f"Hello {name}!"
        
ui.input_select(
    "selected_period", 
    "Select period", 
    get_periods().to_list(),
    width="100%",
)

with ui.layout_columns(gap="1rem", col_widths=(3, 3, 3, 3)):
    with ui.card():
        ui.p("Movies")

        @render.ui
        def display_num_movies():
            return ui.p(
                get_num_elements(input.selected_period()),
                class_="h2",
            )

    with ui.card():
        ui.p("Shows")

        @render.ui
        def display_num_shows():
            return ui.p(
                get_num_shows(input.selected_period()),
                class_="h2",
            )

    with ui.card():
        ui.p("Views")

        @render.ui
        def display_num_views():
            return ui.p(
                get_num_views(input.selected_period()),
                class_="h2",
            )

    with ui.card():
        ui.p("Hours Watched")

        @render.ui
        def display_hours_watch():
            return ui.p(
                get_hours_watch(input.selected_period()),
                class_="h2",
            )

with ui.layout_column_wrap():

    @render_widget
    def display_top_show_hours():
        fig = plot_velocity(input.selected_period())
        w = go.FigureWidget(fig.data, fig.layout)
        return w

@render.data_frame
def display_data():
    return df.filter(pl.col("report") == input.selected_period())