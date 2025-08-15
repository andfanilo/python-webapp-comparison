from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

import streamlit as st

st.set_page_config(page_title="Movie Analytics", layout="wide")

periods = get_periods()
content_types = ("movie", "show")

app = st.container(gap="medium")

with app:
    title_row = st.container()
    greeting_row = st.columns(
        (2, 1),
        gap="medium",
        vertical_alignment="bottom",
    )
    filters_row = st.columns(
        (2, 1),
        gap="medium",
    )
    card_row = st.container(horizontal=True, gap="medium")
    chart_row = st.container()
    preview_row = st.container()

title_row.title("Movie Analytics Dashboard")

with greeting_row[0]:
    st.text_input("Enter name", width="stretch", key="name")
with greeting_row[1]:
    if not st.session_state.name:
        st.markdown("Enter name", width="content")
    else:
        st.markdown(f"Hello {st.session_state.name}!", width="content")

with filters_row[0]:
    st.selectbox("Select Period: ", periods, 0, width="stretch", key="selected_period")
with filters_row[1]:
    st.radio(
        "Select Type",
        content_types,
        0,
        format_func=str.capitalize,
        width="stretch",
        key="selected_content_type",
    )

with card_row:
    st.metric(
        f"{st.session_state.selected_content_type.capitalize()}s",
        get_num_elements(
            st.session_state.selected_period, st.session_state.selected_content_type
        ),
        border=True,
    )
    st.metric(
        "Views",
        get_num_views(
            st.session_state.selected_period, st.session_state.selected_content_type
        ),
        border=True,
    )
    st.metric(
        "Hours Watched",
        get_hours_watch(
            st.session_state.selected_period, st.session_state.selected_content_type
        ),
        border=True,
    )

with chart_row:
    fig = plot_velocity_plotly(
        st.session_state.selected_period, st.session_state.selected_content_type
    )
    st.plotly_chart(
        fig,
        on_select="rerun",
        selection_mode=["box", "lasso"],
        key="selected_points",
    )

data_preview = preview_data(
    st.session_state.selected_period,
    st.session_state.selected_content_type,
    [p["hovertext"] for p in st.session_state.selected_points["selection"]["points"]],
)

preview_row.dataframe(data_preview)
