'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';

interface ImageComparisonProps {
  imageId: number;
  showOriginal?: boolean; // Optional: control whether to show original
}

export default function ImageComparison({ imageId, showOriginal = false }: ImageComparisonProps) {
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

        // Only fetch the generated result (much more efficient!)
        const outputResponse = await api.get(`/generation/results/${imageId}`, { responseType: 'blob' });

        // Create blob URL
        const outputUrl = URL.createObjectURL(new Blob([outputResponse.data]));

        setOutputImageUrl(outputUrl);
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

    // Cleanup blob URL and timeout on unmount
    return () => {
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
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
      {outputImageUrl && (
        <img
          src={outputImageUrl}
          alt="Generated graduation portrait"
          className="w-full h-auto"
        />
      )}
    </div>
  );
}
