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


class State:
    selected_period: str = binding.BindableProperty()
    selected_content_type: str = binding.BindableProperty()
    selected_titles: List[str] = binding.BindableProperty()

    def __init__(self, period, content_type, titles):
        self.selected_period = period
        self.selected_content_type = content_type
        self.selected_titles = titles


def build_plot(state: State):
    fig = plot_velocity_plotly(
        state.selected_period,
        state.selected_content_type,
    )
    fig.update_layout(
        template="plotly_white",
    )
    return fig


def plotly_event_callback(titles: List[str], state: State, data_preview_widget):
    state.selected_titles = titles
    update_data_preview(state, data_preview_widget)


def update_data_preview(state: State, data_preview_widget):
    df = preview_data(
        state.selected_period,
        state.selected_content_type,
        state.selected_titles,
    ).to_dicts()
    data_preview_widget.options["rowData"] = df
    data_preview_widget.update()


def update_graph(state: State, graph_widget):
    graph_widget.update_figure(build_plot(state))


def card(title, reactive_title, fn_value):
    with ui.card().classes("flex-1"):
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
            ).tailwind.font_size("2xl")


app = ui.column().classes("mx-auto container px-8 gap-8")

with app:
    title_row = ui.row()
    greeting_row = ui.row(align_items="end").classes("justify-between w-full")
    filters_row = ui.row(align_items="end").classes("gap-16 justify-between w-full")
    card_row = ui.row().classes("w-full")
    chart_row = ui.row().classes("w-full")
    preview_row = ui.row().classes("w-full")

with title_row:
    html.h1("Movie Analytics Dashboard").tailwind.font_size("4xl").font_weight("bold")

with greeting_row:
    name = ui.input(
        label="Your name",
        placeholder="Provide your name",
    )
    greeting = ui.label()
    greeting.bind_text_from(
        name,
        "value",
        backward=lambda name: f"Hello {name}!" if name else "Provide a name",
    )
    greeting.tailwind.font_size("2xl")


with filters_row:
    periods = get_periods().to_list()
    content_types = ["movie", "show"]
    state = State(periods[0], content_types[0], [])

    period_input = ui.select(
        periods,
        value=state.selected_period,
        label="Select Period",
    )
    period_input.bind_value(state, "selected_period")
    period_input.tailwind.flex("auto")

    content_type_input = ui.radio(
        ["movie", "show"],
        value=state.selected_content_type,
    )
    content_type_input.bind_value(state, "selected_content_type")

with card_row:
    card(None, content_type_input, get_num_elements)
    card("Views", None, get_num_views)
    card("Hours Watched", None, get_hours_watch)


with chart_row:
    plotly_chart = ui.plotly(build_plot(state))
    plotly_chart.classes("w-full")


with preview_row:
    data_preview = preview_data(
        state.selected_period,
        state.selected_content_type,
        state.selected_titles,
    )
    data_output = ui.aggrid.from_polars(data_preview)


# Only changes titles and data preview
# ON Event: https://github.com/zauberzeug/nicegui/issues/3762
plotly_chart.on(
    "plotly_selected",
    lambda e: plotly_event_callback(e.args, state, data_output),
    js_handler="(event) => emit(event.points.map(point => point.customdata).flat())",
).on(
    "plotly_deselect",
    lambda _: plotly_event_callback([], state, data_output),
).on(
    "plotly_doubleclick",
    lambda _: plotly_event_callback([], state, data_output),
)


def handle_widget_callback(state: State, plotly_out, data_out):
    update_graph(state, plotly_out)
    update_data_preview(state, data_out)


period_input.on(
    "update:model-value",
    lambda _: handle_widget_callback(state, plotly_chart, data_output),
)
content_type_input.on(
    "update:model-value",
    lambda _: handle_widget_callback(state, plotly_chart, data_output),
)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
