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
  const [retryCount, setRetryCount] = useState(0);

  const MAX_RETRIES = 5;
  const RETRY_DELAY = 2000; // 2 seconds

  useEffect(() => {
    let retryTimeout: NodeJS.Timeout;

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
        setRetryCount(0); // Reset retry count on success
      } catch (err: any) {
        console.error('Failed to load images:', err);

        // Check if it's a 404 (images not ready yet) and we haven't exceeded max retries
        if (err.response?.status === 404 && retryCount < MAX_RETRIES) {
          setError(`Images not ready yet. Retrying... (${retryCount + 1}/${MAX_RETRIES})`);
          // Retry after delay
          retryTimeout = setTimeout(() => {
            setRetryCount(prev => prev + 1);
          }, RETRY_DELAY);
        } else if (retryCount >= MAX_RETRIES) {
          setError('Images are still processing. Please refresh the page in a moment.');
        } else {
          setError('Failed to load images');
        }
      } finally {
        setLoading(false);
      }
    };

    loadImages();

    // Cleanup blob URLs and timeout on unmount
    return () => {
      if (inputImageUrl) URL.revokeObjectURL(inputImageUrl);
      if (outputImageUrl) URL.revokeObjectURL(outputImageUrl);
      if (retryTimeout) clearTimeout(retryTimeout);
    };
  }, [imageId, retryCount]);

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
