from python_webapp_comparison import get_hours_watch
from python_webapp_comparison import get_num_elements
from python_webapp_comparison import get_num_views
from python_webapp_comparison import get_periods
from python_webapp_comparison import plot_velocity_plotly
from python_webapp_comparison import preview_data

import panel as pn
pn.extension()

name = pn.widgets.TextInput(
    name="Name",
    placeholder="Give me your name",
    description="Lemme greet you!",
)

greeting = pn.rx("Hello {name}!").format(name=name)
greeting_output = pn.pane.Markdown(greeting)

greet_row = pn.Row(
    name, 
    greeting_output,
)

app = pn.Column(greet_row)

pn.template.FastListTemplate(
    title="Movie Dashboard",
    main=app,
).servable()
