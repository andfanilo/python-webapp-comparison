# Trying out all Python Data Web Frameworks

![](./images/streamlit.PNG)

```sh
# Build .venv environment
uv sync

# Download data
cd data
uv run pydytuesday tt-download 2025-07-29

# Run apps
uv run streamlit run streamlit/streamlit_app.py
uv run gradio gradio/gradio_app.py
```

