with open('frontend/dashboard_user.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of the grid
start_marker = '<div class="grid-4-diagram">'
start_idx = content.find(start_marker)

# Find the next section start to know where the grid panel ends
# The next section is "Pending Scrap Offers"
end_marker = 'Pending Scrap Offers'
panel_end_idx = content.find(end_marker)

if start_idx != -1 and panel_end_idx != -1:
    # We want to keep everything before start_idx
    # and everything after the panel closing
    
    # Backtrack from panel_end_idx to find the closing tags of the grid and its container
    # The structure is usually:
    # <div class="grid-4-diagram"> ... </div>
    # </div> <!-- panel -->
    
    # Let's find the last </div> before the "Pending Scrap Offers" h2
    last_div_idx = content.rfind('</div>', 0, panel_end_idx)
    second_last_div_idx = content.rfind('</div>', 0, last_div_idx)
    
    new_grid = '''<div class="grid-4-diagram">
                <div class="price-box">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">♻️</div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: var(--text-main);">Plastic</div>
                    <div style="color: var(--primary-green); font-weight: 700; margin-top: 0.5rem;">₹5.20 / kg</div>
                </div>
                <div class="price-box">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">📰</div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: var(--text-main);">Paper</div>
                    <div style="color: var(--primary-green); font-weight: 700; margin-top: 0.5rem;">₹10.80 / kg</div>
                </div>
                <div class="price-box">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">📦</div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: var(--text-main);">Cardboard</div>
                    <div style="color: var(--primary-green); font-weight: 700; margin-top: 0.5rem;">₹25.50 / kg</div>
                </div>
                <div class="price-box">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">💻</div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: var(--text-main);">E-Waste</div>
                    <div style="color: var(--primary-green); font-weight: 700; margin-top: 0.5rem;">₹4.50 / kg</div>
                </div>
                <div class="price-box">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">⚡</div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: var(--text-main);">Copper</div>
                    <div style="color: var(--primary-green); font-weight: 700; margin-top: 0.5rem;">₹70.00 / kg</div>
                </div>
                <div class="price-box">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">⚒️</div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: var(--text-main);">Iron</div>
                    <div style="color: var(--primary-green); font-weight: 700; margin-top: 0.5rem;">₹30.90 / kg</div>
                </div>
                <div class="price-box">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">🍷</div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: var(--text-main);">Glass</div>
                    <div style="color: var(--primary-green); font-weight: 700; margin-top: 0.5rem;">₹15.30 / kg</div>
                </div>
                <div class="price-box">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">🥫</div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: var(--text-main);">Aluminum</div>
                    <div style="color: var(--primary-green); font-weight: 700; margin-top: 0.5rem;">₹35.50 / kg</div>
                </div>
            </div>
        </div>\n\n        '''
    
    # Replace from start_idx to last_div_idx + 6 (length of </div>)
    content = content[:start_idx] + new_grid + content[last_div_idx+6:]

# Final cleanup of all garbled characters in the remaining content
content = content.replace('â‚¹', '₹')
content = content.replace('ðŸ—‘ï¸ ', '🗑️')
content = content.replace('ðŸ”„', '🔄')
content = content.replace('ðŸ§µ', '🧵')
content = content.replace('âš¡', '⚡')
content = content.replace('ðŸ —ï¸ ', '⚒️')
content = content.replace('ðŸ±', '📱')
content = content.replace('ðŸ“±', '📱')
content = content.replace('ðŸ”¬', '🔬')
content = content.replace('âš—ï¸ ', '⚗️')
content = content.replace('ðŸ“¦', '📦')
content = content.replace('ðŸ’§', '💧')
content = content.replace('ðŸ“ ', '📜')
content = content.replace('â€”', '—')

with open('frontend/dashboard_user.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Dashboard HTML cleaned thoroughly.")
