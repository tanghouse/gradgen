# Before/After Comparison Modes

The landing page now supports **4 different comparison modes** to showcase graduation photos. You can switch between them using the buttons at the top of the hero section.

## 1. Side by Side (Default) ✅ **Recommended**

**File:** `webapp/frontend/components/SideBySideComparison.tsx`

**Best for:** Photos with different compositions or alignment issues

**Features:**
- Before and after images displayed next to each other
- Mobile: Stacked vertically
- Desktop: Two columns with arrow indicator
- Hover effect: Slight scale-up on each image
- No alignment issues - each photo has its own space

**Why it works:**
- Eliminates alignment problems completely
- Clear visual separation
- Easy to compare side by side
- Works on all screen sizes

---

## 2. Hover Reveal

**File:** `webapp/frontend/components/HoverRevealComparison.tsx`

**Best for:** Creating interactive engagement, modern UI feel

**Features:**
- Shows "Before" image by default
- Desktop: Hover to fade to "After" image
- Mobile: Tap to toggle between Before/After
- Smooth fade transition (500ms)
- "Hover to reveal" / "Tap to reveal" hint at bottom

**Why it works:**
- Smooth fade transition hides alignment issues
- Interactive and engaging
- Clean, modern interaction pattern
- Single image view reduces cognitive load

---

## 3. Gallery

**File:** `webapp/frontend/components/ExampleGallery.tsx`

**Best for:** Showcasing all 4 examples at once, professional portfolio feel

**Features:**
- Grid layout: 1 column (mobile), 2 columns (tablet), 4 columns (desktop)
- Each card shows "Before" by default, "After" on hover
- Click any card to open full-screen lightbox
- Lightbox shows side-by-side comparison
- Smooth hover transitions and animations

**Why it works:**
- Shows variety of styles at a glance
- No need to click through examples one by one
- Professional portfolio presentation
- Lightbox eliminates alignment issues

---

## 4. Slider (Original)

**File:** `webapp/frontend/components/BeforeAfterSlider.tsx`

**Best for:** Photos with identical compositions and perfect alignment

**Features:**
- Draggable vertical slider
- Reveals "After" image as you drag right
- Touch and mouse support
- "Drag to compare" hint at bottom

**Why it can be problematic:**
- Requires identical face positions and compositions
- Misaligned photos look jarring
- Works great IF photos are perfectly aligned
- Not recommended for AI-generated photos with different poses

---

## Current Implementation

The landing page (`webapp/frontend/app/page.tsx`) now includes:

1. **Mode selector buttons** at the top
   - Side by Side
   - Hover Reveal
   - Gallery
   - Slider (Original)

2. **Dynamic rendering** based on selected mode

3. **Example selector** (for non-gallery modes)
   - Professional Studio Style
   - University Regalia
   - Classic Graduation
   - Editorial Style

---

## Which Mode Should You Use?

### For Production Landing Page:

**Recommendation: Side by Side** (currently set as default)

**Why:**
- ✅ Works with misaligned photos
- ✅ Clear visual comparison
- ✅ No user confusion
- ✅ Works on all devices
- ✅ Professional appearance
- ✅ Fast to understand

**Alternative: Gallery**
- Great for showing variety
- Portfolio-style presentation
- Good for desktop users
- More visual impact

### For Testing/Development:

Try all modes and see which one:
- Gets the most engagement
- Looks best with your actual photos
- Converts best (A/B testing)
- Feels most natural on mobile

---

## Customization

### Change Default Mode

Edit `webapp/frontend/app/page.tsx` line 42:

```typescript
// Current:
const [comparisonMode, setComparisonMode] = useState<'slider' | 'sideBySide' | 'hover' | 'gallery'>('sideBySide');

// To use gallery by default:
const [comparisonMode, setComparisonMode] = useState<'slider' | 'sideBySide' | 'hover' | 'gallery'>('gallery');
```

### Remove Mode Selector

If you want to lock to one mode and hide the selector buttons:

1. Choose your preferred mode (e.g., `'sideBySide'`)
2. Remove the mode selector buttons (lines 68-109 in page.tsx)
3. Remove the `comparisonMode` state variable

### Adjust Styling

Each component uses Tailwind CSS classes. Common adjustments:

**Change aspect ratio:**
```typescript
// Current: aspect-[3/4] (portrait)
// Options: aspect-[4/3] (landscape), aspect-square, aspect-[16/9]
```

**Change colors:**
```typescript
// Before label: bg-gray-800/90
// After label: bg-primary-600/90
```

**Change animations:**
```typescript
// Hover scale: hover:scale-105
// Transition speed: duration-300
```

---

## Technical Details

### Image Preloading

All components preload images to prevent flickering:

```typescript
useEffect(() => {
  const img1 = new window.Image();
  const img2 = new window.Image();
  img1.onload = onLoad;
  img2.onload = onLoad;
  img1.src = beforeImage;
  img2.src = afterImage;
}, [beforeImage, afterImage]);
```

### Responsive Design

- Mobile-first approach
- Breakpoints:
  - `sm:` 640px+
  - `md:` 768px+
  - `lg:` 1024px+

### Performance

- Images load on demand
- Loading spinners during image load
- No layout shift (fixed aspect ratios)
- Optimized animations (GPU-accelerated)

---

## Next Steps

1. **Test on real devices**
   - iPhone (Safari)
   - Android (Chrome)
   - Desktop (Chrome, Safari, Firefox)

2. **Measure engagement**
   - Which mode gets more clicks?
   - Which leads to more registrations?
   - Time spent on page?

3. **Optimize images**
   - Compress to < 500KB per image
   - Consider WebP format
   - Lazy loading for non-visible images

4. **A/B testing**
   - Test different default modes
   - Test with/without mode selector
   - Track conversion rates

---

## Troubleshooting

**Images not loading:**
- Check console for 404 errors
- Verify file paths in EXAMPLES array
- Ensure images exist in `public/examples/`

**Layout issues:**
- Check aspect ratios match your images
- Inspect with browser DevTools
- Test on different screen sizes

**Performance issues:**
- Compress large images
- Check Network tab for load times
- Consider lazy loading

**Mode selector not working:**
- Check browser console for errors
- Verify TypeScript types
- Test with React DevTools
