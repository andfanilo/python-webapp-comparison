from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

from nicegui import ui
from nicegui import html
from nicegui import binding


class Filters:
    selected_period = binding.BindableProperty()
    selected_content_type = binding.BindableProperty()

    def __init__(self, p, t):
        self.selected_period = p
        self.selected_content_type = t


app = ui.column().classes("mx-auto px-4 container gap-8")

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

    def update_greeting(name: str) -> str:
        if not name:
            return "Provide a name"
        return f"Hello {name}!"

    name = ui.input(
        label="Your name",
        placeholder="Provide your name",
    )
    greeting = ui.label().bind_text_from(
        name,
        "value",
        backward=update_greeting,
    )
    greeting.tailwind.font_size("2xl")


with filters_row:
    periods = get_periods().to_list()
    content_types = ["movie", "show"]
    filters = Filters(periods[0], content_types[0])

    period_input = ui.select(
        periods,
        value=filters.selected_period,
        label="Select Period",
    ).bind_value(filters, "selected_period")
    period_input.tailwind.flex("auto")

    content_type_input = ui.radio(
        ["movie", "show"],
        value=filters.selected_content_type,
    ).bind_value(filters, "selected_content_type")
    content_type_input.tailwind

with card_row:
    with ui.card().classes("flex-1"):
        with ui.card_section():
            greeting = ui.label().bind_text_from(
                content_type_input,
                "value",
                backward=lambda s: f"{s.capitalize()}s",
            )
            ui.label().bind_text_from(
                filters,
                "selected_period",
                backward=lambda period: get_num_elements(
                    period, filters.selected_content_type
                ),
            ).bind_text_from(
                filters,
                "selected_content_type",
                backward=lambda content_type: get_num_elements(
                    filters.selected_period, content_type
                ),
            ).tailwind.font_size("2xl")

    with ui.card().classes("flex-1"):
        with ui.card_section():
            ui.label("Views")
            ui.label().bind_text_from(
                filters,
                "selected_period",
                backward=lambda period: get_num_views(
                    period, filters.selected_content_type
                ),
            ).bind_text_from(
                filters,
                "selected_content_type",
                backward=lambda content_type: get_num_views(
                    filters.selected_period, content_type
                ),
            ).tailwind.font_size("2xl")

    with ui.card().classes("flex-1"):
        with ui.card_section():
            ui.label("Hours Watched")
            ui.label().bind_text_from(
                filters,
                "selected_period",
                backward=lambda period: get_hours_watch(
                    period, filters.selected_content_type
                ),
            ).bind_text_from(
                filters,
                "selected_content_type",
                backward=lambda content_type: get_hours_watch(
                    filters.selected_period, content_type
                ),
            ).tailwind.font_size("2xl")

with chart_row:
    fig = plot_velocity_plotly(
        filters.selected_period,
        filters.selected_content_type,
    )
    fig.update_layout(
        template="plotly_white",
    )
    plotly_chart = ui.plotly(fig).classes("w-full")

with preview_row:
    data = preview_data(
        filters.selected_period,
        [],
    ).to_pandas()
    preview_output = ui.aggrid.from_pandas(data).classes("max-h-40")

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
