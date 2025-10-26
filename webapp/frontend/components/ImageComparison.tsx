'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';

interface ImageComparisonProps {
  imageId: number;
}

export default function ImageComparison({ imageId }: ImageComparisonProps) {
  const [inputImageUrl, setInputImageUrl] = useState<string>('');
  const [outputImageUrl, setOutputImageUrl] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const loadImages = async () => {
      try {
        setLoading(true);
        setError('');

        // Fetch both images with authentication
        const [inputResponse, outputResponse] = await Promise.all([
          api.get(`/generation/inputs/${imageId}`, { responseType: 'blob' }),
          api.get(`/generation/results/${imageId}`, { responseType: 'blob' }),
        ]);

        // Create blob URLs
        const inputUrl = URL.createObjectURL(new Blob([inputResponse.data]));
        const outputUrl = URL.createObjectURL(new Blob([outputResponse.data]));

        setInputImageUrl(inputUrl);
        setOutputImageUrl(outputUrl);
      } catch (err: any) {
        console.error('Failed to load images:', err);
        setError('Failed to load images');
      } finally {
        setLoading(false);
      }
    };

    loadImages();

    // Cleanup blob URLs on unmount
    return () => {
      if (inputImageUrl) URL.revokeObjectURL(inputImageUrl);
      if (outputImageUrl) URL.revokeObjectURL(outputImageUrl);
    };
  }, [imageId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 text-sm p-4 bg-red-50 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {/* Original Image */}
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-2">Original</p>
        <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
          {inputImageUrl && (
            <img
              src={inputImageUrl}
              alt="Original uploaded image"
              className="w-full h-auto"
            />
          )}
        </div>
      </div>

      {/* Generated Result */}
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-2">Generated Result</p>
        <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
          {outputImageUrl && (
            <img
              src={outputImageUrl}
              alt="Generated graduation portrait"
              className="w-full h-auto"
            />
          )}
        </div>
      </div>
    </div>
  );
}
