import os
import re

# Set the correct path to your HTML files
HTML_DIR = r"C:\Users\rajve\OneDrive\Desktop\AcadEase\templates"

def fix_static_paths():
    """Fix unnecessary escape characters in `{% static %}` paths."""
    for filename in os.listdir(HTML_DIR):
        if filename.endswith(".html"):
            file_path = os.path.join(HTML_DIR, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Fix the incorrectly escaped {% static %} paths
            content = re.sub(r"\{% static \\\'(.*?)\\\' %\}", r"{% static '\1' %}", content)

            # Write the corrected content back to the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

            print(f"✅ Fixed: {filename}")

if __name__ == "__main__":
    fix_static_paths()
    print("\n🎉 All HTML files corrected successfully!")
