#############################################################################
# internals.py
#
# This file contains internals for component templating. You do not need
# to understand this file, but are welcome to read through it if you want.
#
#############################################################################

import streamlit.components.v1 as components


def load_html_file(file_path):
    # Read an html file
    with open(file_path, 'r') as file:
        return file.read()


def safe_string(string):
    # Make the string "safe" by escaping quotes and a backslash character
    return ''.join(['\\' + c if c in ["'", '"', '\\'] else c for c in string])


def create_component(data, component_name, height=None, width=None, scrolling=False):
    # Read the HTML content from the file
    component_html = load_html_file(f'custom_components/{component_name}.html')

    # Inject CSS inline if a companion CSS file exists
    try:
        css = load_html_file(f'custom_components/static/{component_name}_css.css')
        component_html = component_html.replace(
            f'<link rel="stylesheet" href="static/{component_name}_css.css">',
            f'<style>{css}</style>'
        )
    except FileNotFoundError:
        pass

    # Inject JS inline if a companion JS file exists
    try:
        js = load_html_file(f'custom_components/static/{component_name}_js.js')
        component_html = component_html.replace(
            f'<script src="static/{component_name}_js.js"></script>',
            f'<script>{js}</script>'
        )
    except FileNotFoundError:
        pass

    # Replace the templates with the specified data
    for key in data:
        data_placeholder = "{{" + str(key) + "}}"
        component_html = component_html.replace(
            data_placeholder, safe_string(str(data[key])))

    # Have streamlit render the component
    components.html(component_html, width, height, scrolling)
