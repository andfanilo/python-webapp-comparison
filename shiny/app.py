from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

import plotly.graph_objects as go
from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_plotly  

ui.page_opts(
    title="Movie Analytics Dashboard",
    window_title="Movie Analytics",
    full_width=True,
)

selection_reactive = reactive.value() 

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

with ui.layout_columns(
    col_widths=(8, 4), 
):
    ui.input_select(
        "selected_period", 
        "Select period", 
        get_periods().to_list(),
        width="100%",
    )
    ui.input_radio_buttons(
        "selected_content_type",
        "Select Type",
        ("movie", "show"),
    )

with ui.layout_columns(gap="1rem"):
    with ui.value_box():
        @render.text
        def display_content_type():
            return f"{input.selected_content_type().capitalize()}s"
        
        @render.text
        def display_num_elements():
            n_elements = get_num_elements(
                input.selected_period(),
                input.selected_content_type(),
            )
            return n_elements


    with ui.value_box():
        "Views"

        @render.text
        def display_views():
            n_views = get_num_views(
                input.selected_period(),
                input.selected_content_type(),
            )
            return n_views
        
    with ui.value_box():
        "Hours Watched"

        @render.text
        def display_hours_watched():
            n_hours = get_hours_watch(
                input.selected_period(),
                input.selected_content_type(),
            )
            return n_hours

with ui.layout_column_wrap():

    @render_plotly
    def display_velocity():
        fig = plot_velocity_plotly(
            input.selected_period(),
            input.selected_content_type(),
        )
        fig.update_layout(
            template="plotly_white",
        )
        w = go.FigureWidget(fig.data, fig.layout)
        w.data[0].on_selection(on_point_selection) 
        w.data[0].on_deselect(on_deselect) 
        return w

def on_point_selection(trace, points, state):
    selection_reactive.set(points)

def on_deselect(trace, points, state): 
    selection_reactive.set(points) 

@render.code
def selection_info():
    return str(selection_reactive.get())