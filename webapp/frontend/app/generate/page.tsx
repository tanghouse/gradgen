'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { generationAPI, paymentAPI, referralAPI, University, TierStatus, PricingInfo } from '@/lib/api';
import Navbar from '@/components/Navbar';

export default function GeneratePage() {
  const { user, loading: authLoading, refreshUser } = useAuth();
  const router = useRouter();

  // Form state
  const [universities, setUniversities] = useState<University[]>([]);
  const [selectedUniversity, setSelectedUniversity] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');

  // Tier state
  const [tierStatus, setTierStatus] = useState<TierStatus | null>(null);
  const [pricingInfo, setPricingInfo] = useState<PricingInfo | null>(null);

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [showPricingModal, setShowPricingModal] = useState(false);

  // Pricing modal state
  const [promoCode, setPromoCode] = useState('');
  const [promoValidating, setPromoValidating] = useState(false);
  const [promoMessage, setPromoMessage] = useState('');
  const [promoValid, setPromoValid] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  // Load universities and tier status
  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      const [univData, tierData, priceData] = await Promise.all([
        generationAPI.listUniversities(),
        generationAPI.getTierStatus(),
        paymentAPI.getPricingInfo(),
      ]);

      setUniversities(univData);
      setTierStatus(tierData);
      setPricingInfo(priceData);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };

  const selectedUniversityData = universities.find(u => u.name === selectedUniversity);
  const availableLevels = selectedUniversityData?.degree_levels || [];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);

      // Create preview
      const url = URL.createObjectURL(selectedFile);
      setPreviewUrl(url);
    }
  };

  // Cleanup preview URL
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleValidatePromo = async () => {
    if (!promoCode.trim()) {
      setPromoMessage('');
      setPromoValid(false);
      return;
    }

    setPromoValidating(true);
    try {
      const result = await paymentAPI.validatePromoCode(promoCode);
      setPromoValid(result.valid);
      setPromoMessage(result.message);
    } catch (err) {
      setPromoValid(false);
      setPromoMessage('Failed to validate promo code');
    } finally {
      setPromoValidating(false);
    }
  };

  const handlePurchasePremium = async () => {
    setLoading(true);
    try {
      const checkout = await paymentAPI.createPremiumCheckout(promoCode || undefined);

      // Redirect to Stripe Checkout
      window.location.href = checkout.session_url;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create checkout session');
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (!file) {
      setError('Please select an image');
      return;
    }

    if (!selectedUniversity || !selectedLevel) {
      setError('Please select university and degree level');
      return;
    }

    // Check if user can generate
    if (!tierStatus?.can_generate) {
      setShowPricingModal(true);
      return;
    }

    setLoading(true);

    try {
      await generationAPI.generateTier(file, selectedUniversity, selectedLevel);

      setSuccess(true);
      await refreshUser(); // Refresh to update tier status

      // Redirect to dashboard after a short delay
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Generation failed. Please try again.');
    } finally {
      setLoading(false);
    }
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

  if (!user || !tierStatus) {
    return null;
  }

  const currentTier = tierStatus.tier;
  const canGenerate = tierStatus.can_generate;

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      <main className="flex-grow container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-4xl font-bold mb-2">Generate Graduation Portrait</h1>
          <p className="text-gray-600 mb-8">
            Upload your portrait and select your university to get started
          </p>

          {/* Tier Status Display */}
          <div className="bg-white rounded-lg shadow-sm p-4 mb-6 border-l-4 border-primary-600">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-600">Current Tier:</p>
                <p className="text-2xl font-bold text-primary-600 capitalize">{currentTier}</p>
                {currentTier === 'free' && !user.has_used_free_tier && (
                  <p className="text-sm text-gray-600 mt-1">
                    5 watermarked photos • No cost
                  </p>
                )}
                {currentTier === 'premium' && (
                  <p className="text-sm text-gray-600 mt-1">
                    10 unwatermarked photos total
                  </p>
                )}
              </div>
              {!canGenerate && (
                <button
                  onClick={() => setShowPricingModal(true)}
                  className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 font-semibold"
                >
                  Upgrade to Premium
                </button>
              )}
            </div>
          </div>

          {/* Error/Success Messages */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">
              Job created successfully! Redirecting to dashboard...
            </div>
          )}

          {/* Generation Form */}
          <div className="bg-white rounded-lg shadow-lg p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Portrait
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    {previewUrl ? (
                      <div>
                        <img
                          src={previewUrl}
                          alt="Preview"
                          className="mx-auto max-h-64 rounded-lg mb-4"
                        />
                        <p className="text-sm text-gray-600">{file?.name}</p>
                        <p className="text-xs text-gray-500 mt-2">Click to change</p>
                      </div>
                    ) : (
                      <>
                        <div className="text-gray-400 mb-2">
                          <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        </div>
                        <p className="text-sm text-gray-600">Click to upload or drag and drop</p>
                        <p className="text-xs text-gray-500 mt-1">PNG, JPG, WEBP up to 10MB</p>
                      </>
                    )}
                  </label>
                </div>
              </div>

              {/* University Selection */}
              <div>
                <label htmlFor="university" className="block text-sm font-medium text-gray-700 mb-2">
                  University
                </label>
                <select
                  id="university"
                  value={selectedUniversity}
                  onChange={(e) => {
                    setSelectedUniversity(e.target.value);
                    setSelectedLevel('');
                  }}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select University</option>
                  {universities.map((uni) => (
                    <option key={uni.name} value={uni.name}>
                      {uni.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Degree Level Selection */}
              <div>
                <label htmlFor="level" className="block text-sm font-medium text-gray-700 mb-2">
                  Degree Level
                </label>
                <select
                  id="level"
                  value={selectedLevel}
                  onChange={(e) => setSelectedLevel(e.target.value)}
                  required
                  disabled={!selectedUniversity}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100"
                >
                  <option value="">Select Degree Level</option>
                  {availableLevels.map((level) => (
                    <option key={level} value={level}>
                      {level}
                    </option>
                  ))}
                </select>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !file || !selectedUniversity || !selectedLevel}
                className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Generating...' : canGenerate ? `Generate ${currentTier === 'free' ? '5 Watermarked' : '5 Premium'} Photos` : 'Upgrade Required'}
              </button>
            </form>
          </div>

          {/* Info Box */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">What You'll Get:</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              {currentTier === 'free' && !user.has_used_free_tier ? (
                <>
                  <li>• 5 graduation photos with different styles</li>
                  <li>• Watermarked with "GradGen.AI"</li>
                  <li>• Completely free - no credit card required</li>
                  <li>• Upgrade to premium for unwatermarked photos</li>
                </>
              ) : (
                <>
                  <li>• 5 additional premium style photos</li>
                  <li>• All 10 photos unwatermarked</li>
                  <li>• High-quality download</li>
                  <li>• Full commercial rights</li>
                </>
              )}
            </ul>
          </div>
        </div>
      </main>

      {/* Pricing Modal */}
      {showPricingModal && pricingInfo && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-2xl font-bold mb-4">Upgrade to Premium</h2>

            <div className="space-y-4 mb-6">
              <div className="border-2 border-primary-600 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="text-lg font-semibold">Premium Tier</p>
                    <p className="text-sm text-gray-600">5 more photos + unwatermark all 10</p>
                  </div>
                  <div className="text-right">
                    {pricingInfo.discount_available ? (
                      <>
                        <p className="text-sm text-gray-500 line-through">£{pricingInfo.base_price.toFixed(2)}</p>
                        <p className="text-2xl font-bold text-primary-600">£{pricingInfo.discounted_price?.toFixed(2)}</p>
                        <p className="text-xs text-green-600 font-semibold">
                          {pricingInfo.discount_source === 'referral' ? '3 Friends Discount!' : 'Discount Applied!'}
                        </p>
                      </>
                    ) : (
                      <p className="text-2xl font-bold text-primary-600">£{pricingInfo.base_price.toFixed(2)}</p>
                    )}
                  </div>
                </div>

                <ul className="text-sm text-gray-700 space-y-1">
                  <li>✓ 5 additional premium prompts</li>
                  <li>✓ Remove watermarks from all 10 photos</li>
                  <li>✓ High-resolution downloads</li>
                  <li>✓ Commercial usage rights</li>
                </ul>
              </div>

              {/* Referral Progress */}
              {!pricingInfo.referral_discount_eligible && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm font-semibold text-blue-900 mb-2">
                    Get £20 Off - Refer {pricingInfo.referrals_needed} Friends!
                  </p>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex-grow bg-blue-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${(pricingInfo.referrals_completed / pricingInfo.referrals_needed) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-xs font-semibold text-blue-900">
                      {pricingInfo.referrals_completed}/{pricingInfo.referrals_needed}
                    </span>
                  </div>
                  <p className="text-xs text-blue-700">
                    Refer {pricingInfo.referrals_needed - pricingInfo.referrals_completed} more friend{pricingInfo.referrals_needed - pricingInfo.referrals_completed !== 1 ? 's' : ''} to unlock £19.99 pricing!
                  </p>
                </div>
              )}

              {/* Promo Code */}
              {!pricingInfo.discount_available && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Have a promo code?
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={promoCode}
                      onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                      placeholder="PROMO CODE"
                      className="flex-grow px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                    <button
                      onClick={handleValidatePromo}
                      disabled={promoValidating || !promoCode.trim()}
                      className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
                    >
                      {promoValidating ? '...' : 'Apply'}
                    </button>
                  </div>
                  {promoMessage && (
                    <p className={`text-sm mt-2 ${promoValid ? 'text-green-600' : 'text-red-600'}`}>
                      {promoMessage}
                    </p>
                  )}
                </div>
              )}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowPricingModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handlePurchasePremium}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-semibold disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Proceed to Payment'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
