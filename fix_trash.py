with open('frontend/dashboard_user.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of the h3 for the transformation workflow
start_marker = '<h3'
if 'Scrap-to-Product Transformation Workflow' in content:
    h3_idx = content.find('Scrap-to-Product Transformation Workflow')
    # Backtrack to find the start of the div container
    # The container starts with the linear-gradient style
    start_search = content.rfind('<div', 0, h3_idx)
    # The specific div we want is the one with the border-radius: 20px
    while start_search != -1:
        if 'border-radius: 20px' in content[start_search:h3_idx]:
            break
        start_search = content.rfind('<div', 0, start_search)
    
    # Find the end of this section
    # The next major section is 'Maharashtra: India\'s #1 Recycling Hub'
    end_marker = 'Maharashtra: India\'s #1 Recycling Hub'
    end_search = content.find(end_marker, h3_idx)
    if end_search != -1:
        # Final end of the workflow div is before the next section
        end_idx = content.rfind('</div>', h3_idx, end_search)
        # We need to go up one level to close the container div
        end_idx = content.rfind('</div>', h3_idx, end_idx)
        
        new_section = '''<div
                    style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%); border-radius: 20px; padding: 2rem; border: 1px solid rgba(16, 185, 129, 0.15); margin-bottom: 2.5rem;">
                    <h3
                        style="color: var(--primary-green); margin-bottom: 0.5rem; font-size: 1.3rem; display: flex; align-items: center; gap: 0.75rem;">
                        <i class="fa-solid fa-arrow-right-arrow-left"></i> Scrap-to-Product Transformation Workflow
                    </h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 2rem;">See how raw scrap becomes a useful, everyday product through the recycling chain.</p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.5rem;">
                        <div style="background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.15);">
                            <div style="background: linear-gradient(90deg, #3b82f6, #6366f1); padding: 1rem 1.25rem; display: flex; align-items: center; gap: 0.75rem;"><i class="fa-solid fa-bottle-water" style="color: #fff; font-size: 1.4rem;"></i><span style="color: #fff; font-weight: 700;">Plastic Scrap (PET)</span></div>
                            <div style="padding: 1.25rem; display: flex; flex-direction: column; gap: 0.6rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #eff6ff; color: #3b82f6; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">🗑️ Collection</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">PET bottles from households & streets</span></div>
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #eff6ff; color: #3b82f6; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">🔄 Shredding</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Cleaned & shredded into PET flakes</span></div>
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #eff6ff; color: #3b82f6; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">🧵 Spinning</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Melted into polyester fibre for textiles</span></div>
                                <div style="background: #eff6ff; padding: 0.6rem 1rem; border-radius: 10px; margin-top: 0.4rem; font-size: 0.84rem; color: #3b82f6; font-weight: 600;"><i class="fa-solid fa-check-circle"></i> Final: T-shirts, Eco-bricks, Packaging</div>
                            </div>
                        </div>
                        <div style="background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(100,116,139,0.1); border: 1px solid rgba(100,116,139,0.15);">
                            <div style="background: linear-gradient(90deg, #475569, #64748b); padding: 1rem 1.25rem; display: flex; align-items: center; gap: 0.75rem;"><i class="fa-solid fa-industry" style="color: #fff; font-size: 1.4rem;"></i><span style="color: #fff; font-weight: 700;">Metal Scrap (Steel)</span></div>
                            <div style="padding: 1.25rem; display: flex; flex-direction: column; gap: 0.6rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #f1f5f9; color: #475569; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">🔨 Collection</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Old cars, appliances & construction scrap</span></div>
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #f1f5f9; color: #475569; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">⚡ Smelting</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Melted in electric arc furnace at 1600°C</span></div>
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #f1f5f9; color: #475569; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">⚒️ Casting</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Cast into ingots, rods & beams</span></div>
                                <div style="background: #f1f5f9; padding: 0.6rem 1rem; border-radius: 10px; margin-top: 0.4rem; font-size: 0.84rem; color: #475569; font-weight: 600;"><i class="fa-solid fa-check-circle"></i> Final: Rebar, car parts, bridges, appliances</div>
                            </div>
                        </div>
                        <div style="background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.15);">
                            <div style="background: linear-gradient(90deg, #7c3aed, #8b5cf6); padding: 1rem 1.25rem; display: flex; align-items: center; gap: 0.75rem;"><i class="fa-solid fa-microchip" style="color: #fff; font-size: 1.4rem;"></i><span style="color: #fff; font-weight: 700;">E-Waste (Electronics)</span></div>
                            <div style="padding: 1.25rem; display: flex; flex-direction: column; gap: 0.6rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #f5f3ff; color: #7c3aed; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">📱 Collection</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Old phones, TVs, PCBs & batteries</span></div>
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #f5f3ff; color: #7c3aed; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">🔬 Dismantling</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Manual & robotic disassembly</span></div>
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #f5f3ff; color: #7c3aed; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">⚗️ Refining</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Extraction of Gold, Silver, Palladium</span></div>
                                <div style="background: #f5f3ff; padding: 0.6rem 1rem; border-radius: 10px; margin-top: 0.4rem; font-size: 0.84rem; color: #7c3aed; font-weight: 600;"><i class="fa-solid fa-check-circle"></i> Final: New PCBs, jewellery, semiconductors</div>
                            </div>
                        </div>
                        <div style="background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.15);">
                            <div style="background: linear-gradient(90deg, #d97706, #f59e0b); padding: 1rem 1.25rem; display: flex; align-items: center; gap: 0.75rem;"><i class="fa-solid fa-newspaper" style="color: #fff; font-size: 1.4rem;"></i><span style="color: #fff; font-weight: 700;">Paper & Cardboard</span></div>
                            <div style="padding: 1.25rem; display: flex; flex-direction: column; gap: 0.6rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #fffbeb; color: #d97706; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">📦 Collection</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Newspapers, cartons & office waste</span></div>
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #fffbeb; color: #d97706; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">💧 Pulping</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Soaked in water to create pulp slurry</span></div>
                                <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.87rem;"><span style="background: #fffbeb; color: #d97706; padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 600; white-space: nowrap;">📝 Pressing</span><i class="fa-solid fa-arrow-right" style="color: #cbd5e1; flex-shrink: 0;"></i><span style="color: var(--text-muted);">Dried & pressed into new sheets</span></div>
                                <div style="background: #fffbeb; padding: 0.6rem 1rem; border-radius: 10px; margin-top: 0.4rem; font-size: 0.84rem; color: #d97706; font-weight: 600;"><i class="fa-solid fa-check-circle"></i> Final: Notebooks, packaging, tissue paper</div>
                            </div>
                        </div>
                    </div>
                </div>'''
        
        content = content[:start_search] + new_section + content[end_idx+6:]
        
        with open('frontend/dashboard_user.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Transformation section fixed.")
else:
    print("Transformation workflow marker not found.")
