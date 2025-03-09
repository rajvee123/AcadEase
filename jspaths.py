import os
import re

# Define the directory containing the templates
TEMPLATES_DIR = "templates"

def update_js_paths(file_path):
    """Update JavaScript paths in an HTML file to use Django's static template tag."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Ensure {% load static %} is at the top
    if "{% load static %}" not in content:
        content = "{% load static %}\n" + content

    # Regex pattern to match <script src="..."></script>
    script_pattern = re.compile(r'<script\s+src="(lib/.*?\.js)"></script>')

    # Replace script paths with Django static tag
    content = script_pattern.sub(r'<script src="{% static \'\1\' %}"></script>', content)

    # Write the updated content back to the file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Updated: {file_path}")

# Recursively find all HTML files in the templates directory
for root, _, files in os.walk(TEMPLATES_DIR):
    for file in files:
        if file.endswith(".html"):
            update_js_paths(os.path.join(root, file))

print("JavaScript paths updated successfully!")
