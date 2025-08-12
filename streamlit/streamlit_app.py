from python_webapp_comparison import get_data
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_movies
from python_webapp_comparison import get_num_shows
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_detail_per_titles
from python_webapp_comparison import plot_top_show_hours

import streamlit as st

st.set_page_config(page_title="Movie Analytics")

df = get_data()

app = st.container(gap="medium")

app.title("Movie Analytics Dashboard - Jan / Jun 2025")

with app.container(
    horizontal=True,
    horizontal_alignment="distribute",
    vertical_alignment="bottom",
):
    name = st.text_input("Enter name", width=250)
    st.markdown(f"Hello {name}!", width="content")

with app.container():
    periods = get_periods()
    selected_period = st.selectbox("Select Period: ", periods)

with app.container(horizontal=True):
    st.metric("Movies", get_num_movies(selected_period), border=True)
    st.metric("Shows", get_num_shows(selected_period), border=True)
    st.metric("Views", get_num_views(selected_period), border=True)
    st.metric("Hours Watched", get_hours_watch(selected_period), border=True)

with app.container(horizontal=True):
    chart_container = st.container()
    detail_container = st.container(width=400)

with chart_container:
    fig = plot_top_show_hours(selected_period)
    selected_bar = st.plotly_chart(
        fig,
        on_select="rerun",
        selection_mode="points",
        config={"displayModeBar": False},
    )

with detail_container:
    if selected_bar["selection"]["points"]:
        selected_titles = [p["hovertext"] for p in selected_bar["selection"]["points"]]
        fig = plot_detail_per_titles(selected_titles)
        st.plotly_chart(
            fig,
            config={"displayModeBar": False},
        )

app.dataframe(df)
