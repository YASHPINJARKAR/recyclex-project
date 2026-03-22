import re

# We need the version BEFORE my last restructure if possible, but I'll work with what I have and try to find missing parts in previous view_file calls if needed.
# Actually, I can probably reconstruct it.

def extract_block(text, start_marker, end_marker_tag='</div>'):
    start_idx = text.find(start_marker)
    if start_idx == -1: return None
    
    # Simple tag balancer
    depth = 0
    for i in range(start_idx, len(text)):
        if text[i:i+4] == '<div' or text[i:i+8] == '<section':
            depth += 1
        elif text[i:i+6] == '</div' or text[i:i+10] == '</section':
            depth -= 1
            if depth == 0:
                # Find the end of the closing tag
                end_tag_close = text.find('>', i)
                return text[start_idx:end_tag_close+1]
    return None

with open('frontend/dashboard_user.html', 'r', encoding='utf-8') as f:
    content = f.read()

# I need to recover the scripts. Since they are gone from the file, I'll use the content from Step 821
scripts = '''
    <script src="../js/app.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const user = requireAuth('user');
            if (user) {
                document.getElementById('userGreeting').textContent = `Hello, ${user.name}`;
                refreshStats();
                fetchPendingBids();

                // Open history if requested via URL
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.get('showHistory') === 'true') {
                    showUserHistory();
                    setTimeout(()=>document.getElementById('historyModal').scrollIntoView({behavior:'smooth', block:'start'}), 500);
                }
            }
        });
    </script>
'''

# Extract blocks from current (partially broken) content
eco_profile = extract_block(content, 'Eco Profile')
ai_scanner = extract_block(content, 'AI Waste Scanner')
market_prices = extract_block(content, 'Live Scrap Market Prices')
pending_offers = extract_block(content, 'Pending Scrap Offers')
services = extract_block(content, 'id="services"')
scrap_insights = extract_block(content, 'id="scrap-insights"')
history_modal = extract_block(content, 'id="historyModal"')
footer = extract_block(content, '<footer')

# Reconstruct Header
header_end = content.find('<div class="container"')
header = content[:header_end] + '<div class="container" style="margin-top: 2rem; display: flex; flex-direction: column; gap: 2rem;">'

# Reconstruct Body
# Note: Eco Profile and AI Scanner should be in a grid-2
top_grid = f'<div class="grid-2" style="gap: 1.5rem;">\n{eco_profile}\n{ai_scanner}\n</div>'

new_html = f"""{header}
    {top_grid}
    {market_prices if market_prices else ""}
    {pending_offers if pending_offers else ""}
    {services if services else ""}
    {scrap_insights if scrap_insights else ""}
</div> <!-- End container -->
</div> <!-- End main-wrapper -->
</div> <!-- End layout-wrapper -->

{history_modal if history_modal else ""}
{scripts}
{footer if footer else ""}
</body>
</html>
"""

with open('frontend/dashboard_user.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Dashboard fixed and scripts recovered.")
