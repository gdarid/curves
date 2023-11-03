from streamlit.testing.v1 import AppTest


def test_app():
    at = AppTest.from_file("streamlit_app.py")
    at.run()
    assert not at.exception
