import os
import re

def fix_json_ld(root_dir):
    # Regex to extract JSON-LD content blocks
    # We use a capturing group for the content to modify it
    script_pattern = re.compile(r'(<script type="application/ld\+json">)([\s\S]*?)(</script>)', re.IGNORECASE)
    
    # Regex to find URLs to fix inside the JSON content
    # Matches strings starting with https://gemini-vip.top/ and ending with .html
    # We match "https://..." to ensure we are inside a JSON string value
    url_pattern = re.compile(r'"(https://gemini-vip\.top/[^"]*?\.html)"')

    def fix_url(match):
        full_url = match.group(1) # content inside quotes
        if full_url.endswith('/index.html'):
            new_url = full_url[:-10] # remove /index.html
            # Ensure it doesn't end with a slash if we want to match fix_links.py behavior which likely stripped it?
            # Actually, let's keep it clean. 
            # If the canonical says /blog/, we might want /blog/.
            # But let's follow the previous pattern: strip /index.html completely.
            # https://site/blog/index.html -> https://site/blog
        elif full_url.endswith('.html'):
            new_url = full_url[:-5] # remove .html
        else:
            return match.group(0) # No change
        
        return f'"{new_url}"'

    def fix_block(match):
        start_tag = match.group(1)
        content = match.group(2)
        end_tag = match.group(3)
        
        # Apply URL fixing to the content
        new_content = url_pattern.sub(fix_url, content)
        
        return f'{start_tag}{new_content}{end_tag}'

    count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = script_pattern.sub(fix_block, content)
                
                if new_content != content:
                    print(f"Fixing JSON-LD in {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    count += 1
    
    print(f"Total files fixed: {count}")

if __name__ == "__main__":
    fix_json_ld(".")
