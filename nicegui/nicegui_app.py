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


@binding.bindable_dataclass
class Filters:
    selected_period: str
    selected_content_type: str
    selected_titles: List[str]


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
    with ui.card().classes("flex-1"):
        with ui.card_section():
            elements_card_title = ui.label()
            elements_card_title.bind_text_from(
                content_type_input,
                "value",
                backward=lambda s: f"{s.capitalize()}s",
            )

            elements_card_value = ui.label().bind_text_from(
                filters,
                "selected_period",
                backward=lambda _: get_num_elements(
                    filters.selected_period, filters.selected_content_type
                ),
            )
            elements_card_value.bind_text_from(
                filters,
                "selected_content_type",
                backward=lambda _: get_num_elements(
                    filters.selected_period, filters.selected_content_type
                ),
            )
            elements_card_value.tailwind.font_size("2xl")

    with ui.card().classes("flex-1"):
        with ui.card_section():
            views_card_title = ui.label("Views")
            views_card_value = ui.label()
            views_card_value.bind_text_from(
                filters,
                "selected_period",
                backward=lambda _: get_num_views(
                    filters.selected_period, filters.selected_content_type
                ),
            )
            views_card_value.bind_text_from(
                filters,
                "selected_content_type",
                backward=lambda _: get_num_views(
                    filters.selected_period, filters.selected_content_type
                ),
            )
            views_card_value.tailwind.font_size("2xl")

    with ui.card().classes("flex-1"):
        with ui.card_section():
            hours_card_title = ui.label("Hours Watched")
            hours_card_value = ui.label()
            hours_card_value.bind_text_from(
                filters,
                "selected_period",
                backward=lambda _: get_hours_watch(
                    filters.selected_period, filters.selected_content_type
                ),
            )
            hours_card_value.bind_text_from(
                filters,
                "selected_content_type",
                backward=lambda _: get_hours_watch(
                    filters.selected_period, filters.selected_content_type
                ),
            )
            hours_card_value.tailwind.font_size("2xl")

with chart_row:
    fig = plot_velocity_plotly(
        filters.selected_period,
        filters.selected_content_type,
    )
    fig.update_layout(
        template="plotly_white",
    )
    plotly_chart = ui.plotly(fig)
    plotly_chart.classes("w-full")

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
    ).to_pandas()
    data_output = ui.aggrid.from_pandas(data_preview)
    data_output.classes("max-h-40")

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
