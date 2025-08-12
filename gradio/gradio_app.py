from python_webapp_comparison import get_data
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly

import gradio as gr

df = get_data()

css = """
.card {
    border: 1px;
}
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown("# Movie Analytics Dashboard")

    with gr.Row():
        name_input = gr.Textbox(
            label="Enter your name",
            container=False,
        )
        greeting_output = gr.Markdown("Provide your name")

        @name_input.change(
            inputs=[name_input],
            outputs=[greeting_output],
        )
        def update_greeting(name):
            if not name:
                return "Provide your name"
            return f"Hello {name}!"

    with gr.Row():
        selected_period = gr.Dropdown(
            get_periods().to_list(),
            label="Select period:",
            interactive=True,
        )
        selected_content_type = gr.Radio(
            ("movie", "show"),
            value="movie",
            interactive=True,
        )

    with gr.Row():
        with gr.Column():
            display_content_type = gr.Markdown(
                f"{selected_content_type.value.capitalize()}s"
            )
            num_elements_output = gr.Markdown(
                "## "
                + str(
                    get_num_elements(
                        selected_period.value,
                        selected_content_type.value,
                    )
                )
            )

            @gr.on(
                triggers=[selected_period.change, selected_content_type.change],
                inputs=[selected_period, selected_content_type],
                outputs=[display_content_type, num_elements_output],
            )
            def update_num_elements_card(period, content_type):
                res_type = f"{selected_content_type.value.capitalize()}s"
                res_num = f"## {get_num_elements(period, content_type)}"
                return res_type, res_num

    with gr.Row():
        fig = plot_velocity_plotly(
            selected_period.value,
            selected_content_type.value,
        )
        fig.update_layout(
            template="plotly_white",
        )
        display_plotly = gr.Plot(fig)

        @gr.on(
            triggers=[selected_period.change, selected_content_type.change],
            inputs=[selected_period, selected_content_type],
            outputs=display_plotly,
        )
        def update_plotly_output(period, content_type):
            fig = plot_velocity_plotly(
                period,
                content_type,
            )
            fig.update_layout(
                template="plotly_white",
            )
            return fig


demo.launch()
