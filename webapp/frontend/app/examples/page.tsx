'use client';

import Link from 'next/link';
import Navbar from '@/components/Navbar';

export default function ExamplesPage() {
  const examples = [
    {
      id: 1,
      university: 'University of Cambridge',
      level: 'Masters',
      beforeDesc: 'Casual portrait photo',
      afterDesc: 'Professional graduation photo with Cambridge MA regalia',
    },
    {
      id: 2,
      university: 'University of Oxford',
      level: 'Bachelors',
      beforeDesc: 'LinkedIn profile picture',
      afterDesc: 'Graduation portrait with Oxford BA gown and hood',
    },
    {
      id: 3,
      university: 'Imperial College London',
      level: 'PhD',
      beforeDesc: 'Outdoor headshot',
      afterDesc: 'Doctoral graduation photo with Imperial PhD regalia',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      <main className="flex-grow container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Example Transformations</h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              See how GradGen transforms ordinary portraits into professional graduation photos
              with accurate academic regalia
            </p>
          </div>

          {/* Examples Grid */}
          <div className="space-y-16">
            {examples.map((example) => (
              <div key={example.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-2xl font-bold text-gray-900">{example.university}</h2>
                  <p className="text-gray-600">{example.level}</p>
                </div>

                <div className="grid md:grid-cols-2 gap-0">
                  {/* Before */}
                  <div className="p-8 border-r border-gray-200">
                    <div className="text-center mb-4">
                      <span className="inline-block bg-gray-100 text-gray-700 px-4 py-2 rounded-full font-semibold">
                        Before
                      </span>
                    </div>
                    <div className="aspect-[3/4] bg-gray-200 rounded-lg flex items-center justify-center mb-4">
                      <div className="text-center text-gray-400">
                        <svg className="mx-auto h-16 w-16 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        <p className="text-sm">Original Portrait</p>
                      </div>
                    </div>
                    <p className="text-center text-gray-600 text-sm">{example.beforeDesc}</p>
                  </div>

                  {/* After */}
                  <div className="p-8">
                    <div className="text-center mb-4">
                      <span className="inline-block bg-primary-100 text-primary-700 px-4 py-2 rounded-full font-semibold">
                        After
                      </span>
                    </div>
                    <div className="aspect-[3/4] bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg flex items-center justify-center mb-4">
                      <div className="text-center text-primary-400">
                        <svg className="mx-auto h-16 w-16 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
                        </svg>
                        <p className="text-sm">Generated Result</p>
                      </div>
                    </div>
                    <p className="text-center text-gray-600 text-sm">{example.afterDesc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Features Highlight */}
          <div className="mt-16 bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-6 text-center">What Makes GradGen Special?</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-4xl mb-3">🎯</div>
                <h3 className="font-semibold mb-2">Identity Preservation</h3>
                <p className="text-sm text-gray-600">
                  Your face and features remain perfectly intact - only the attire changes
                </p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-3">🎓</div>
                <h3 className="font-semibold mb-2">Accurate Regalia</h3>
                <p className="text-sm text-gray-600">
                  Precise gowns, hoods, and caps specific to your university and degree level
                </p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-3">✨</div>
                <h3 className="font-semibold mb-2">Photo-Realistic</h3>
                <p className="text-sm text-gray-600">
                  Natural lighting, realistic fabric textures, and professional quality
                </p>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="mt-12 text-center">
            <Link
              href="/generate"
              className="inline-block bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700"
            >
              Try It Now
            </Link>
            <p className="mt-4 text-gray-600">
              New users get 5 free credits!
            </p>
          </div>

          {/* Note */}
          <div className="mt-12 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <p className="text-sm text-yellow-800">
              <strong>Note:</strong> The examples shown above are placeholders. Actual generated images
              will be displayed here once real generations are processed. Each transformation preserves
              facial identity while accurately applying university-specific graduation attire.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 GradGen. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
