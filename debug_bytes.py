with open('frontend/dashboard_user.html', 'rb') as f:
    raw = f.read()

# Search for common garbled starts \xc3\xb0 (ð) or \xc3\xa2 (â)
idxs = [i for i, b in enumerate(raw) if b in [0xc3]] # Start of many multibyte chars

for idx in idxs[:20]: # Show first 20
    chunk = raw[idx:idx+15]
    print(f"Offset {idx}: {chunk}")
