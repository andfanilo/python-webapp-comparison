from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

import solara

periods = get_periods().to_list()
content_types = ["movie", "show"]

name = solara.reactive("")
selected_period = solara.reactive(periods[0])
selected_content_type = solara.reactive(content_types[0])

selected_points = solara.reactive({})

def update_selection(e):
    print(e)
    selected_points.set(e)

@solara.component
def card(title, value):
    with solara.Card(
        title=title,
        style={"flex": 1},
    ):
        solara.Markdown(str(value))

@solara.component
def Page():
    app = solara.Column(
        gap="2rem",
        style={"padding": "2rem 4rem"},
    )

    with app:
        solara.Title("Movie Analytics")
        title_row = solara.Row()
        greeting_row = solara.Row(
            gap="4rem",
            style={"align-items": "end"},
        )
        filters_row = solara.Row(
            gap="4rem",
            style={"align-items": "end"},
        )
        cards_row = solara.Row(
            gap="1rem",
        )
        chart_row = solara.Row(
            style={"width": "100%"},
        )
        preview_row = solara.Row(
            style={"width": "100%"},
        )

    with title_row:
        solara.Markdown("# Movie Analytics Dashboard")

    with greeting_row:
        solara.InputText(
            "Enter name",
            name,
            continuous_update=True,
            style={"flex": 3},
        )
        solara.Markdown(
            f"Hello {name.value}" if name.value else "Enter name",
            style={"flex": 1, "font-size": "1.2rem"},
        )

    with filters_row:
        solara.Select(
            label="Select Period",
            value=selected_period,
            values=periods,
            style={"flex": 3},
        )
        solara.ToggleButtonsSingle(
            value=selected_content_type,
            values=content_types,
            style={"flex": 1},
        )

    with cards_row:
        card(
            f"{selected_content_type.value.capitalize()}s", 
            get_num_elements(
                selected_period.value,
                selected_content_type.value,
            )
        )
        card(
            "Views", 
            get_num_views(
                selected_period.value,
                selected_content_type.value,
            )
        )
        card(
            "Hours Watched", 
            get_hours_watch(
                selected_period.value,
                selected_content_type.value,
            )
        )

    with chart_row:
        fig = plot_velocity_plotly(
            selected_period.value,
            selected_content_type.value,
        )
        fig.update_layout(
            template="plotly_white",
        )
        solara.FigurePlotly(
            fig, 
            on_selection=update_selection,
            on_deselect=update_selection,
        )

    with preview_row:
        solara.DataFrame(preview_data(
            selected_period.value,
            [],
        ))

    return app
