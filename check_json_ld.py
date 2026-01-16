import os
import json
import re

def check_json_ld(root_dir):
    files_with_issues = []
    
    # Regex to extract JSON-LD content
    json_ld_pattern = re.compile(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', re.DOTALL)
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                matches = json_ld_pattern.findall(content)
                for json_str in matches:
                    try:
                        data = json.loads(json_str)
                        if has_html_suffix(data):
                            files_with_issues.append(file_path)
                            print(f"Found .html suffix in JSON-LD: {file_path}")
                            break # Move to next file
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in {file_path}")

    if not files_with_issues:
        print("No .html suffixes found in JSON-LD.")

def has_html_suffix(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if has_html_suffix(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if has_html_suffix(item):
                return True
    elif isinstance(data, str):
        # Check if it looks like a URL and ends with .html
        # We want to avoid false positives, but for this site, most internal links might be relative or absolute
        if ".html" in data and ("gemini-vip.top" in data or data.startswith("/") or data.startswith("http")):
             if data.strip().endswith(".html"):
                 print(f"  Match: {data}")
                 return True
    return False

if __name__ == "__main__":
    check_json_ld(".")
