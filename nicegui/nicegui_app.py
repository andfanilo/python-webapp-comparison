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


class Filters:
    selected_period: str = binding.BindableProperty()
    selected_content_type: str = binding.BindableProperty()
    selected_titles: List[str] = binding.BindableProperty()

    def __init__(self, period, content_type, titles):
        self.selected_period = period
        self.selected_content_type = content_type
        self.selected_titles = titles


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
                filters,
                "selected_period",
                backward=lambda _: fn_value(
                    filters.selected_period, filters.selected_content_type
                ),
            ).bind_text_from(
                filters,
                "selected_content_type",
                backward=lambda _: fn_value(
                    filters.selected_period, filters.selected_content_type
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
    filters = Filters(periods[0], content_types[0], [])

    period_input = ui.select(
        periods,
        value=filters.selected_period,
        label="Select Period",
    )
    period_input.bind_value(filters, "selected_period")
    period_input.tailwind.flex("auto")

    content_type_input = ui.radio(
        ["movie", "show"],
        value=filters.selected_content_type,
    )
    content_type_input.bind_value(filters, "selected_content_type")
    content_type_input.tailwind

with card_row:
    card(None, content_type_input, get_num_elements)
    card("Views", None, get_num_views)
    card("Hours Watched", None, get_hours_watch)


def build_plot(filt):
    fig = plot_velocity_plotly(
        filt.selected_period,
        filt.selected_content_type,
    )
    fig.update_layout(
        template="plotly_white",
    )
    return fig


with chart_row:
    plotly_chart = ui.plotly(build_plot(filters))
    plotly_chart.classes("w-full")
    period_input.on(
        "update:model-value", lambda _: plotly_chart.update_figure(build_plot(filters))
    )
    content_type_input.on(
        "update:model-value", lambda _: plotly_chart.update_figure(build_plot(filters))
    )

    # ON Event: https://github.com/zauberzeug/nicegui/issues/3762
    plotly_chart.on(
        "plotly_selected",
        lambda e: ui.notify(e.args),
        js_handler="(event) => emit(event.points.map(point => point.customdata).flat())",
    ).on(
        "plotly_deselect",
        lambda _: ui.notify("Byebye"),
    ).on(
        "plotly_doubleclick",
        lambda _: ui.notify("Byebye"),
    )


with preview_row:
    data_preview = preview_data(
        filters.selected_period,
        filters.selected_titles,
    )
    data_output = ui.aggrid.from_polars(data_preview)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
