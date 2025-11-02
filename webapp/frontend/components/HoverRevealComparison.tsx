'use client';

import { useState, useEffect } from 'react';

interface HoverRevealComparisonProps {
  beforeImage: string;
  afterImage: string;
  beforeLabel?: string;
  afterLabel?: string;
  title?: string;
}

export default function HoverRevealComparison({
  beforeImage,
  afterImage,
  beforeLabel = 'Before',
  afterLabel = 'After',
  title,
}: HoverRevealComparisonProps) {
  const [isRevealed, setIsRevealed] = useState(false);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Detect mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);

    // Preload images
    const img1 = new window.Image();
    const img2 = new window.Image();
    let loaded = 0;

    const onLoad = () => {
      loaded++;
      if (loaded === 2) {
        setImagesLoaded(true);
      }
    };

    img1.onload = onLoad;
    img2.onload = onLoad;
    img1.src = beforeImage;
    img2.src = afterImage;

    return () => window.removeEventListener('resize', checkMobile);
  }, [beforeImage, afterImage]);

  return (
    <div className="w-full max-w-4xl mx-auto">
      {title && (
        <h3 className="text-2xl md:text-3xl font-bold text-center mb-6 text-white">
          {title}
        </h3>
      )}

      {!imagesLoaded && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
        </div>
      )}

      <div
        className={`relative overflow-hidden rounded-2xl shadow-2xl cursor-pointer select-none ${!imagesLoaded ? 'hidden' : ''}`}
        onMouseEnter={() => !isMobile && setIsRevealed(true)}
        onMouseLeave={() => !isMobile && setIsRevealed(false)}
        onClick={() => isMobile && setIsRevealed(!isRevealed)}
      >
        {/* Container with fixed aspect ratio */}
        <div className="relative aspect-[3/4] bg-gray-200">
          {/* Before Image */}
          <div
            className={`absolute inset-0 transition-opacity duration-500 ${
              isRevealed ? 'opacity-0' : 'opacity-100'
            }`}
          >
            <img
              src={beforeImage}
              alt={beforeLabel}
              className="w-full h-full object-cover"
            />
            {/* Before Label */}
            <div className="absolute top-4 left-4 bg-gray-800/90 text-white px-4 py-2 rounded-full font-semibold text-sm shadow-lg">
              {beforeLabel}
            </div>
          </div>

          {/* After Image */}
          <div
            className={`absolute inset-0 transition-opacity duration-500 ${
              isRevealed ? 'opacity-100' : 'opacity-0'
            }`}
          >
            <img
              src={afterImage}
              alt={afterLabel}
              className="w-full h-full object-cover"
            />
            {/* After Label */}
            <div className="absolute top-4 right-4 bg-primary-600/90 text-white px-4 py-2 rounded-full font-semibold text-sm shadow-lg">
              {afterLabel}
            </div>
          </div>

          {/* Instruction hint */}
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 pointer-events-none">
            <div className="bg-black/60 text-white px-4 py-2 rounded-full text-xs md:text-sm font-medium">
              {isMobile ? 'Tap to reveal' : 'Hover to reveal'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
