from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

from dash import Dash, html, dcc, callback, Output, Input, dash_table

periods = get_periods().to_list()
content_types = ["movie", "show"]

app = Dash(
    __name__,
    external_scripts=["https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"],
)

title_row = html.H1(
    "Movie Analytics Dashboard",
    className="font-bold text-4xl",
)

greeting_row = html.Div(
    [
        dcc.Input(
            id="name",
            placeholder="Enter name",
            className="rounded-sm border-gray-200 border-1 border-solid flex-2",
        ),
        html.Div(id="greeting", className="flex-1"),
    ],
    className="flex gap-8",
)

filters_row = html.Div(
    [
        html.Div(
            dcc.Dropdown(
                id="selected-period", options=periods, value=periods[0], clearable=False
            ),
            className="flex-2",
        ),
        html.Div(
            dcc.RadioItems(
                id="selected-content-type",
                options=content_types,
                value=content_types[0],
            ),
            className="flex-1",
        ),
    ],
    className="flex items-end gap-8",
)

card_row = html.Div(
    [
        html.Div(
            [
                html.Div(id="elements-count-card-title"),
                html.Div(
                    id="elements-count-card-value", className="text-4xl font-bold"
                ),
            ],
            className="flex-1 p-6 border-1 flex flex-col gap-1 rounded-md",
        ),
        html.Div(
            [
                html.Div("Views"),
                html.Div(id="views-count-card-value", className="text-4xl font-bold"),
            ],
            className="flex-1 p-6 border-1 flex flex-col gap-1 rounded-md",
        ),
        html.Div(
            [
                html.Div("Hours Watched"),
                html.Div(id="hours-watched-card-value", className="text-4xl font-bold"),
            ],
            className="flex-1 p-6 border-1 flex flex-col gap-1 rounded-md",
        ),
    ],
    className="flex gap-8",
)

chart_row = html.Div(
    dcc.Graph(
        id="plotly-chart",
    ),
)

preview_row = html.Div(
    dash_table.DataTable(
        id="preview-data",
        page_size=10,
        page_action="native",
        sort_action="native",
    ),
)

app.layout = html.Div(
    [
        title_row,
        greeting_row,
        filters_row,
        card_row,
        chart_row,
        preview_row,
    ],
    className="container mx-auto mt-8 flex flex-col gap-8",
)


@callback(
    Output(component_id="greeting", component_property="children"),
    Input(component_id="name", component_property="value"),
)
def greet_name(name):
    return f"Hello {name}!" if name else "Enter name"


@callback(
    Output(component_id="elements-count-card-title", component_property="children"),
    Input(component_id="selected-content-type", component_property="value"),
)
def card_title(content_type):
    return f"{content_type.capitalize()}s"


@callback(
    Output(component_id="elements-count-card-value", component_property="children"),
    Input(component_id="selected-period", component_property="value"),
    Input(component_id="selected-content-type", component_property="value"),
)
def elements_per_content(period, content_type):
    return get_num_elements(period, content_type)


@callback(
    Output(component_id="views-count-card-value", component_property="children"),
    Input(component_id="selected-period", component_property="value"),
    Input(component_id="selected-content-type", component_property="value"),
)
def count_views(period, content_type):
    return get_num_views(period, content_type)


@callback(
    Output(component_id="hours-watched-card-value", component_property="children"),
    Input(component_id="selected-period", component_property="value"),
    Input(component_id="selected-content-type", component_property="value"),
)
def count_hours_watched(period, content_type):
    return get_hours_watch(period, content_type)


@callback(
    Output(component_id="plotly-chart", component_property="figure"),
    Input(component_id="selected-period", component_property="value"),
    Input(component_id="selected-content-type", component_property="value"),
)
def count_hours_watched(period, content_type):
    fig = plot_velocity_plotly(
        period,
        content_type,
    )
    fig.update_layout(
        template="plotly_white",
    )
    return fig


@callback(
    Output(component_id="preview-data", component_property="data"),
    Output(component_id="preview-data", component_property="columns"),
    Input(component_id="selected-period", component_property="value"),
    Input(component_id="selected-content-type", component_property="value"),
    Input(component_id="plotly-chart", component_property="selectedData"),
)
def data_preview(period, content_type, selected_points):
    if selected_points:
        selected_titles = [p["hovertext"] for p in selected_points["points"]]
    else:
        selected_titles = []
    df = preview_data(
        period,
        content_type,
        selected_titles,
    )
    return df.to_pandas().to_dict("records"), [{"name": i, "id": i} for i in df.columns]


if __name__ == "__main__":
    app.run(debug=True)
