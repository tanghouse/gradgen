'use client';

import { useState, useEffect } from 'react';

interface Example {
  id: number;
  before: string;
  after: string;
  name: string;
}

interface ExampleGalleryProps {
  examples: Example[];
}

export default function ExampleGallery({ examples }: ExampleGalleryProps) {
  const [selectedExample, setSelectedExample] = useState<number | null>(null);
  const [imagesLoaded, setImagesLoaded] = useState<Set<number>>(new Set());

  useEffect(() => {
    // Preload all images
    examples.forEach((example) => {
      const img1 = new window.Image();
      const img2 = new window.Image();
      let loaded = 0;

      const onLoad = () => {
        loaded++;
        if (loaded === 2) {
          setImagesLoaded((prev) => new Set([...prev, example.id]));
        }
      };

      img1.onload = onLoad;
      img2.onload = onLoad;
      img1.src = example.before;
      img2.src = example.after;
    });
  }, [examples]);

  return (
    <div className="w-full max-w-7xl mx-auto">
      {/* Gallery Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {examples.map((example) => (
          <div
            key={example.id}
            className="group cursor-pointer"
            onClick={() => setSelectedExample(example.id)}
          >
            {/* Card */}
            <div className="bg-white rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
              {/* Images Container */}
              <div className="relative aspect-[3/4] overflow-hidden">
                {!imagesLoaded.has(example.id) && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-200">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                  </div>
                )}

                {/* Before Image (default) */}
                <img
                  src={example.before}
                  alt={`Before - ${example.name}`}
                  className="absolute inset-0 w-full h-full object-cover transition-opacity duration-300 group-hover:opacity-0"
                />

                {/* After Image (on hover) */}
                <img
                  src={example.after}
                  alt={`After - ${example.name}`}
                  className="absolute inset-0 w-full h-full object-cover opacity-0 transition-opacity duration-300 group-hover:opacity-100"
                />

                {/* Labels */}
                <div className="absolute top-2 left-2 bg-gray-800/90 text-white px-3 py-1 rounded-full text-xs font-semibold opacity-100 group-hover:opacity-0 transition-opacity">
                  Before
                </div>
                <div className="absolute top-2 right-2 bg-primary-600/90 text-white px-3 py-1 rounded-full text-xs font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                  After
                </div>

                {/* Hover hint */}
                <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/70 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <p className="text-white text-xs text-center">
                    Click to enlarge
                  </p>
                </div>
              </div>

              {/* Card Footer */}
              <div className="p-4 bg-gradient-to-br from-gray-50 to-white">
                <h4 className="font-semibold text-gray-800 text-sm md:text-base text-center">
                  {example.name}
                </h4>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Lightbox Modal */}
      {selectedExample !== null && (
        <div
          className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedExample(null)}
        >
          <div
            className="relative max-w-6xl w-full"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button
              onClick={() => setSelectedExample(null)}
              className="absolute -top-12 right-0 text-white hover:text-gray-300 transition-colors"
            >
              <svg
                className="w-8 h-8"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>

            {/* Side by Side Comparison */}
            {examples
              .filter((ex) => ex.id === selectedExample)
              .map((example) => (
                <div key={example.id} className="grid md:grid-cols-2 gap-4">
                  {/* Before */}
                  <div className="relative rounded-xl overflow-hidden bg-gray-800">
                    <img
                      src={example.before}
                      alt="Before"
                      className="w-full h-full object-contain"
                    />
                    <div className="absolute top-4 left-4 bg-gray-800/90 text-white px-4 py-2 rounded-full font-semibold text-sm">
                      Before
                    </div>
                  </div>

                  {/* After */}
                  <div className="relative rounded-xl overflow-hidden bg-gray-800">
                    <img
                      src={example.after}
                      alt="After"
                      className="w-full h-full object-contain"
                    />
                    <div className="absolute top-4 right-4 bg-primary-600/90 text-white px-4 py-2 rounded-full font-semibold text-sm">
                      After
                    </div>
                  </div>
                </div>
              ))}

            {/* Example Name */}
            <div className="text-center mt-4">
              <p className="text-white text-lg font-semibold">
                {examples.find((ex) => ex.id === selectedExample)?.name}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
