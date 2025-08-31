from trame.app import TrameApp
from trame.decorators import change
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import html, plotly, vuetify3 as v3

from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data


class MovieDashboard(TrameApp):
    def __init__(self, server=None):
        super().__init__(server, client_type="vue3")

        # define/reserve some initial states for UI
        self.state.elements_count = 0
        self.state.views_count = 0
        self.state.hours_watched = 0
        self.state.selected_titles = []

        self._build_ui()

    def _build_ui(self):
        with SinglePageLayout(self.server) as self.ui:
            # rework the toolbar
            with self.ui.toolbar.clear() as toolbar:
                toolbar.density = "compact"
                v3.VToolbarTitle("Movie Analytics Dashboard")
                v3.VSpacer()
                v3.VSelect(
                    v_model=("period", get_periods()[0]),
                    items=("periods", get_periods()),
                    density="compact",
                    hide_details=True,
                    variant="outlined",
                    style="max-width: 200px;",
                )
                with v3.VBtnToggle(
                    v_model=("content_type", "movie"),
                    density="compact",
                    hide_details=True,
                    classes="mx-2",
                    variant="outlined",
                ):
                    v3.VBtn(icon="mdi-movie-open", value="movie")
                    v3.VBtn(icon="mdi-television-classic", value="show")

            # Main content
            with self.ui.content:
                # cards
                with v3.VRow(classes="ma-2"):
                    with v3.VCol(cols=4):
                        with v3.VCard(variant="outlined"):
                            v3.VCardTitle(
                                "{{ content_type }}", classes="text-capitalize"
                            )
                            v3.VCardText("{{ elements_count }}", classes="text-h4")
                    with v3.VCol(cols=4):
                        with v3.VCard(variant="outlined"):
                            v3.VCardTitle("Views")
                            v3.VCardText("{{ views_count }}", classes="text-h4")
                    with v3.VCol(cols=4):
                        with v3.VCard(variant="outlined"):
                            v3.VCardTitle("Hours Watched")
                            v3.VCardText("{{ hours_watched }}", classes="text-h4")

                # Chart
                with html.Div(style="position: relative; height: 500px;"):
                    self.ctrl.update_fig = plotly.Figure(
                        deselect="selected_titles = []",
                        selected="selected_titles = $event?.points.map((v) => v.hovertext) || []",
                    ).update

                # Table
                v3.VDataTableVirtual(
                    headers=("columns", []),
                    items=("rows", []),
                    fixed_header=True,
                    density="compact",
                    height=400,
                )

    @change("period", "content_type", "selected_titles")
    def _on_selection_change(self, period, content_type, selected_titles, **_):
        # update figure
        fig = plot_velocity_plotly(period, content_type)
        fig.update_layout(template="plotly_white")
        self.ctrl.update_fig(fig)

        # update numbers
        self.state.elements_count = get_num_elements(period, content_type)
        self.state.views_count = get_num_views(period, content_type)
        self.state.hours_watched = get_hours_watch(period, content_type)

        # update Table
        df = preview_data(
            period,
            content_type,
            selected_titles,
        )
        self.state.columns = [
            {
                "title": c.replace("_", " ").capitalize(),
                "key": c,
            }
            for c in df.columns
        ]
        self.state.rows = [
            {
                **entry,
                # !Timestamp is not serializable by json
                "last_report_date": entry["last_report_date"].strftime("%Y-%m-%d"),
            }
            for entry in df.to_pandas().to_dict("records")
        ]


if __name__ == "__main__":
    app = MovieDashboard()
    app.server.start()
