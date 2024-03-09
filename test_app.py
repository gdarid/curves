import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.filterwarnings("ignore:coroutine")
def test_app():
    at = AppTest.from_file("streamlit_app.py").run()
    at.button[0].click().run()
