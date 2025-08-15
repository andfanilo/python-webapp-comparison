from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

import panel as pn

pn.extension("plotly", "tabulator")

periods = get_periods().to_list()
content_types = ["movie", "show"]


def greet_name(name):
    return f"Hello {name}!" if name else "Provide a name"


name = pn.widgets.TextInput(
    name="Name",
    placeholder="Give me your name",
    description="Lemme greet you!",
    styles={"flex": "2"},
)

greeting_rx = pn.bind(greet_name, name)
greeting_output = pn.pane.HTML(
    greeting_rx,
    styles={"font-size": "1.2rem", "flex": "1"},
)


selected_period = pn.widgets.Select(
    name="Select period",
    options=periods,
    value=periods[0],
    styles={"flex": "2"},
)
selected_content_type = pn.widgets.ToggleGroup(
    name="Select type",
    options=content_types,
    behavior="radio",
    styles={"flex": "1"},
)

card_title_rx = selected_content_type.rx().capitalize() + "s"
num_elements_rx = pn.bind(get_num_elements, selected_period, selected_content_type)
num_elements_rx_int = pn.rx("{n}").format(n=num_elements_rx)
views_rx = pn.bind(get_num_views, selected_period, selected_content_type)
hours_watched_rx = pn.bind(get_hours_watch, selected_period, selected_content_type)

card_style = {
    "padding": "1rem",
    "border": "1px solid #bbbbbb",
    "border-radius": "12px",
    "flex": "1",
}
card_num_elements = pn.FlexBox(
    pn.pane.HTML(card_title_rx),
    pn.pane.HTML(
        num_elements_rx_int, styles={"font-size": "2rem", "font-weight": "bold"}
    ),
    flex_direction="column",
    styles=card_style,
)
card_views = pn.FlexBox(
    pn.pane.HTML("Views"),
    pn.pane.HTML(views_rx, styles={"font-size": "2rem", "font-weight": "bold"}),
    flex_direction="column",
    styles=card_style,
)
card_hours = pn.FlexBox(
    pn.pane.HTML("Hours Watched"),
    pn.pane.HTML(hours_watched_rx, styles={"font-size": "2rem", "font-weight": "bold"}),
    flex_direction="column",
    styles=card_style,
)


def build_plotly_figure(period, content_type):
    fig = plot_velocity_plotly(
        period,
        content_type,
    )
    fig.update_layout(
        template="plotly_white",
    )
    return fig


plotly_chart_rx = pn.bind(build_plotly_figure, selected_period, selected_content_type)
plotly_pane = pn.pane.Plotly(plotly_chart_rx, sizing_mode="stretch_width")


def extract_selected_titles(plotly_selected_data):
    if plotly_selected_data:
        return [p["hovertext"] for p in plotly_selected_data["points"]]
    else:
        return []


selected_titles = pn.bind(extract_selected_titles, plotly_pane.param.selected_data)


def build_data_preview(period, content_type, titles):
    df = preview_data(period, content_type, titles).to_pandas()
    return df


data_preview_rx = pn.bind(
    build_data_preview, selected_period, selected_content_type, selected_titles
)
data_preview_pane = pn.widgets.Tabulator(data_preview_rx, sizing_mode="stretch_width")

title_row = pn.pane.HTML(
    "Movie Analytics Dashboad",
    styles={"font-size": "2rem", "font-weight": "bold"},
)

greet_row = pn.FlexBox(
    name,
    greeting_output,
    align_items="end",
    gap="4rem",
)

filters_row = pn.FlexBox(
    selected_period,
    selected_content_type,
    gap="4rem",
    align_items="end",
)

card_row = pn.FlexBox(
    card_num_elements,
    card_views,
    card_hours,
    gap="4rem",
)
chart_row = pn.Row(
    plotly_pane,
)
preview_row = pn.Row(
    data_preview_pane,
)

app = pn.FlexBox(
    title_row,
    greet_row,
    filters_row,
    card_row,
    chart_row,
    preview_row,
    sizing_mode="stretch_width",
    gap="2rem",
    flex_direction="column",
    styles={"padding": "2rem 4rem"},
)

app.servable()
