import plotly.graph_objects as go
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data
from shinywidgets import output_widget
from shinywidgets import render_plotly

from shiny import App
from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui


@module.ui
def card_ui():
    return ui.value_box(
        ui.output_text("display_title"),
        ui.output_text("display_value"),
    )


@module.server
def card_server(
    input,
    output,
    session,
    reactive_title,
    static_title,
    fn_value,
    reactive_period,
    reactive_content_type,
):
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


greeting_row = ui.layout_columns(
    ui.input_text("name", label=None, width="100%"),
    ui.output_text("greeting"),
    col_widths=(8, 4),
    gap="4rem",
    class_="align-items-end",
)
filters_row = ui.layout_columns(
    ui.input_select(
        "selected_period",
        "Select period",
        get_periods().to_list(),
        width="100%",
    ),
    ui.input_radio_buttons(
        "selected_content_type",
        "Select Type",
        ("movie", "show"),
    ),
    col_widths=(8, 4),
    gap="4rem",
)
card_row = ui.layout_columns(
    card_ui("elements_per_content"),
    card_ui("views"),
    card_ui("hours"),
    col_widths=(4, 4, 4),
    gap="4rem",
)
chart_row = ui.layout_column_wrap(
    output_widget("display_velocity"),
    width=1,
)
preview_row = ui.layout_column_wrap(
    ui.output_data_frame("preview_dataframe"),
    ui.input_action_button(
        "reset_titles",
        "Reset titles",
        width="100px",
    ),
    width=1,
)

app_ui = ui.page_fluid(
    ui.layout_column_wrap(
        ui.h1("Movie Analytics Dashboard"),
        greeting_row,
        filters_row,
        card_row,
        chart_row,
        preview_row,
        width=1,
        heights_equal="row",
        gap="3rem",
    ),
    title="Movie Analytics",
    class_="mt-4 px-5",
)


def server(input, output, session):
    selected_titles = reactive.value([])

    def plotly_selection_callback(trace, points, state):
        custom_data = trace.customdata
        selected_points = list(trace.selectedpoints)

        titles = [
            t for ind, l in enumerate(custom_data) for t in l if ind in selected_points
        ]
        selected_titles.set(titles)

    @reactive.effect
    @reactive.event(
        input.selected_period, input.selected_content_type, input.reset_titles
    )
    def remove_titles():
        selected_titles.set([])

    @render.text
    def greeting():
        name = input.name()
        return "Enter your name" if not name else f"Hello {name}!"

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
        w.data[0].on_selection(plotly_selection_callback)
        w.data[0].on_deselect(remove_titles)
        return w

    @render.data_frame
    def preview_dataframe():
        df = preview_data(
            input.selected_period(),
            input.selected_content_type(),
            selected_titles(),
        )
        return render.DataGrid(df, width="100%")

    card_server(
        "elements_per_content",
        input.selected_content_type,
        None,
        get_num_elements,
        input.selected_period,
        input.selected_content_type,
    )
    card_server(
        "views",
        None,
        "Views",
        get_num_views,
        input.selected_period,
        input.selected_content_type,
    )
    card_server(
        "hours",
        None,
        "Hours Watched",
        get_hours_watch,
        input.selected_period,
        input.selected_content_type,
    )


app = App(app_ui, server)
