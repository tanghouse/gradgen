'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';

interface ImageComparisonProps {
  imageId: number;
  showOriginal?: boolean; // Optional: control whether to show original
}

export default function ImageComparison({ imageId, showOriginal = false }: ImageComparisonProps) {
  const [outputImageUrl, setOutputImageUrl] = useState<string>('');
  const [inputImageUrl, setInputImageUrl] = useState<string>('');
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

        // Fetch the generated result
        const outputResponse = await api.get(`/generation/results/${imageId}`, { responseType: 'blob' });
        const outputUrl = URL.createObjectURL(new Blob([outputResponse.data]));
        setOutputImageUrl(outputUrl);

        // Optionally fetch the original input image
        if (showOriginal) {
          try {
            const inputResponse = await api.get(`/generation/input/${imageId}`, { responseType: 'blob' });
            const inputUrl = URL.createObjectURL(new Blob([inputResponse.data]));
            setInputImageUrl(inputUrl);
          } catch (inputErr) {
            console.warn('Failed to load original image:', inputErr);
            // Don't fail the whole component if original can't load
          }
        }

        setRetryCount(0); // Reset retry count on success
      } catch (err: any) {
        console.error('Failed to load image:', err);

        // Check if it's a 404 (image not ready yet) and we haven't exceeded max retries
        if (err.response?.status === 404 && retryCount < MAX_RETRIES) {
          setError(`Image not ready yet. Retrying... (${retryCount + 1}/${MAX_RETRIES})`);
          // Retry after delay
          retryTimeout = setTimeout(() => {
            setRetryCount(prev => prev + 1);
          }, RETRY_DELAY);
        } else if (retryCount >= MAX_RETRIES) {
          setError('Image is still processing. Please refresh the page in a moment.');
        } else {
          setError('Failed to load image');
        }
      } finally {
        setLoading(false);
      }
    };

    loadImages();

    // Cleanup blob URLs and timeout on unmount
    return () => {
      if (outputImageUrl) URL.revokeObjectURL(outputImageUrl);
      if (inputImageUrl) URL.revokeObjectURL(inputImageUrl);
      if (retryTimeout) clearTimeout(retryTimeout);
    };
  }, [imageId, retryCount, showOriginal]);

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
    <div className="space-y-2">
      {/* Show original if requested */}
      {showOriginal && inputImageUrl && (
        <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
          <img
            src={inputImageUrl}
            alt="Original photo"
            className="w-full h-auto"
          />
          <div className="px-3 py-2 bg-gray-100 text-xs text-gray-600 text-center font-medium">
            Original
          </div>
        </div>
      )}

      {/* Generated result */}
      {outputImageUrl && (
        <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
          <img
            src={outputImageUrl}
            alt="Generated graduation portrait"
            className="w-full h-auto"
          />
          <div className="px-3 py-2 bg-primary-100 text-xs text-primary-700 text-center font-medium">
            Generated
          </div>
        </div>
      )}
    </div>
  );
}
