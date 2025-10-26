'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { loadStripe, Stripe } from '@stripe/stripe-js';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { useAuth } from '@/lib/auth-context';
import { paymentAPI } from '@/lib/api';
import Navbar from '@/components/Navbar';

// Stripe promise
let stripePromise: Promise<Stripe | null>;

const getStripe = async () => {
  if (!stripePromise) {
    const config = await paymentAPI.getConfig();
    stripePromise = loadStripe(config.publishable_key);
  }
  return stripePromise;
};

function CheckoutForm({ credits, onSuccess }: { credits: number; onSuccess: () => void }) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const { error: submitError } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/dashboard`,
        },
      });

      if (submitError) {
        setError(submitError.message || 'Payment failed');
      } else {
        onSuccess();
      }
    } catch (err: any) {
      setError(err.message || 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <PaymentElement />

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={!stripe || loading}
        className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'Processing...' : `Pay $${(credits / 10).toFixed(2)}`}
      </button>
    </form>
  );
}

export default function CreditsPage() {
  const { user, loading: authLoading, refreshUser } = useAuth();
  const router = useRouter();
  const [selectedPackage, setSelectedPackage] = useState<number | null>(null);
  const [clientSecret, setClientSecret] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  const packages = [
    { credits: 10, price: 1, popular: false },
    { credits: 50, price: 5, popular: true },
    { credits: 100, price: 10, popular: false },
    { credits: 500, price: 50, popular: false },
  ];

  const handleSelectPackage = async (credits: number) => {
    setSelectedPackage(credits);
    setError('');
    setLoading(true);

    try {
      const response = await paymentAPI.createPaymentIntent(credits);
      setClientSecret(response.client_secret);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create payment. Please try again.');
      setSelectedPackage(null);
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentSuccess = async () => {
    await refreshUser();
    setTimeout(() => {
      router.push('/dashboard');
    }, 1000);
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      <main className="flex-grow container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-2 text-center">Buy Credits</h1>
          <p className="text-gray-600 mb-8 text-center">
            Purchase credits to generate graduation portraits
          </p>

          {/* Current Credits */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8 text-center">
            <div className="text-sm text-gray-600 mb-1">Current Balance</div>
            <div className="text-4xl font-bold text-primary-600">{user.credits} Credits</div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {!selectedPackage ? (
            /* Package Selection */
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {packages.map((pkg) => (
                <div
                  key={pkg.credits}
                  className={`bg-white rounded-lg shadow-lg p-6 text-center relative ${
                    pkg.popular ? 'ring-2 ring-primary-500' : ''
                  }`}
                >
                  {pkg.popular && (
                    <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                      <span className="bg-primary-500 text-white px-3 py-1 rounded-full text-xs font-semibold">
                        Popular
                      </span>
                    </div>
                  )}

                  <div className="text-4xl font-bold text-gray-900 mb-2">
                    {pkg.credits}
                  </div>
                  <div className="text-sm text-gray-600 mb-4">Credits</div>

                  <div className="text-3xl font-bold text-primary-600 mb-6">
                    ${pkg.price}
                  </div>

                  <div className="text-xs text-gray-500 mb-6">
                    ${(pkg.price / pkg.credits).toFixed(2)} per credit
                  </div>

                  <button
                    onClick={() => handleSelectPackage(pkg.credits)}
                    disabled={loading}
                    className="w-full bg-primary-600 text-white py-2 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Loading...' : 'Select'}
                  </button>
                </div>
              ))}
            </div>
          ) : (
            /* Payment Form */
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-md mx-auto">
              <button
                onClick={() => {
                  setSelectedPackage(null);
                  setClientSecret('');
                }}
                className="text-gray-600 hover:text-gray-900 mb-6 flex items-center"
              >
                ← Back to packages
              </button>

              <h2 className="text-2xl font-bold mb-6">
                Purchase {selectedPackage} Credits
              </h2>

              {clientSecret && (
                <Elements
                  stripe={getStripe()}
                  options={{
                    clientSecret,
                    appearance: {
                      theme: 'stripe',
                    },
                  }}
                >
                  <CheckoutForm credits={selectedPackage} onSuccess={handlePaymentSuccess} />
                </Elements>
              )}

              {loading && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Setting up payment...</p>
                </div>
              )}
            </div>
          )}

          {/* Info */}
          <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="font-semibold text-blue-900 mb-3">About Credits</h3>
            <ul className="text-sm text-blue-800 space-y-2">
              <li>• Each portrait generation costs 1 credit</li>
              <li>• Credits never expire</li>
              <li>• Secure payment powered by Stripe</li>
              <li>• Instant credit delivery after payment</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
