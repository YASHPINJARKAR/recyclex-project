import os
import re

frontend_dir = 'frontend'

def fix_double_encoding(text):
    def replace_match(match):
        s = match.group(0)
        try:
            # If it's double-encoded, it should be representable in latin-1
            # and then decodable as utf-8.
            return s.encode('latin-1').decode('utf-8')
        except:
            # If it fails (e.g. contains real Hindi/Marathi), leave it alone
            return s

    # This regex matches sequences of Latin-1 characters that often result from broken UTF-8
    # We target characters from \u0080 to \u00ff (Latin-1 Supplement)
    return re.sub(r'[\u0080-\u00ff]+', replace_match, text)

for root, dirs, files in os.walk(frontend_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # Apply the smart fix
            content = fix_double_encoding(content)
            
            # Plus the Rupee symbol and few others that might not fit the regex perfectly
            # (Though 'â‚¹' should fit the regex)
            
            # Ensure language switcher is restricted
            if 'id="languageSwitcher"' in content:
                content = re.sub(r'(<select id="languageSwitcher"[\s\S]+?>)[\s\S]+?</select>', r'\1\n                        <option value="en">English</option>\n                        <option value="hi">हिंदी</option>\n                        <option value="mr">मराठी</option>\n                    </select>', content)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed {file}")

# Fix app.js
js_path = 'js/app.js'
if os.path.exists(js_path):
    with open(js_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    content = fix_double_encoding(content)
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed js/app.js")
