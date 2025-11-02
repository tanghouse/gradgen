'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';

function SuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [countdown, setCountdown] = useState(5);

  useEffect(() => {
    // Redirect to generate page after countdown
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          router.push('/generate');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [router]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      <main className="flex-grow flex items-center justify-center px-4 py-12">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          {/* Success Icon */}
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg
              className="w-12 h-12 text-green-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>

          {/* Success Message */}
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Payment Successful!
          </h1>

          <p className="text-gray-600 mb-6">
            Thank you for upgrading to premium! You can now generate 5 more professional photos
            and download all 10 without watermarks.
          </p>

          {/* What's Next */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left">
            <h3 className="font-semibold text-blue-900 mb-2">What's Next:</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>✓ Premium tier activated</li>
              <li>✓ Generate 5 additional photos</li>
              <li>✓ Download all 10 without watermarks</li>
              <li>✓ High-resolution files ready</li>
            </ul>
          </div>

          {/* Transaction ID */}
          {sessionId && (
            <p className="text-xs text-gray-500 mb-6">
              Transaction ID: {sessionId.slice(0, 20)}...
            </p>
          )}

          {/* Action Buttons */}
          <div className="space-y-3">
            <Link
              href="/generate"
              className="block w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
            >
              Generate Premium Photos
            </Link>
            <Link
              href="/dashboard"
              className="block w-full bg-gray-100 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
            >
              View My Photos
            </Link>
          </div>

          {/* Auto Redirect */}
          <p className="text-sm text-gray-500 mt-6">
            Redirecting to generate page in {countdown} seconds...
          </p>
        </div>
      </main>
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex flex-col bg-gray-50">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </main>
      </div>
    }>
      <SuccessContent />
    </Suspense>
  );
}
