from flask import render_template
from app import app


@app.route('/')
def index():
    """
    Main page with API testing interface.
    """
    return render_template('index.html')


@app.route('/test')
def test_page():
    """
    Simple test page.
    """
    return render_template('index.html')
