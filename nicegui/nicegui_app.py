from python_webapp_comparison import get_content_types
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

from typing import List
from nicegui import binding
from nicegui import html
from nicegui import ui

periods = get_periods()
content_types = get_content_types()

################################################
### STATE
################################################


class State:
    selected_period: str = binding.BindableProperty()
    selected_content_type: str = binding.BindableProperty()
    selected_titles: List[str] = binding.BindableProperty()

    def __init__(self, period, content_type, titles):
        self.selected_period = period
        self.selected_content_type = content_type
        self.selected_titles = titles


state = State(periods[0], content_types[0], [])


def build_plotly_figure(state: State):
    fig = plot_velocity_plotly(
        state.selected_period,
        state.selected_content_type,
    )
    fig.update_layout(
        template="plotly_white",
    )
    return fig


################################################
### LAYOUT
################################################

app = ui.column().classes("mx-auto container px-8 gap-8 mt-4")

with app:
    title_row = ui.row()
    greeting_row = ui.row(align_items="end").classes("full-width q-col-gutter-sm")
    filters_row = ui.row(align_items="end").classes("full-width q-col-gutter-sm")
    card_row = ui.row().classes("full-width q-gutter-md")
    chart_row = ui.row().classes("full-width")
    preview_row = ui.row().classes("full-width")

################################################
### TITLE & GREETING
################################################

with title_row:
    html.h1("Movie Analytics Dashboard").classes("text-h3 text-weight-bold")

with greeting_row:
    name = ui.input(
        label="Your name",
        placeholder="Provide your name",
    )
    name.classes("col-8")
    greeting = ui.label()
    greeting.bind_text_from(
        name,
        "value",
        backward=lambda name: f"Hello {name}!" if name else "Provide a name",
    )
    greeting.classes("col text-h5")

################################################
### DROPDOWN FILTERS
################################################

with filters_row:
    period_input = ui.select(
        periods,
        value=state.selected_period,
        label="Select Period",
    )
    period_input.bind_value(state, "selected_period")
    period_input.classes("col-8")

    content_type_input = ui.radio(
        ["movie", "show"],
        value=state.selected_content_type,
    )
    content_type_input.bind_value(state, "selected_content_type")
    content_type_input.classes("col")

################################################
### CARDS
################################################


def card(state: State, title, reactive_title, fn_value):
    with ui.card().classes("col"):
        with ui.card_section():
            if reactive_title:
                ui.label().bind_text_from(
                    reactive_title,
                    "value",
                    backward=lambda s: f"{s.capitalize()}s",
                )
            else:
                ui.label(title)

            ui.label().bind_text_from(
                state,
                "selected_period",
                backward=lambda _: fn_value(
                    state.selected_period, state.selected_content_type
                ),
            ).bind_text_from(
                state,
                "selected_content_type",
                backward=lambda _: fn_value(
                    state.selected_period, state.selected_content_type
                ),
            ).classes("text-h4")


with card_row:
    card(state, None, content_type_input, get_num_elements)
    card(state, "Views", None, get_num_views)
    card(state, "Hours Watched", None, get_hours_watch)

################################################
### CHART & DATAFRAME
################################################

with chart_row:
    plotly_chart = ui.plotly(build_plotly_figure(state))
    plotly_chart.classes("full-width")

with preview_row:
    data_preview = preview_data(
        state.selected_period,
        state.selected_content_type,
        state.selected_titles,
    )
    data_output = ui.aggrid.from_polars(data_preview)

################################################
### CALLBACKS
################################################


def compute_data_preview(state: State, data_preview_widget):
    df = preview_data(
        state.selected_period,
        state.selected_content_type,
        state.selected_titles,
    ).to_dicts()
    data_preview_widget.options["rowData"] = df
    data_preview_widget.update()


def plotly_selection_callback(titles: List[str], state: State, data_preview_widget):
    """On Change Plotly Selection -> Titles to filter Dataframe"""
    state.selected_titles = titles
    compute_data_preview(state, data_preview_widget)


def handle_widget_callback(state: State, plotly_out, data_out):
    """On Change Period/Type -> Plotly/Dataframe"""
    plotly_out.update_figure(build_plotly_figure(state))
    compute_data_preview(state, data_out)


period_input.on(
    "update:model-value",
    lambda _: handle_widget_callback(state, plotly_chart, data_output),
)
content_type_input.on(
    "update:model-value",
    lambda _: handle_widget_callback(state, plotly_chart, data_output),
)

plotly_chart.on(
    # ON Event: https://github.com/zauberzeug/nicegui/issues/3762
    "plotly_selected",
    lambda e: plotly_selection_callback(e.args, state, data_output),
    js_handler="(event) => emit(event.points.map(point => point.customdata).flat())",
).on(
    "plotly_deselect",
    lambda _: plotly_selection_callback([], state, data_output),
).on(
    "plotly_doubleclick",
    lambda _: plotly_selection_callback([], state, data_output),
)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
