with open('main.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Find the start and end of the upload_scrap function
start_marker = '@app.post("/upload_scrap")'
end_marker = '    return {"type": scrap_type'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print('Markers not found')
    print('Start found:', start_idx)
    print('End found:', end_idx)
else:
    # Find the end of the return statement
    newline_after_return = content.find('\n', end_idx)
    
    new_function = '''@app.post("/upload_scrap")
async def upload_scrap(file: UploadFile = File(...), seller_id: int = 1, category_override: str = ""):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
        
    path = f"uploads/{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Use category override if provided, otherwise classify with AI
    if category_override and category_override in ECO_POINTS_MAP:
        scrap_type = category_override
    else:
        scrap_type = classify(path)
    
    # Get eco points for this category
    points_earned = ECO_POINTS_MAP.get(scrap_type, 10)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE users SET eco_points = eco_points + ? WHERE id=?", (points_earned, seller_id))
    
    cursor.execute("""
    INSERT INTO scrap(seller_id,image,type,price,status)
    VALUES(?,?,?,?,?)
    """, (seller_id, path, scrap_type, 0.0, "available"))
    
    conn.commit()
    conn.close()

    return {"type": scrap_type, "message": f"Scrap uploaded and classified! You earned {points_earned} Eco Points.", "points_earned": points_earned}
'''
    
    content = content[:start_idx] + new_function + content[newline_after_return+1:]
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Backend fixed successfully')
