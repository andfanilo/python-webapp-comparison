from python_webapp_comparison import get_content_types
from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

import gradio as gr

periods = get_periods()
content_types = get_content_types()

css = """
.card {
    padding: 1rem;
    border: 1px solid #bbbbbb;
    border-radius: 12px;
}

.card__value p {
    font-size: 3rem;
    font-weight: bold;
}
"""


def build_plot(period, content_type):
    fig = plot_velocity_plotly(
        period,
        content_type,
    )
    fig.update_layout(
        template="plotly_white",
    )
    return fig


################################################
### LAYOUT
################################################

with gr.Blocks(css=css) as demo:
    title_row = gr.Row()
    greeting_row = gr.Row()
    filters_row = gr.Row()
    card_row = gr.Row()
    chart_row = gr.Row()
    preview_row = gr.Row()

    ################################################
    ### TITLE & GREETING
    ################################################

    with title_row:
        gr.Markdown("# Movie Analytics Dashboard")

    with greeting_row:
        name_input = gr.Textbox(
            label="Enter your name",
            container=False,
            scale=2,
        )
        greeting_output = gr.HTML(
            "Provide your name",
        )

    @gr.on(
        triggers=[name_input.change],
        inputs=[name_input],
        outputs=[greeting_output],
    )
    def greet_name(name):
        """On Change Name -> Greeting"""
        if not name:
            return "Provide your name"
        return f"Hello {name}!"

    ################################################
    ### DROPDOWN FILTERS
    ################################################

    with filters_row:
        selected_period = gr.Dropdown(
            periods,
            value=periods[0],
            label="Select period:",
            interactive=True,
            scale=2,
        )
        selected_content_type = gr.Radio(
            content_types,
            value=content_types[0],
            label="Select Content:",
            interactive=True,
            scale=1,
        )

    ################################################
    ### CARDS
    ################################################

    with card_row:
        count_card = gr.Column(elem_classes="card")
        views_card = gr.Column(elem_classes="card")
        hours_card = gr.Column(elem_classes="card")

    with count_card:
        display_content_type = gr.Markdown(
            f"{selected_content_type.value.capitalize()}s",
            elem_classes="card__title",
        )
        num_elements_output = gr.Markdown(
            f"{get_num_elements(selected_period.value, selected_content_type.value)}",
            elem_classes="card__value",
        )

    with views_card:
        gr.Markdown("Views", elem_classes="card__title")
        num_views_output = gr.Markdown(
            get_num_views(selected_period.value, selected_content_type.value),
            elem_classes="card__value",
        )

    with hours_card:
        gr.Markdown(
            "Hours Watched",
            elem_classes="card__title",
        )
        num_hours_output = gr.Markdown(
            get_hours_watch(selected_period.value, selected_content_type.value),
            elem_classes="card__value",
        )

    @gr.on(
        triggers=[selected_period.change, selected_content_type.change],
        inputs=[selected_period, selected_content_type],
        outputs=[display_content_type, num_elements_output],
    )
    def update_num_card(period, content_type):
        """On Change Period/Type -> Count Card title/value"""
        res_type = f"{selected_content_type.value.capitalize()}s"
        res_num = f"{get_num_elements(period, content_type)}"
        return res_type, res_num

    @gr.on(
        triggers=[selected_period.change, selected_content_type.change],
        inputs=[selected_period, selected_content_type],
        outputs=[num_views_output],
    )
    def update_views_card(period, content_type):
        """On Change Period/Type -> Views Card value"""
        res_num = f"{get_num_views(period, content_type)}"
        return res_num

    @gr.on(
        triggers=[selected_period.change, selected_content_type.change],
        inputs=[selected_period, selected_content_type],
        outputs=[num_hours_output],
    )
    def update_hours_card(period, content_type):
        """On Change Period/Type -> Hours Card value"""
        res_num = f"{get_hours_watch(period, content_type)}"
        return res_num

    ################################################
    ### CHART & DATAFRAME
    ################################################

    with chart_row:
        display_plotly = gr.Plot(
            build_plot(selected_period.value, selected_content_type.value)
        )

    @gr.on(
        triggers=[selected_period.change, selected_content_type.change],
        inputs=[selected_period, selected_content_type],
        outputs=display_plotly,
    )
    def build_plotly_figure(period, content_type):
        """On Change Period/Type -> Plotly Chart"""
        fig = build_plot(period, content_type)
        return fig

    with preview_row:
        data_preview = gr.DataFrame(
            preview_data(
                selected_period.value, selected_content_type.value, []
            ).to_pandas(),
        )

    @gr.on(
        triggers=[selected_period.change, selected_content_type.change],
        inputs=[selected_period, selected_content_type],
        outputs=data_preview,
    )
    def compute_data_preview(period, content_type):
        """On Change Period/Type -> Dataframe"""
        return preview_data(period, content_type, []).to_pandas()


demo.launch()
