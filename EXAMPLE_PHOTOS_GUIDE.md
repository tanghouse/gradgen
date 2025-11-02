# Guide: Generating Licensed Example Photos for Landing Page

## ⚖️ Legal Considerations

When creating example photos for commercial use (landing page, marketing), you need to consider:

1. **Source Photo License**: Permission to use the original photo
2. **AI-Generated Derivative**: Whether you can create and publish AI-modified versions
3. **Commercial Use**: Whether you can use it for marketing/advertising
4. **Model Release**: Permission from the person in the photo

---

## ✅ Recommended Approach: Unsplash Photos

### Why Unsplash is Perfect for This:

**Unsplash License (Best Option):**
- ✅ Free to use for commercial purposes
- ✅ No attribution required (but appreciated)
- ✅ Can modify, remix, and create derivative works
- ✅ Can use in marketing and advertising
- ✅ No need to track down model releases

**Important Unsplash Terms:**
- ❌ Cannot compile photos to replicate Unsplash
- ❌ Cannot sell unmodified photos
- ✅ CAN use modified/AI-generated versions for marketing
- ✅ CAN use as examples/demos for your service

**Source:** [Unsplash License](https://unsplash.com/license)

---

## 🎯 Step-by-Step: Proper Licensed Examples

### Method 1: Use Your Existing System (Recommended)

**If you already have GradGen running:**

1. **Download Unsplash Photos**
   ```bash
   # Create a downloads folder
   mkdir -p unsplash_downloads
   ```

2. **Visit Unsplash and Download**
   - Go to: https://unsplash.com/s/photos/professional-portrait
   - Filter by orientation: "Portrait"
   - Look for high-quality professional headshots
   - Download 4 diverse photos (different genders, ages, ethnicities)
   - Click "Download free" button (this is important for license compliance)

3. **Save Photos Properly**
   ```bash
   # Save downloaded photos with proper names
   mv ~/Downloads/photo-1234-xyz.jpg unsplash_downloads/original-1.jpg
   mv ~/Downloads/photo-5678-abc.jpg unsplash_downloads/original-2.jpg
   mv ~/Downloads/photo-9012-def.jpg unsplash_downloads/original-3.jpg
   mv ~/Downloads/photo-3456-ghi.jpg unsplash_downloads/original-4.jpg
   ```

4. **Generate Graduation Versions Using Your System**

   **Option A: Via API (if backend is running)**
   ```bash
   # Start your backend
   cd webapp/backend
   poetry run uvicorn app.main:app --reload

   # In another terminal, use curl to generate
   curl -X POST "http://localhost:8000/api/generation/generate" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@unsplash_downloads/original-1.jpg" \
     -F "university=Loughborough University" \
     -F "degree_level=Bachelors"

   # Download the generated result
   # Save to webapp/frontend/public/examples/after/example-1.jpg
   ```

   **Option B: Via Frontend (easier)**
   ```bash
   # Start frontend
   cd webapp/frontend
   npm run dev

   # Go to http://localhost:3000/generate
   # Upload each Unsplash photo
   # Generate graduation versions
   # Download results
   # Save to examples/after/
   ```

5. **Copy to Public Directory**
   ```bash
   # Copy originals to 'before' folder
   cp unsplash_downloads/original-1.jpg webapp/frontend/public/examples/before/example-1.jpg
   cp unsplash_downloads/original-2.jpg webapp/frontend/public/examples/before/example-2.jpg
   cp unsplash_downloads/original-3.jpg webapp/frontend/public/examples/before/example-3.jpg
   cp unsplash_downloads/original-4.jpg webapp/frontend/public/examples/before/example-4.jpg

   # Generated versions should already be in examples/after/
   ```

6. **Keep Attribution Record (Optional but Good Practice)**
   ```bash
   # Create a file tracking the sources
   cat > webapp/frontend/public/examples/ATTRIBUTIONS.txt << 'EOF'
   Example photos sourced from Unsplash (https://unsplash.com)

   Example 1: Photo by [Photographer Name] on Unsplash (link to photo)
   Example 2: Photo by [Photographer Name] on Unsplash (link to photo)
   Example 3: Photo by [Photographer Name] on Unsplash (link to photo)
   Example 4: Photo by [Photographer Name] on Unsplash (link to photo)

   All photos used under Unsplash License (https://unsplash.com/license)
   Graduation versions generated using GradGen.AI technology
   EOF
   ```

---

### Method 2: Create Your Own Photos (Most Control)

**If you want 100% control and zero licensing concerns:**

1. **Take Your Own Photos**
   - Ask friends/family to model
   - Take professional-looking headshots with good lighting
   - Get written consent for commercial use

2. **Model Release Template**
   ```
   I, [Name], grant [Your Company] permission to use my likeness in photographs
   for marketing and promotional purposes, including but not limited to:
   - Website demonstrations
   - Marketing materials
   - Social media

   Signed: _______________  Date: _______________
   ```

3. **Generate Graduation Versions**
   - Use your GradGen system as in Method 1
   - Save to examples folders

**Pros:**
- ✅ Complete control
- ✅ No licensing concerns
- ✅ Can get exactly the diversity you want

**Cons:**
- ❌ Time-consuming
- ❌ Requires photography skills/equipment
- ❌ Need to coordinate with models

---

### Method 3: Use AI-Generated Faces (Questionable)

**This Person Does Not Exist / Generated Photos:**

⚠️ **Caution:** While technically you could use AI-generated faces:
- Legal gray area for commercial use
- Some services prohibit commercial use
- Potential ethical concerns
- May look "uncanny" to users

**Not Recommended** for a professional landing page.

---

## 📸 Recommended Unsplash Photos (As of 2025)

Here are some search strategies to find good examples:

### Search Terms:
- "professional headshot male"
- "professional headshot female"
- "business portrait"
- "corporate headshot diverse"
- "professional portrait Asian"
- "professional portrait Black"
- "professional portrait mature"

### Quality Criteria:
✅ Front-facing or 3/4 angle
✅ Clear facial features
✅ Good lighting (soft, even)
✅ Neutral or simple background
✅ Professional attire
✅ Natural expression (slight smile okay)
✅ High resolution (2000px+ width)
✅ Half-body or head/shoulders composition

### Diversity Checklist:
- [ ] At least 1 male
- [ ] At least 1 female
- [ ] Different age ranges (20s, 30s, 40s+)
- [ ] Different ethnicities
- [ ] Different styles (formal, casual-professional)

---

## 🔧 Practical Script to Download & Generate

Here's a complete script you can use:

```bash
#!/bin/bash
# generate_examples.sh

# 1. Create directories
mkdir -p unsplash_downloads
mkdir -p webapp/frontend/public/examples/before
mkdir -p webapp/frontend/public/examples/after

echo "📥 Step 1: Download Photos from Unsplash"
echo "Go to: https://unsplash.com/s/photos/professional-headshot"
echo "Download 4 photos and save them to unsplash_downloads/ as:"
echo "  - original-1.jpg"
echo "  - original-2.jpg"
echo "  - original-3.jpg"
echo "  - original-4.jpg"
echo ""
read -p "Press Enter when you've downloaded the photos..."

# 2. Copy to before folder
echo "📋 Step 2: Copying originals to 'before' folder..."
cp unsplash_downloads/original-1.jpg webapp/frontend/public/examples/before/example-1.jpg
cp unsplash_downloads/original-2.jpg webapp/frontend/public/examples/before/example-2.jpg
cp unsplash_downloads/original-3.jpg webapp/frontend/public/examples/before/example-3.jpg
cp unsplash_downloads/original-4.jpg webapp/frontend/public/examples/before/example-4.jpg

echo "✅ Originals copied!"

# 3. Generate graduation versions
echo "🎓 Step 3: Generate graduation versions"
echo "Option A: Use your running GradGen system via the web interface"
echo "  1. Go to http://localhost:3000/generate"
echo "  2. Upload each example-N.jpg from examples/before/"
echo "  3. Download results and save to examples/after/"
echo ""
echo "Option B: Use the batch generation script (if you have one)"
echo ""
read -p "Press Enter when you've generated all 4 graduation photos..."

# 4. Verify
echo "🔍 Step 4: Verifying files..."
MISSING=0

for i in 1 2 3 4; do
  if [ ! -f "webapp/frontend/public/examples/before/example-$i.jpg" ]; then
    echo "❌ Missing: examples/before/example-$i.jpg"
    MISSING=1
  fi

  if [ ! -f "webapp/frontend/public/examples/after/example-$i.jpg" ]; then
    echo "❌ Missing: examples/after/example-$i.jpg"
    MISSING=1
  fi
done

if [ $MISSING -eq 0 ]; then
  echo "✅ All 8 files present!"
  echo ""
  echo "🎨 Step 5: Optimize images for web (optional)"
  echo "If you have ImageMagick installed:"
  echo "  cd webapp/frontend/public/examples/before && mogrify -resize 1600x -quality 85 *.jpg"
  echo "  cd ../after && mogrify -resize 1600x -quality 85 *.jpg"
  echo ""
  echo "🚀 Ready to test! Run: cd webapp/frontend && npm run dev"
else
  echo "⚠️  Some files are missing. Please complete the steps above."
fi
```

Save this as `generate_examples.sh` and run:
```bash
chmod +x generate_examples.sh
./generate_examples.sh
```

---

## 🎨 Alternative: Pexels or Pixabay

**Pexels License:**
- ✅ Free for commercial use
- ✅ Can modify and create derivatives
- ✅ No attribution required
- Similar to Unsplash

**Pixabay License:**
- ✅ Free for commercial use
- ✅ Can modify
- ✅ No attribution required
- More restrictive than Unsplash/Pexels

**Recommendation:** Stick with **Unsplash** - it's the most permissive and well-documented.

---

## ⚠️ What NOT to Do

❌ **Google Images**: Most are copyrighted, even with usage rights filter
❌ **Stock Photo Services without License**: Getty, Shutterstock without purchasing
❌ **Social Media Photos**: Instagram, Facebook, LinkedIn (without explicit permission)
❌ **Celebrity Photos**: Almost always require licensing
❌ **University Official Photos**: Usually copyrighted by the institution

---

## 📝 Summary: The Right Way

**Recommended Workflow:**

1. ✅ Download 4 photos from **Unsplash** (click "Download free")
2. ✅ Save photographer names and links (optional but courteous)
3. ✅ Use your **GradGen system** to generate graduation versions
4. ✅ Save originals to `examples/before/`
5. ✅ Save generated versions to `examples/after/`
6. ✅ Optionally optimize images for web
7. ✅ Test landing page locally
8. ✅ Deploy!

**License Compliance:**
- Unsplash License allows commercial use and derivatives ✅
- Your AI-generated versions are transformative works ✅
- No attribution legally required (but you can add it) ✅
- Can use in marketing materials ✅

**Total Time:** ~30 minutes

**Cost:** £0

---

## 🆘 Quick Start for Busy People

**Fastest way to get examples:**

```bash
# 1. Download 4 Unsplash photos (5 min)
# https://unsplash.com/s/photos/professional-headshot

# 2. Start GradGen frontend (1 min)
cd webapp/frontend && npm run dev

# 3. Upload each photo, generate, download (15 min total)
# Visit http://localhost:3000/generate
# Upload → Generate → Download
# Do this 4 times

# 4. Save files (2 min)
# Originals → examples/before/
# Generated → examples/after/

# 5. Test (1 min)
# Refresh homepage to see before/after slider

# Done! ✅
```

---

## 📧 When in Doubt

If you're ever unsure about licensing:

1. **Check the license page**: Unsplash.com/license
2. **Read the download page**: It will say "Free to use" if compliant
3. **Keep records**: Save links to source photos
4. **Attribution is safe**: Even if not required, adding credit is always safe

**For GradGen.AI specifically:**
- You're using photos as **input** to demonstrate your **AI service**
- The output is a **transformative derivative work**
- This is clearly **fair use** for product demonstration
- Unsplash explicitly allows this use case

You're good to go! 🚀
