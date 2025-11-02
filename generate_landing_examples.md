# Generate Landing Page Examples - Step by Step

You have 4 "before" photos saved. Now let's generate the graduation versions!

## ✅ Current Status

- ✅ 4 example photos in `webapp/frontend/public/examples/before/`
  - example-1.jpg (5.2MB)
  - example-2.jpg (3.4MB)
  - example-3.jpg (364KB)
  - example-4.jpg (2.4MB)

- Backend server: Starting on http://localhost:8000
- Frontend server: Starting on http://localhost:3000

---

## 🎯 Option 1: Generate via Web Interface (Easiest - 10 minutes)

### Step 1: Open Your Browser
```
Visit: http://localhost:3000
```

### Step 2: Login (if needed)
- If not logged in, login or register a test account
- You'll need an account to use the generation feature

### Step 3: Generate Each Photo

**For example-1.jpg:**
1. Go to http://localhost:3000/generate
2. Upload: `webapp/frontend/public/examples/before/example-1.jpg`
3. Select University: Any UK university (e.g., "Loughborough University")
4. Select Degree Level: "Bachelors"
5. Click "Generate"
6. Wait for generation to complete
7. Download the result
8. Save as: `webapp/frontend/public/examples/after/example-1.jpg`

**Repeat for example-2, example-3, and example-4**

---

## 🎯 Option 2: Generate via Batch Script (Faster - 5 minutes)

If you want to automate this, I can create a script that uses your backend API directly.

### Requirements:
- You need to be logged in
- Get your JWT token from the browser (F12 → Application → Local Storage → `auth_token`)

### Script:
```bash
#!/bin/bash

# Get your auth token from browser and paste here:
AUTH_TOKEN="paste_your_token_here"

# API endpoint
API_URL="http://localhost:8000/api/generation"

# Generate each example
for i in 1 2 3 4; do
  echo "🎓 Generating example-$i..."

  # Upload and generate
  RESPONSE=$(curl -s -X POST "$API_URL/generate" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -F "file=@webapp/frontend/public/examples/before/example-$i.jpg" \
    -F "university=Loughborough University" \
    -F "degree_level=Bachelors")

  # Extract job ID from response
  JOB_ID=$(echo $RESPONSE | jq -r '.id')

  echo "  Job ID: $JOB_ID"
  echo "  Waiting for completion..."

  # Poll until complete (adjust timeout as needed)
  while true; do
    STATUS=$(curl -s "$API_URL/status/$JOB_ID" \
      -H "Authorization: Bearer $AUTH_TOKEN" | jq -r '.status')

    echo "  Status: $STATUS"

    if [ "$STATUS" = "completed" ]; then
      break
    elif [ "$STATUS" = "failed" ]; then
      echo "  ❌ Generation failed!"
      break
    fi

    sleep 3
  done

  # Download result
  if [ "$STATUS" = "completed" ]; then
    echo "  ✅ Downloading result..."
    curl -s "$API_URL/download/$JOB_ID" \
      -H "Authorization: Bearer $AUTH_TOKEN" \
      -o "webapp/frontend/public/examples/after/example-$i.jpg"
    echo "  ✅ Saved to examples/after/example-$i.jpg"
  fi

  echo ""
done

echo "🎉 All examples generated!"
```

Save as `generate_examples.sh` and run:
```bash
chmod +x generate_examples.sh
./generate_examples.sh
```

---

## 🎯 Option 3: Use Python Batch Script (Most Reliable)

If you have Python, here's a more robust script:

```python
#!/usr/bin/env python3
import requests
import time
import os

# Configuration
API_URL = "http://localhost:8000/api"
AUTH_TOKEN = "paste_your_token_here"  # Get from browser local storage

HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}"
}

# Universities to use (you can change these)
CONFIGS = [
    {"university": "Loughborough University", "degree_level": "Bachelors"},
    {"university": "Westminster University", "degree_level": "Bachelors"},
    {"university": "Wolverhampton University", "degree_level": "Masters"},
    {"university": "Keele University", "degree_level": "Bachelors"},
]

def generate_photo(input_path, output_path, config):
    """Generate a graduation photo."""
    print(f"🎓 Generating: {os.path.basename(input_path)}")

    # Upload and start generation
    with open(input_path, 'rb') as f:
        files = {'file': f}
        data = {
            'university': config['university'],
            'degree_level': config['degree_level']
        }

        response = requests.post(
            f"{API_URL}/generation/generate",
            headers=HEADERS,
            files=files,
            data=data
        )

        if response.status_code != 200:
            print(f"  ❌ Failed to start generation: {response.text}")
            return False

        job_id = response.json()['id']
        print(f"  Job ID: {job_id}")

    # Poll for completion
    print("  Waiting for completion...", end='', flush=True)
    while True:
        status_response = requests.get(
            f"{API_URL}/generation/status/{job_id}",
            headers=HEADERS
        )

        status = status_response.json()['status']

        if status == 'completed':
            print(" ✅")
            break
        elif status == 'failed':
            print(" ❌ Failed!")
            return False

        print(".", end='', flush=True)
        time.sleep(3)

    # Download result
    print("  Downloading...", end='', flush=True)
    download_response = requests.get(
        f"{API_URL}/generation/download/{job_id}",
        headers=HEADERS
    )

    if download_response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(download_response.content)
        print(f" ✅ Saved to {output_path}")
        return True
    else:
        print(f" ❌ Download failed: {download_response.status_code}")
        return False

def main():
    """Generate all 4 examples."""
    base_path = "webapp/frontend/public/examples"

    for i in range(1, 5):
        input_path = f"{base_path}/before/example-{i}.jpg"
        output_path = f"{base_path}/after/example-{i}.jpg"

        if not os.path.exists(input_path):
            print(f"❌ Missing: {input_path}")
            continue

        config = CONFIGS[i-1]
        success = generate_photo(input_path, output_path, config)

        if success:
            print(f"✅ Example {i} complete!\n")
        else:
            print(f"❌ Example {i} failed!\n")

        # Small delay between generations
        time.sleep(1)

    print("🎉 All examples generated!")

if __name__ == "__main__":
    main()
```

Save as `generate_examples.py` and run:
```bash
python3 generate_examples.py
```

---

## 📋 What You Need to Do

**Choose ONE of the options above:**

1. **Option 1 (Recommended for first time)**: Use web interface
   - Most visual
   - Easiest to verify results
   - Takes ~10 minutes

2. **Option 2**: Use bash script
   - Faster
   - Requires getting auth token
   - Takes ~5 minutes

3. **Option 3**: Use Python script
   - Most robust
   - Best error handling
   - Takes ~5 minutes

**After generation, you should have:**
```
webapp/frontend/public/examples/
├── before/
│   ├── example-1.jpg ✅
│   ├── example-2.jpg ✅
│   ├── example-3.jpg ✅
│   └── example-4.jpg ✅
└── after/
    ├── example-1.jpg ← Need to generate
    ├── example-2.jpg ← Need to generate
    ├── example-3.jpg ← Need to generate
    └── example-4.jpg ← Need to generate
```

---

## 🧪 Testing After Generation

Once all 4 "after" photos are generated:

1. **Refresh your homepage:**
   ```
   Visit: http://localhost:3000
   ```

2. **You should see:**
   - Hero section with before/after slider working
   - 4 example selector buttons
   - Draggable slider to compare before/after
   - All photos loading properly

3. **Test on mobile:**
   - Open Chrome DevTools (F12)
   - Toggle device toolbar (Ctrl+Shift+M)
   - Select "iPhone 12 Pro" or similar
   - Test touch dragging on slider

---

## 🎨 Optional: Optimize Images

Your photos are quite large. You can optimize them:

```bash
# Install ImageMagick if not already installed
brew install imagemagick  # macOS
# or: sudo apt-get install imagemagick  # Linux

# Optimize all images
cd webapp/frontend/public/examples/before
mogrify -resize 1600x -quality 85 *.jpg

cd ../after
mogrify -resize 1600x -quality 85 *.jpg
```

This will:
- Resize to max 1600px width
- Compress to 85% quality (still looks great)
- Reduce file sizes significantly (faster page load)

---

## ❓ Troubleshooting

**Backend not starting?**
```bash
# Check what's running on port 8000
lsof -i :8000

# Kill existing process if needed
kill -9 <PID>

# Restart
cd webapp/backend
poetry run uvicorn app.main:app --reload --port 8000
```

**Frontend not starting?**
```bash
# Check what's running on port 3000
lsof -i :3000

# Kill and restart
cd webapp/frontend
npm run dev
```

**Can't login?**
- Register a new test account
- Or use existing credentials from previous testing

**Generation fails?**
- Check backend logs for errors
- Verify Gemini API key is set
- Try with a smaller image first
- Check if Redis/Celery is running

---

## 🚀 Quick Start (Web Interface Method)

The absolute fastest way right now:

1. Open: http://localhost:3000
2. Login/Register
3. Go to /generate
4. Upload example-1.jpg → Generate → Download → Save to after/example-1.jpg
5. Repeat for examples 2, 3, and 4
6. Refresh homepage to see results!

**Total time: ~10 minutes**

Let me know which option you'd like to use and I can help you through it! 🎯
