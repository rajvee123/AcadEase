import os
import re

# Define mapping of filenames to Django URL names
url_mappings = {
    "index.html": "home",
    "about.html": "about",
    "contact.html": "contact",
    "courses.html": "courses",
    "team.html": "team",
    "testimonial.html": "testimonial"
}

# Path where HTML files are stored (Update this if needed)
TEMPLATES_DIR = "templates"  # Change if your templates are in another location

# Regex to match href links like href="about.html"
pattern = re.compile(r'href="([^"]+\.html)"')

def update_html_links(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace static href links with Django template tags
    def replace_link(match):
        filename = match.group(1)
        if filename in url_mappings:
            return f'href="{{% url \'{url_mappings[filename]}\' %}}"'
        return match.group(0)

    new_content = pattern.sub(replace_link, content)

    # Save the updated file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

def process_all_html_files():
    for root, _, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                update_html_links(file_path)
                print(f"Updated: {file_path}")

if __name__ == "__main__":
    process_all_html_files()
    print("✅ All HTML files updated successfully!")
