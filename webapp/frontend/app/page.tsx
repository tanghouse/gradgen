'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import SideBySideComparison from '@/components/SideBySideComparison';

// Example photos configuration
const EXAMPLES = [
  {
    id: 1,
    before: '/examples/before/example-1.jpg',
    after: '/examples/after/example-1.png',
    name: 'Professional Studio Style',
  },
  {
    id: 2,
    before: '/examples/before/example-2.jpg',
    after: '/examples/after/example-2.png',
    name: 'University Regalia',
  },
  {
    id: 3,
    before: '/examples/before/example-3.jpg',
    after: '/examples/after/example-3.png',
    name: 'Classic Graduation',
  },
  {
    id: 4,
    before: '/examples/before/example-4.jpg',
    after: '/examples/after/example-4.png',
    name: 'Editorial Style',
  },
];

export default function Home() {
  const [currentExample, setCurrentExample] = useState(0);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-grow">
        {/* Hero Section with Before/After */}
        <section className="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white py-12 md:py-20 px-4">
          <div className="container mx-auto max-w-6xl">
            <div className="text-center mb-8 md:mb-12">
              <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold mb-4 md:mb-6 leading-tight">
                Transform Your Portrait into a
                <br className="hidden md:block" />
                <span className="text-yellow-300"> Professional Graduation Photo</span>
              </h1>
              <p className="text-lg md:text-xl opacity-90 mb-6 md:mb-8 max-w-3xl mx-auto px-4">
                AI-Powered. Instant Results. Perfect for announcements, LinkedIn, and more.
              </p>
            </div>

            {/* Example Selector */}
            <div className="flex justify-center gap-2 mb-6 md:mb-8 flex-wrap px-4">
              {EXAMPLES.map((example, idx) => (
                <button
                  key={example.id}
                  onClick={() => setCurrentExample(idx)}
                  className={`px-4 py-2 md:px-6 md:py-2.5 rounded-lg text-sm md:text-base font-semibold transition-all shadow-md ${
                    currentExample === idx
                      ? 'bg-white text-primary-600 shadow-lg'
                      : 'bg-white/20 text-white hover:bg-white/30'
                  }`}
                >
                  Example {idx + 1}
                </button>
              ))}
            </div>

            {/* Side by Side Comparison */}
            {mounted && EXAMPLES[currentExample] && (
              <div className="mb-16 md:mb-20">
                <SideBySideComparison
                  beforeImage={EXAMPLES[currentExample].before}
                  afterImage={EXAMPLES[currentExample].after}
                  beforeLabel="Original"
                  afterLabel="GradGen.AI"
                  title={EXAMPLES[currentExample].name}
                />
              </div>
            )}

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/register"
                className="w-full sm:w-auto bg-yellow-400 text-primary-900 px-8 py-4 rounded-lg text-lg font-bold hover:bg-yellow-300 transition-all shadow-lg hover:shadow-xl text-center"
              >
                Try 5 Styles Free →
              </Link>
              <Link
                href="#how-it-works"
                className="w-full sm:w-auto bg-white/10 backdrop-blur text-white border-2 border-white/30 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white/20 transition-all text-center"
              >
                See How It Works
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="mt-8 md:mt-12 flex flex-wrap justify-center gap-4 md:gap-8 text-sm md:text-base opacity-90">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span>AI-Powered</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Instant Results</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Face Preserved</span>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section id="how-it-works" className="py-12 md:py-20 bg-white">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
              How It Works
            </h2>
            <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
              Get professional graduation photos in 3 simple steps
            </p>

            <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              <div className="text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">📸</span>
                </div>
                <h3 className="text-xl font-bold mb-2">1. Upload Photo</h3>
                <p className="text-gray-600">
                  Upload a clear portrait photo. Our AI works best with front-facing headshots.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🎓</span>
                </div>
                <h3 className="text-xl font-bold mb-2">2. Choose University</h3>
                <p className="text-gray-600">
                  Select your university and degree level for accurate academic regalia.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">✨</span>
                </div>
                <h3 className="text-xl font-bold mb-2">3. Get 10 Styles</h3>
                <p className="text-gray-600">
                  Receive 10 different professional graduation photo styles instantly.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section className="py-12 md:py-20 bg-gray-50">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-center text-gray-600 mb-12">
              Try 5 styles free, then unlock more with our full package
            </p>

            <div className="grid md:grid-cols-2 gap-6 md:gap-8 max-w-5xl mx-auto">
              {/* Free Tier */}
              <div className="bg-white rounded-2xl shadow-lg p-6 md:p-8 border-2 border-gray-200">
                <div className="text-center">
                  <h3 className="text-2xl font-bold mb-2">Free Trial</h3>
                  <div className="text-5xl font-bold text-gray-900 mb-6">£0</div>

                  <ul className="text-left space-y-3 mb-8">
                    <li className="flex items-start gap-2">
                      <svg className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>5 AI-generated graduation photos</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <svg className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>5 professional styles</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <svg className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Preview all results</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <svg className="w-6 h-6 text-yellow-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <span className="text-gray-600">Watermarked photos</span>
                    </li>
                  </ul>

                  <Link
                    href="/register"
                    className="block w-full bg-gray-200 text-gray-800 px-6 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                  >
                    Start Free Trial
                  </Link>
                </div>
              </div>

              {/* Paid Tier */}
              <div className="bg-gradient-to-br from-primary-600 to-primary-700 rounded-2xl shadow-2xl p-6 md:p-8 border-2 border-primary-800 relative">
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-yellow-400 text-primary-900 px-6 py-2 rounded-full font-bold text-sm shadow-lg">
                  ⭐ BEST VALUE
                </div>

                <div className="text-center text-white">
                  <h3 className="text-2xl font-bold mb-2">Full Package</h3>
                  <div className="mb-4">
                    <div className="text-2xl line-through opacity-75">£39.99</div>
                    <div className="text-5xl font-bold mb-2">£19.99</div>
                    <div className="text-sm bg-green-500 inline-block px-3 py-1 rounded-full">
                      With 3 referrals or promo code
                    </div>
                  </div>

                  <ul className="text-left space-y-3 mb-8">
                    <li className="flex items-start gap-2">
                      <svg className="w-6 h-6 text-yellow-300 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Everything in Free Tier</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <svg className="w-6 h-6 text-yellow-300 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span><strong>5 MORE</strong> random unique styles (10 total)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <svg className="w-6 h-6 text-yellow-300 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span><strong>ALL 10 photos unwatermarked</strong></span>
                    </li>
                    <li className="flex items-start gap-2">
                      <svg className="w-6 h-6 text-yellow-300 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>High-resolution downloads</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <svg className="w-6 h-6 text-yellow-300 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Download all as ZIP</span>
                    </li>
                  </ul>

                  <div className="bg-white/10 backdrop-blur rounded-lg p-3 mb-6 text-sm">
                    <p>🎁 Refer 3 friends to unlock £19.99 pricing!</p>
                  </div>

                  <Link
                    href="/register"
                    className="block w-full bg-yellow-400 text-primary-900 px-6 py-3 rounded-lg font-bold hover:bg-yellow-300 transition-colors shadow-lg"
                  >
                    Get Full Package
                  </Link>
                </div>
              </div>
            </div>

            <div className="text-center mt-8">
              <p className="text-gray-600">
                Have a promo code?{' '}
                <Link href="/register" className="text-primary-600 underline font-semibold">
                  Apply at checkout
                </Link>
              </p>
            </div>
          </div>
        </section>

        {/* Social Proof / Features */}
        <section className="py-12 md:py-20 bg-white">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
              Why Choose GradGen.AI?
            </h2>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
              <div className="text-center">
                <div className="text-4xl mb-4">🤖</div>
                <h3 className="font-bold mb-2">AI-Powered</h3>
                <p className="text-gray-600 text-sm">
                  Advanced AI preserves your face while adding perfect graduation attire
                </p>
              </div>

              <div className="text-center">
                <div className="text-4xl mb-4">⚡</div>
                <h3 className="font-bold mb-2">Instant Results</h3>
                <p className="text-gray-600 text-sm">
                  Get all 10 graduation photos in minutes, not days
                </p>
              </div>

              <div className="text-center">
                <div className="text-4xl mb-4">🎯</div>
                <h3 className="font-bold mb-2">Accurate Regalia</h3>
                <p className="text-gray-600 text-sm">
                  University-specific gowns, hoods, and caps that match your degree
                </p>
              </div>

              <div className="text-center">
                <div className="text-4xl mb-4">💎</div>
                <h3 className="font-bold mb-2">Multiple Styles</h3>
                <p className="text-gray-600 text-sm">
                  10 different professional styles to choose your favorite
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-12 md:py-20 bg-gradient-to-r from-primary-600 to-primary-800 text-white">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              Ready to Transform Your Portrait?
            </h2>
            <p className="text-lg md:text-xl opacity-90 mb-8 max-w-2xl mx-auto">
              Join thousands of graduates who trust GradGen.AI for their professional graduation photos
            </p>
            <Link
              href="/register"
              className="inline-block bg-yellow-400 text-primary-900 px-10 py-4 rounded-lg text-xl font-bold hover:bg-yellow-300 transition-all shadow-2xl hover:shadow-xl"
            >
              Get Started Free Today →
            </Link>
            <p className="mt-6 text-sm opacity-75">
              No credit card required • 5 free styles • Instant results
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 md:py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="font-bold text-lg mb-4">GradGen.AI</h3>
              <p className="text-gray-400 text-sm">
                AI-powered professional graduation portrait generation
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-4">Quick Links</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/register" className="text-gray-400 hover:text-white">Get Started</Link></li>
                <li><Link href="/login" className="text-gray-400 hover:text-white">Login</Link></li>
                <li><Link href="#how-it-works" className="text-gray-400 hover:text-white">How It Works</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-4">Legal</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/privacy" className="text-gray-400 hover:text-white">Privacy Policy</Link></li>
                <li><Link href="/terms" className="text-gray-400 hover:text-white">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-6 text-center text-gray-400 text-sm">
            <p>&copy; 2025 GradGen.AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
