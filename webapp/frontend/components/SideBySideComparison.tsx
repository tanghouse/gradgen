'use client';

import { useState, useEffect } from 'react';

interface SideBySideComparisonProps {
  beforeImage: string;
  afterImage: string;
  beforeLabel?: string;
  afterLabel?: string;
  title?: string;
}

export default function SideBySideComparison({
  beforeImage,
  afterImage,
  beforeLabel = 'Before',
  afterLabel = 'After',
  title,
}: SideBySideComparisonProps) {
  const [imagesLoaded, setImagesLoaded] = useState(false);

  useEffect(() => {
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
  }, [beforeImage, afterImage]);

  return (
    <div className="w-full max-w-6xl mx-auto">
      {!imagesLoaded && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
        </div>
      )}

      <div className={`relative grid md:grid-cols-2 gap-4 md:gap-8 ${!imagesLoaded ? 'hidden' : ''}`}>
        {/* Before Image */}
        <div className="group relative overflow-hidden rounded-2xl shadow-2xl bg-gray-200 transition-transform duration-300 hover:scale-105">
          <div className="relative aspect-[3/4]">
            <img
              src={beforeImage}
              alt={beforeLabel}
              className="w-full h-full object-cover"
            />
            {/* Label */}
            <div className="absolute top-4 left-4 bg-gray-800/90 text-white px-4 py-2 rounded-full font-semibold text-sm shadow-lg">
              {beforeLabel}
            </div>
            {/* Overlay on hover */}
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300"></div>
          </div>
        </div>

        {/* After Image */}
        <div className="group relative overflow-hidden rounded-2xl shadow-2xl bg-gray-200 transition-transform duration-300 hover:scale-105">
          <div className="relative aspect-[3/4]">
            <img
              src={afterImage}
              alt={afterLabel}
              className="w-full h-full object-cover"
            />
            {/* Label */}
            <div className="absolute top-4 right-4 bg-primary-600/90 text-white px-4 py-2 rounded-full font-semibold text-sm shadow-lg">
              {afterLabel}
            </div>
            {/* Overlay on hover */}
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300"></div>
          </div>
        </div>
      </div>

      {/* Arrow indicator (desktop only) - positioned absolutely within the grid gap */}
      <div className="hidden md:block absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none z-10">
        <div className="bg-white/95 rounded-full p-3 shadow-2xl">
          <svg
            className="w-6 h-6 text-primary-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 7l5 5m0 0l-5 5m5-5H6"
            />
          </svg>
        </div>
      </div>
    </div>
  );
}
