import re

with open('frontend/dashboard_user.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Extract the components

# Header area (ends before <div class="container")
header_match = re.search(r'([\s\S]+?<div class="container"[\s\S]+?>)', content)
header = header_match.group(1) if header_match else ""

# First Grid (Eco Profile and AI Scanner)
# Ends before Live Scrap Market Prices
grid1_match = re.search(r'(<div class="grid-2">[\s\S]+?Live Scrap Market Prices[\s\S]*?</h2>)', content)
# We need to find the specific closing div for grid1
grid1_start = content.find('<div class="grid-2">')
grid1_end_search = content.find('Live Scrap Market Prices', grid1_start)
grid1_end = content.rfind('</div>', grid1_start, grid1_end_search)
# We need to go up one level to close the grid-2
grid1_end = content.rfind('</div>', grid1_start, grid1_end)
grid1 = content[grid1_start:grid1_end+6]

# Live Scrap Market Prices section
# Starts at <div class="glass-panel" followed by h2 Live Scrap Market Prices
prices_start = content.find('Live Scrap Market Prices')
prices_start = content.rfind('<div class="glass-panel', 0, prices_start)
prices_end_search = content.find('id="scrap-insights"', prices_start)
prices_end = content.rfind('</div>', prices_start, prices_end_search)
prices = content[prices_start:prices_end+6]

# Scrap Insights Section
# Everything inside <section id="scrap-insights">
insights_start = content.find('id="scrap-insights"')
insights_start = content.rfind('<section', 0, insights_start)
insights_end = content.find('</section>', insights_start)
insights_section_inner = content[insights_start:insights_end+10]

# Pre-existing script area and footer
footer_start = content.find('<footer')
footer = content[footer_start:]

# 2. Re-stitch with clean structure

new_content = header + "\n"
new_content += "                " + grid1 + "\n\n"
new_content += "                " + prices + "\n\n"
new_content += "                " + insights_section_inner + "\n\n"
new_content += "            </div> <!-- End container -->\n"
new_content += "        </div> <!-- End main-wrapper -->\n"
new_content += "    </div> <!-- End layout-wrapper -->\n"

# Add the modals (Privacy, History) and scripts
# We need to extract them from the original content to make sure they aren't lost
modals_search = re.search(r'(<section id="historyModal"[\s\S]+?</section>)', content)
if modals_search:
    new_content += "    " + modals_search.group(1) + "\n"

new_content += "\n    " + footer

with open('frontend/dashboard_user.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Dashboard restructured successfully.")
