'use client';

import Link from 'next/link'
import Navbar from '@/components/Navbar'

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      {/* Hero Section */}
      <main className="flex-grow">
        <section className="container mx-auto px-4 py-20 text-center">
          <h1 className="text-5xl font-bold mb-6">
            Transform Your Portrait into a
            <span className="text-primary-600"> Professional Graduation Photo</span>
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            Upload your portrait and get an AI-generated graduation photo with accurate
            academic regalia from your university. Perfect for announcements, LinkedIn, and more.
          </p>
          <div className="space-x-4">
            <Link
              href="/generate"
              className="bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700 inline-block"
            >
              Generate Your Photo
            </Link>
            <Link
              href="/examples"
              className="bg-gray-200 text-gray-800 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-300 inline-block"
            >
              View Examples
            </Link>
          </div>
        </section>

        {/* Features */}
        <section className="bg-gray-50 py-20">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-4xl mb-4">📸</div>
                <h3 className="text-xl font-semibold mb-2">1. Upload Your Portrait</h3>
                <p className="text-gray-600">
                  Upload a clear photo of yourself. No special requirements needed.
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-4xl mb-4">🎓</div>
                <h3 className="text-xl font-semibold mb-2">2. Select Your University</h3>
                <p className="text-gray-600">
                  Choose your university and degree level to get the correct regalia.
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-4xl mb-4">✨</div>
                <h3 className="text-xl font-semibold mb-2">3. Get Your Photo</h3>
                <p className="text-gray-600">
                  Download your professional graduation portrait in seconds.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">Simple Pricing</h2>
            <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-lg">
              <div className="text-center">
                <div className="text-5xl font-bold mb-2">$0.10</div>
                <div className="text-gray-600 mb-6">per portrait</div>
                <ul className="text-left mb-8 space-y-3">
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    High-quality AI generation
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Accurate university regalia
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Face identity preserved
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Instant download
                  </li>
                </ul>
                <div className="bg-primary-50 p-4 rounded-lg mb-6">
                  <div className="font-semibold text-primary-700">New User Bonus</div>
                  <div className="text-sm text-primary-600">Get 5 free credits on signup!</div>
                </div>
                <Link
                  href="/register"
                  className="block bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700"
                >
                  Get Started Free
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 GradGen. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
