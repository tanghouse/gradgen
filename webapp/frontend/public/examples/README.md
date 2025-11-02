# Example Photos for Landing Page

This directory contains before/after example photos for the GradGen.AI landing page.

## Directory Structure

```
examples/
├── before/
│   ├── example-1.jpg  # Professional portrait 1
│   ├── example-2.jpg  # Professional portrait 2
│   ├── example-3.jpg  # Professional portrait 3
│   └── example-4.jpg  # Professional portrait 4
└── after/
    ├── example-1.jpg  # Graduation version 1
    ├── example-2.jpg  # Graduation version 2
    ├── example-3.jpg  # Graduation version 3
    └── example-4.jpg  # Graduation version 4
```

## How to Add Example Photos

### Step 1: Download "Before" Photos from Unsplash

Visit [Unsplash Professional Headshots](https://unsplash.com/s/photos/professional-headshot) and download 4 high-quality portraits:

**Criteria:**
- Clear face visibility (front-facing preferred)
- Professional appearance
- Good lighting
- Diverse representation (different genders, ethnicities, ages)
- Half-body or headshot composition
- High resolution (minimum 1200px width)

**Recommended Search Terms:**
- "professional headshot"
- "professional portrait"
- "business portrait"
- "corporate headshot"

**Example Photo IDs (as of 2025):**
You can search for these on Unsplash or choose your own:
- Young professional woman
- Young professional man
- Mature professional
- Professional with glasses

### Step 2: Save "Before" Photos

1. Download each photo from Unsplash
2. Rename them to:
   - `example-1.jpg`
   - `example-2.jpg`
   - `example-3.jpg`
   - `example-4.jpg`
3. Save to `webapp/frontend/public/examples/before/`

### Step 3: Generate "After" Graduation Photos

You have two options:

#### Option A: Use Existing GradGen System (Recommended)
1. Start the backend server
2. Use the generation API with each before photo
3. Save generated results to `examples/after/` with matching names

#### Option B: Manual Upload
1. If you have pre-generated graduation photos, save them directly to `examples/after/`
2. Ensure filenames match: `example-1.jpg` → `example-1.jpg`

### Step 4: Optimize Images

For best performance, optimize images before deployment:

```bash
# Using ImageMagick (if installed)
cd webapp/frontend/public/examples/before
for i in *.jpg; do convert "$i" -resize 1600x -quality 85 "$i"; done

cd ../after
for i in *.jpg; do convert "$i" -resize 1600x -quality 85 "$i"; done
```

## Image Requirements

- **Format:** JPG or PNG
- **Width:** 1200-2000px recommended
- **Aspect Ratio:** 4:3 or 3:4 (portrait) works best with BeforeAfterSlider
- **File Size:** < 500KB per image (optimize for web)
- **Naming:** Must match exactly: `example-N.jpg` in both folders

## Attribution

If using Unsplash photos:
- License: Unsplash License (free to use, no attribution required)
- But good practice: Credit photographers in footer or about page

## Testing

After adding photos, test the landing page:

```bash
cd webapp/frontend
npm run dev
# Visit http://localhost:3000
```

The before/after slider should display your example photos with smooth transitions.

## Troubleshooting

**Images not showing:**
- Check file names match exactly (`example-1.jpg` not `Example-1.jpg`)
- Verify files are in correct directories
- Check browser console for 404 errors
- Ensure Next.js dev server restarted after adding images

**Slider not working:**
- Clear browser cache
- Check BeforeAfterSlider component is imported correctly
- Verify image paths in `page.tsx` EXAMPLES array

**Images too large:**
- Optimize with ImageMagick or online tools
- Target < 500KB per image for good performance
- Consider WebP format for even smaller sizes
