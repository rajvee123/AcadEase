import os
import re

TEMPLATES_DIR = "templates"

def update_css_links(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Regex to find <link> tags with href="css/..."
    pattern = r'(<link\s+[^>]*href=")(css/[^"]+)(".*?>)'

    # Replace with Django's static tag
    updated_content = re.sub(pattern, r'\1{% static "\2" %}\3', content)

    if updated_content != content:  # Only overwrite if changes were made
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(updated_content)
        print(f"Updated: {file_path}")

def process_templates():
    for root, _, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                update_css_links(file_path)

if __name__ == "__main__":
    print("Updating CSS links in HTML files...")
    process_templates()
    print("Update complete!")
