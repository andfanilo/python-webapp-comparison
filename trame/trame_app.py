from trame.app import TrameApp
from trame.decorators import change
from trame.ui.html import DivLayout
from trame.widgets import html, plotly, client

from python_webapp_comparison import get_content_types
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

periods = get_periods()
content_types = get_content_types()


class MovieDashboard(TrameApp):
    def __init__(self, server=None):
        super().__init__(server, client_type="vue3")

        # add tailwind
        self.server.enable_module(
            {"scripts": ["https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"]}
        )

        # define/reserve some initial states for UI
        self.state.elements_count = 0
        self.state.views_count = 0
        self.state.hours_watched = 0
        self.state.colums = []
        self.state.rows = []

        self._build_ui()

    def _build_ui(self):
        with DivLayout(self.server) as self.ui:
            self.ui.root.classes = "container mx-auto px-4 mt-8 flex flex-col gap-8"

            client.Style("""
                table, th, td {
                    border: 1px solid black;
                }
            """)

            html.H1("Movie Analytics Dashboard", classes="font-bold text-4xl")

            # greeting
            with html.Div(classes="flex gap-8"):
                html.Input(
                    v_model=("name", ""),
                    placeholder="Enter name",
                    classes="rounded-sm border-gray-200 border-1 border-solid flex-2",
                )
                html.Div(
                    "{{ name.length ? 'Hello ' + name : 'Enter name' }}",
                    classes="flex-1",
                )

            # filters
            with html.Div(classes="flex items-end gap-8"):
                with html.Select(
                    v_model=("period", periods[0]),
                    classes="flex-2",
                ):
                    for p in periods:
                        html.Option(p, value=p)
                with html.Div(classes="flex-1"):
                    for content_type in content_types:
                        with html.Label() as label:
                            html.Input(
                                type="radio",
                                v_model=("content_type", content_types[0]),
                                value=content_type,
                            )
                            label.add_child(content_type)

            # cards
            with html.Div(classes="flex gap-8"):
                with html.Div(
                    classes="flex-1 p-6 border-1 flex flex-col gap-1 rounded-md"
                ):
                    html.Div("{{ content_type }}", style="text-transform: capitalize;")
                    html.Div("{{ elements_count }}", classes="text-4xl font-bold")
                with html.Div(
                    classes="flex-1 p-6 border-1 flex flex-col gap-1 rounded-md"
                ):
                    html.Div("Views")
                    html.Div("{{ views_count }}", classes="text-4xl font-bold")
                with html.Div(
                    classes="flex-1 p-6 border-1 flex flex-col gap-1 rounded-md"
                ):
                    html.Div("Hours Watched")
                    html.Div("{{ hours_watched }}", classes="text-4xl font-bold")

            # Chart
            with html.Div(style="position: relative; height: 40vh;"):
                self.ctrl.update_fig = plotly.Figure().update

            # Table
            with html.Div(style="max-height: 40vh; max-width: 100vw; overflow: auto;"):
                with html.Table():
                    with html.Tr():
                        html.Th("{{ col }}", v_for="col, i in colums", key="i")
                    with html.Tr(v_for="row, ridx in rows", key="ridx"):
                        html.Td(
                            "{{ row[col] }}", v_for="col, cidx in colums", key="cidx"
                        )

    @change("period", "content_type")
    def _on_selection_change(self, period, content_type, **_):
        # update figure
        fig = plot_velocity_plotly(period, content_type)
        fig.update_layout(template="plotly_white")
        self.ctrl.update_fig(fig)

        # update numbers
        self.state.elements_count = get_num_elements(period, content_type)
        self.state.views_count = get_num_views(period, content_type)
        self.state.hours_watched = get_hours_watch(period, content_type)

        # update Table
        selected_titles = []
        # if selected_points:
        #     selected_titles = [p["hovertext"] for p in selected_points["points"]]
        df = preview_data(
            period,
            content_type,
            selected_titles,
        )
        self.state.colums = df.columns
        self.state.rows = [
            {
                **entry,
                "last_report_date": entry["last_report_date"].strftime("%Y-%m-%d"),
            }
            for entry in df.to_pandas().to_dict("records")
        ]


if __name__ == "__main__":
    app = MovieDashboard()
    app.server.start()
