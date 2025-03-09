import os
import re

# Correct path to your templates folder
TEMPLATES_DIR = r"C:\Users\rajve\OneDrive\Desktop\AcadEase\templates"

def update_static_tags(file_path):
    """Updates <img> and <link> tags to use Django's static template tag."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Update <img> tags: src="img/example.jpg" → src="{% static 'img/example.jpg' %}"
        updated_content = re.sub(
            r'(<img[^>]+src=["\'])(?!http|https|/{% static)(img/[^"\']+)(["\'])',
            r'\1{% static "\2" %}\3',
            content
        )

        # Update <link> tags (for favicon and stylesheets): href="img/favicon.ico" → href="{% static 'img/favicon.ico' %}"
        updated_content = re.sub(
            r'(<link[^>]+href=["\'])(?!http|https|/{% static)(img/[^"\']+)(["\'])',
            r'\1{% static "\2" %}\3',
            updated_content
        )

        # Write the updated content back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(updated_content)

        print(f"✅ Updated: {file_path}")
    
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")

def update_all_templates():
    """Goes through all HTML files in the templates directory and updates image and link paths."""
    for root, _, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                update_static_tags(file_path)

if __name__ == "__main__":
    update_all_templates()
    print("🚀 All image and link paths updated successfully!")
