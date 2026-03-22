import os

# Revert backend/main.py
with open('backend/main.py', 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

# Find the start of the relevant section
start_idx = -1
for i, line in enumerate(lines):
    if 'from ai_model import classify' in line:
        start_idx = i - 1 # Include the try:
        break

if start_idx != -1:
    new_tail = [
        'try:\n',
        '    from ai_model import classify\n',
        'except ImportError:\n',
        '    def classify(path):\n',
        '        return random.choice(["Plastic", "Metal", "Paper", "E-Waste"])\n',
        '\n',
        '@app.post("/upload_scrap")\n',
        'async def upload_scrap(file: UploadFile = File(...), seller_id: int = 1):\n',
        '    if not os.path.exists("uploads"):\n',
        '        os.makedirs("uploads")\n',
        '        \n',
        '    path = f"uploads/{file.filename}"\n',
        '    with open(path, "wb") as buffer:\n',
        '        shutil.copyfileobj(file.file, buffer)\n',
        '\n',
        '    scrap_type = classify(path)\n',
        '    \n',
        '    conn = get_db()\n',
        '    cursor = conn.cursor()\n',
        '    \n',
        '    # Simple award 10 points\n',
        '    cursor.execute("UPDATE users SET eco_points = eco_points + 10 WHERE id=?", (seller_id,))\n',
        '    \n',
        '    cursor.execute("""\n',
        '    INSERT INTO scrap(seller_id,image,type,price,status)\n',
        '    VALUES(?,?,?,?,?)\n',
        '    """, (seller_id, path, scrap_type, 0.0, "available"))\n',
        '    \n',
        '    conn.commit()\n',
        '    conn.close()\n',
        '\n',
        '    return {"type": scrap_type, "message": "Scrap uploaded and classified! You earned 10 Eco Points."}\n'
    ]
    
    # We replace everything from start_idx to the end of the file
    lines = lines[:start_idx] + new_tail
    
    with open('backend/main.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Backend reverted successfully")
else:
    print("Could not find start of section in main.py")

# Revert js/app.js
with open('js/app.js', 'r', encoding='utf-8-sig') as f:
    js_content = f.read()

# Revert submitScrap() function
import re
old_js_pattern = r'async function submitScrap\(\) \{[\s\S]+?showAlert\("Server connection failed", "error"\);\n    \}\n\}'
new_js = '''async function submitScrap() {
    const user = requireAuth('user');
    if (!user) return;
    
    const fileInput = document.getElementById("scrapFile");
    if (!fileInput.files[0]) {
        showAlert("Please select an image first", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    
    try {
        const res = await fetch(`${API_URL}/upload_scrap?seller_id=${user.id}`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        if (res.ok) {
            document.getElementById("scanResult").style.display = "block";
            document.getElementById("detectedType").textContent = data.type;
            document.getElementById("scanMessage").textContent = data.message;
            
            showAlert("Image classified successfully!", "success");
            refreshStats(); // Update eco points
        } else {
            showAlert("Upload failed", "error");
        }
    } catch (err) {
        showAlert("Server connection failed", "error");
    }
}'''

js_content = re.sub(old_js_pattern, new_js, js_content)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print("JavaScript reverted successfully")
