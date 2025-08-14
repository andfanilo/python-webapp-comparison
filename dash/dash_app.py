from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

from dash import Dash, html, dcc, callback, Output, Input

app = Dash(
    __name__,
    external_scripts=["https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"],
)

app.layout = html.Div(
    [
        html.H1("Movie Analytics Dashboard", className="font-bold text-4xl"),
        dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),
    ],
    className="container mx-auto mt-8",
)

if __name__ == '__main__':
    app.run(debug=True)
