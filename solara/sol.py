from python_webapp_comparison import get_content_types
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

import solara

periods = get_periods().to_list()
content_types = get_content_types()


def build_plotly_figure(period, content_type):
    fig = plot_velocity_plotly(
        period,
        content_type,
    )
    fig.update_layout(
        template="plotly_white",
    )
    return fig


################################################
### STATE
################################################

name = solara.reactive("")
selected_period = solara.reactive(periods[0])
selected_content_type = solara.reactive(content_types[0])

selected_titles = solara.reactive([])
plotly_figure = solara.reactive(build_plotly_figure(periods[0], content_types[0]))

################################################
### CALLBACKS
################################################


def select_period_callback(e):
    selected_period.set(e)
    plotly_figure.set(
        build_plotly_figure(selected_period.value, selected_content_type.value)
    )


def select_content_type_callback(e):
    selected_content_type.set(e)
    plotly_figure.set(
        build_plotly_figure(selected_period.value, selected_content_type.value)
    )


def plotly_selection_callback(e):
    custom_data = plotly_figure.value.data[0]["customdata"]
    selected_points = list(e["points"]["point_indexes"])

    titles = [
        t for ind, l in enumerate(custom_data) for t in l if ind in selected_points
    ]
    selected_titles.set(titles)


################################################
### APP
################################################


@solara.component
def Page():
    app = solara.Column(
        gap="2rem",
        style={"padding": "2rem 4rem"},
    )

    with app:
        solara.Title("Movie Analytics")

    ################################################
    ### LAYOUT
    ################################################

    with app:
        title_row = solara.Row()
        greeting_row = solara.Columns(
            widths=(2, 1),
            style={"gap": "2rem"},
        )
        filters_row = solara.Columns(
            widths=(2, 1),
            style={"gap": "2rem"},
        )
        cards_row = solara.Columns()
        chart_row = solara.Columns()
        preview_row = solara.Columns()

    ################################################
    ### TITLE & GREETING
    ################################################

    with title_row:
        solara.Markdown("# Movie Analytics Dashboard")

    with greeting_row:
        solara.InputText(
            "Enter name",
            value=name,
            on_value=name.set,
            continuous_update=True,
        )
        solara.Markdown(
            f"Hello {name.value}" if name.value else "Enter name",
            style={"font-size": "1.2rem"},
        )

    ################################################
    ### DROPDOWN FILTERS
    ################################################

    with filters_row:
        solara.Select(
            label="Select Period",
            value=selected_period,
            on_value=select_period_callback,
            values=periods,
            style={"flex": 3},
        )
        solara.ToggleButtonsSingle(
            value=selected_content_type,
            values=content_types,
            on_value=select_content_type_callback,
            style={"flex": 1},
        )

    ################################################
    ### CARDS
    ################################################

    def card(title, value):
        with solara.Card(
            title=title,
        ):
            solara.Markdown(
                str(value), style={"font-size": "1.5rem", "font-weight": "bold"}
            )

    with cards_row:
        card(
            f"{selected_content_type.value.capitalize()}s",
            get_num_elements(
                selected_period.value,
                selected_content_type.value,
            ),
        )
        card(
            "Views",
            get_num_views(
                selected_period.value,
                selected_content_type.value,
            ),
        )
        card(
            "Hours Watched",
            get_hours_watch(
                selected_period.value,
                selected_content_type.value,
            ),
        )

    ################################################
    ### CHART & DATAFRAME
    ################################################

    # https://github.com/widgetti/solara/discussions/1039 Layout issue
    with chart_row:
        solara.FigurePlotly(
            plotly_figure.value,
            on_selection=plotly_selection_callback,
            on_deselect=plotly_selection_callback,
        )

    with preview_row:
        solara.DataFrame(
            preview_data(
                selected_period.value,
                selected_content_type.value,
                selected_titles.value,
            )
        )

    return app
