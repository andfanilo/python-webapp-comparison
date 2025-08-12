from python_webapp_comparison import get_data
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity

import streamlit as st

st.set_page_config(page_title="Movie Analytics", layout="wide")

df = get_data()

app = st.container(gap="medium")

app.title("Movie Analytics Dashboard")

with app.container(
    horizontal=True,
    horizontal_alignment="distribute",
    vertical_alignment="bottom",
):
    name = st.text_input("Enter name", width=250)
    if not name:
        st.markdown("Enter name", width="content")
    else:
        st.markdown(f"Hello {name}!", width="content")

with app.container(horizontal=True, gap="large"):
    periods = get_periods()
    selected_period = st.selectbox("Select Period: ", periods, width="stretch")
    selected_content_type = st.radio(
        "Select Type", ("movie", "show"), format_func=str.capitalize, width=300
    )

with app.container(horizontal=True):
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

with app.container(horizontal=True):
    chart_container = st.container()
    detail_container = st.container(width=400)

with chart_container:
    fig = plot_velocity(selected_period, selected_content_type)
    st.plotly_chart(
        fig,
    )

app.dataframe(df)
