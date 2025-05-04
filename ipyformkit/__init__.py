"""
IpyFormKit: Easy form creation with ipywidgets in Jupyter.
"""

__version__ = "0.1.0"

from .custom_widgets import *
from IPython.display import display, HTML, Javascript
from .core import Form

# Get the directory of this file (core.py)
module_dir = os.path.dirname(os.path.abspath(__file__))
stylesheets = [
    'custom_widgets.css',
    'ipyformkit.css'
]

for stylesheet in stylesheets:
    stylesheet = module_dir + os.sep + stylesheet
    if os.path.exists(stylesheet):
        with open(stylesheet, 'r') as f:
            css = f.read()
        display(HTML(f'<style>{css}</style>'))
    else:
        print(f"Warning: {stylesheet} not found. Custom styles will not be applied.")


# Force a reflow after styles are injected
display(Javascript("""
setTimeout(() => {
    document.body.offsetHeight; // trigger reflow
}, 10);
"""))