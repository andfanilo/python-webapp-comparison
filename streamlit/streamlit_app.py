from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

import streamlit as st

st.set_page_config(page_title="Movie Analytics", layout="wide")

app = st.container(gap="medium")

with app:
    title_row = st.container()
    greeting_row = st.container(
        horizontal=True,
        horizontal_alignment="distribute",
        vertical_alignment="bottom",
    )
    filters_row = st.container(horizontal=True, gap="large")
    card_row = st.container(horizontal=True)
    chart_row = st.container()
    preview_row = st.container()

title_row.title("Movie Analytics Dashboard")

with greeting_row:
    name = st.text_input("Enter name", width=250)
    if not name:
        st.markdown("Enter name", width="content")
    else:
        st.markdown(f"Hello {name}!", width="content")

with filters_row:
    periods = get_periods()
    selected_period = st.selectbox("Select Period: ", periods, width="stretch")
    selected_content_type = st.radio(
        "Select Type", ("movie", "show"), format_func=str.capitalize, width=300
    )

with card_row:
    st.metric(
        f"{selected_content_type.capitalize()}s",
        get_num_elements(selected_period, selected_content_type),
        border=True,
    )
    st.metric(
        "Views", get_num_views(selected_period, selected_content_type), border=True
    )
    st.metric(
        "Hours Watched",
        get_hours_watch(selected_period, selected_content_type),
        border=True,
    )

with chart_row:
    fig = plot_velocity_plotly(selected_period, selected_content_type)
    selected_points = st.plotly_chart(
        fig,
        on_select="rerun",
        selection_mode="lasso",
    )
    selected_titles = [p["hovertext"] for p in selected_points["selection"]["points"]]

preview_data = preview_data(selected_period, selected_titles)

if preview_data.is_empty():
    st.info(
        "Lasso select titles (25 max) to see detail", width=400, icon=":material/info:"
    )
else:
    preview_row.dataframe(preview_data)
