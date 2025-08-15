from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

import plotly.graph_objects as go
from shiny import reactive
from shiny.express import module, input, render, ui
from shinywidgets import render_plotly

selected_titles = reactive.value([])


@module
def card(
    input,
    output,
    session,
    reactive_title,
    static_title,
    fn_value,
    reactive_period,
    reactive_content_type,
):
    with ui.value_box():

        @render.text
        def display_title():
            return static_title or reactive_title().capitalize() + "s"

        @render.text
        def display_value():
            res = fn_value(
                reactive_period(),
                reactive_content_type(),
            )
            return res


ui.page_opts(
    window_title="Movie Analytics",
    full_width=True,
    class_="mt-4 px-5",
)

app = ui.layout_column_wrap(
    width=1,
    gap="1rem",
)

with app:
    title_row = ui.layout_column_wrap()
    greeting_row = ui.layout_columns(
        col_widths=(8, 4), gap="1rem", class_="align-items-end"
    )
    filters_row = ui.layout_columns(
        col_widths=(8, 4),
        gap="1rem",
    )
    card_row = ui.layout_columns(gap="2rem")
    chart_row = ui.layout_column_wrap()
    preview_row = ui.layout_column_wrap(width=1)


with title_row:
    ui.h1("Movie Analytics Dashboard")


with greeting_row:
    ui.input_text("name", label="Enter your name", width="100%")

    @render.text
    def greeting():
        name = input.name()
        return "Enter your name" if not name else f"Hello {name}!"


with filters_row:
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


with card_row:
    card(
        "elements_per_content",
        input.selected_content_type,
        None,
        get_num_elements,
        input.selected_period,
        input.selected_content_type,
    )
    card(
        "views",
        None,
        "Views",
        get_num_views,
        input.selected_period,
        input.selected_content_type,
    )
    card(
        "hours",
        None,
        "Hours Watched",
        get_hours_watch,
        input.selected_period,
        input.selected_content_type,
    )


with chart_row:

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
        w.data[0].on_deselect(remove_titles)
        # w.data[0].on_doubleclick(remove_titles)
        return w


def on_point_selection(trace, points, state):
    custom_data = trace.customdata
    selected_points = list(trace.selectedpoints)

    titles = [
        t for ind, l in enumerate(custom_data) for t in l if ind in selected_points
    ]
    selected_titles.set(titles)


@reactive.effect
@reactive.event(input.selected_period, input.selected_content_type, input.reset_titles)
def remove_titles():
    selected_titles.set([])


with preview_row:

    @render.data_frame
    def preview_dataframe():
        df = preview_data(
            input.selected_period(),
            input.selected_content_type(),
            selected_titles(),
        )
        return render.DataGrid(df, width="100%")

    ui.input_action_button(
        "reset_titles",
        "Reset titles",
        width="100px",
    )
