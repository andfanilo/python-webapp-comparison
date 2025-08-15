from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import reflex as rx
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

periods = get_periods()
content_types = ["movie", "show"]

################################################
### STATE
################################################


class State(rx.State):
    name: str = ""
    selected_period: str = periods[0]
    selected_content_type: str = content_types[0]
    selected_titles: List[str]

    figure: go.Figure = px.scatter()

    ################################################
    ### REACTIVITY
    ################################################

    @rx.var
    def greeting(self) -> str:
        """Reactive Name -> Greeting"""
        return f"Hello {self.name}!" if self.name else "Enter your name"

    @rx.var(cache=True)
    def card_content_title(self) -> str:
        """Reactive Period -> Card title"""
        return f"{self.selected_content_type.capitalize()}s"

    @rx.var(cache=True)
    def count_num_elements(self) -> int:
        """Reactive Period/Type -> Count Card value"""
        return get_num_elements(self.selected_period, self.selected_content_type)

    @rx.var(cache=True)
    def count_num_views(self) -> str:
        """Reactive Period/Type -> Views Card value"""
        return get_num_views(self.selected_period, self.selected_content_type)

    @rx.var(cache=True)
    def count_hours_watch(self) -> str:
        """Reactive Period/Type -> Hours Card value"""
        return get_hours_watch(self.selected_period, self.selected_content_type)

    @rx.var
    def compute_data_preview(self) -> pd.DataFrame:
        """Reactive Period/Type/Titles -> Dataframe"""
        return preview_data(
            self.selected_period,
            self.selected_content_type,
            self.selected_titles,
        ).to_pandas()

    ################################################
    ### CALLBACKS
    ################################################

    @rx.event
    def select_period_callback(self, value):
        """On Change Period -> Titles to filter Dataframe"""
        self.selected_period = value
        self.selected_titles = []
        self.build_plotly_figure()

    @rx.event
    def select_content_type_callback(self, value):
        """On Change Type -> Titles to filter Dataframe"""
        self.selected_content_type = value
        self.selected_titles = []
        self.build_plotly_figure()

    @rx.event
    def plotly_selection_callback(self, evt):
        """On Change Plotly Selection -> Titles to filter Dataframe"""
        # https://github.com/orgs/reflex-dev/discussions/2845
        custom_data = self.figure.data[0]["customdata"]
        selected_point_idx = [p["pointIndex"] for p in evt]
        selected_titles = [
            t
            for ind, l in enumerate(custom_data)
            for t in l
            if ind in selected_point_idx
        ]
        self.selected_titles = selected_titles

    @rx.event
    def build_plotly_figure(self):
        """On Change Period/Type -> Plotly Chart"""
        fig = plot_velocity_plotly(self.selected_period, self.selected_content_type)
        self.figure = fig


################################################
### TITLE & GREETING
################################################


def title_row() -> rx.Component:
    return (
        rx.heading(
            "Movies Dashboard",
            size="8",
        ),
    )


def greeting_row() -> rx.Component:
    label = rx.text("Enter name:", as_="span")
    input_box = rx.input(
        placeholder="Search here...",
        value=State.name,
        on_change=State.set_name,
    )
    input_widget = rx.flex(
        label,
        input_box,
        direction="column",
        spacing="1",
        class_name="flex-2",
    )
    greeting_out = rx.text(
        State.greeting,
        as_="span",
        class_name="flex-1",
    )

    return rx.flex(
        input_widget,
        greeting_out,
        align="end",
        spacing="8",
        class_name="w-full",
    )


################################################
### DROPDOWN FILTERS
################################################


def filters_row() -> rx.Component:
    period_select = rx.flex(
        rx.text("Select period:", as_="span"),
        rx.select(
            periods,
            value=State.selected_period,
            on_change=State.select_period_callback,
        ),
        direction="column",
        class_name="flex-2",
    )
    content_type_select = rx.flex(
        rx.text("Select content:", as_="span"),
        rx.segmented_control.root(
            rx.segmented_control.item("Movies", value="movie"),
            rx.segmented_control.item("Shows", value="show"),
            value=State.selected_content_type,
            on_change=State.select_content_type_callback,
        ),
        direction="column",
        class_name="flex-1",
    )
    return rx.flex(
        period_select,
        content_type_select,
        spacing="7",
        class_name="w-full",
    )


################################################
### CARDS
################################################


def card(title, value) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.text(title),
            rx.text(value, class_name="text-4xl"),
            spacing="2",
            direction="column",
        ),
        size="4",
        class_name="flex-1",
    )


def card_row() -> rx.Component:
    return rx.flex(
        card(State.card_content_title, State.count_num_elements),
        card("Views", State.count_num_views),
        card("Hours Watched", State.count_hours_watch),
        spacing="6",
        class_name="w-full",
    )


################################################
### CHART & DATAFRAME
################################################


def chart_row() -> rx.Component:
    return rx.plotly(
        data=State.figure,
        on_mount=State.build_plotly_figure,
        on_selected=State.plotly_selection_callback.throttle(500),
        template=pio.templates["plotly_white"],
        class_name="w-full",
    )


def preview_row() -> rx.Component:
    return rx.box(
        rx.data_table(
            data=State.compute_data_preview,
            pagination=True,
            search=True,
        ),
        class_name="w-full max-h-8",
    )


################################################
### LAYOUT
################################################


@rx.page(route="/", title="Movies Dashboard")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            title_row(),
            greeting_row(),
            filters_row(),
            card_row(),
            chart_row(),
            preview_row(),
            spacing="6",
            class_name="mt-4",
        ),
        size="4",
    )


app = rx.App()
