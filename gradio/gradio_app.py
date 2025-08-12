from python_webapp_comparison import get_data
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_shows
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_detail_per_titles
from python_webapp_comparison import plot_velocity

import polars as pl
import gradio as gr

df = get_data()

css = """
.card {
    border: 1px;
}
"""


def update_dataframe_preview(period):
    return df.filter(pl.col("report") == period)


with gr.Blocks(css=css) as demo:
    gr.Markdown("# Movie Analytics Dashboard")

    with gr.Row():
        name_input = gr.Textbox(
            label="Enter your name",
            container=False,
        )
        hello_output = gr.Markdown("Provide your name")

        @name_input.change(
            inputs=[name_input],
            outputs=[hello_output],
        )
        def update_greeting(name):
            if not name:
                return "Provide your name"
            return f"Hello {name}!"

    with gr.Row():
        periods = get_periods().to_list()
        selected_period = gr.Dropdown(
            periods,
            label="Select period:",
            interactive=True,
        )

    with gr.Row():
        with gr.Column(elem_classes="card"):
            gr.Markdown("### Movies")
            gr.Markdown(f"{get_num_elements(selected_period.value)}")
        with gr.Column():
            gr.Markdown("### Shows")
            gr.Markdown(f"{get_num_shows(selected_period.value)}")
        with gr.Column():
            gr.Markdown("### Views")
            gr.Markdown(f"{get_num_views(selected_period.value)}")
        with gr.Column():
            gr.Markdown("### Hours Watched")
            gr.Markdown(f"{get_hours_watch(selected_period.value)}")

    with gr.Row():
        preview_dataframe = gr.DataFrame(update_dataframe_preview(periods[0]))

    selected_period.change(
        fn=update_dataframe_preview,
        inputs=selected_period,
        outputs=preview_dataframe,
    )

demo.launch()
