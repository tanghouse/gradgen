'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { generationAPI, University } from '@/lib/api';
import Navbar from '@/components/Navbar';

export default function GeneratePage() {
  const { user, loading: authLoading, refreshUser } = useAuth();
  const router = useRouter();
  const [universities, setUniversities] = useState<University[]>([]);
  const [selectedUniversity, setSelectedUniversity] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [mode, setMode] = useState<'single' | 'batch'>('single');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  // Load universities
  useEffect(() => {
    const loadUniversities = async () => {
      try {
        const data = await generationAPI.listUniversities();
        setUniversities(data);
      } catch (err) {
        console.error('Failed to load universities:', err);
      }
    };
    loadUniversities();
  }, []);

  const selectedUniversityData = universities.find(u => u.name === selectedUniversity);
  const availableLevels = selectedUniversityData?.degree_levels || [];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileList = Array.from(e.target.files);
      setFiles(fileList);
      if (fileList.length > 1) {
        setMode('batch');
      }

      // Create preview URLs for images
      const urls = fileList.map(file => URL.createObjectURL(file));
      setPreviewUrls(urls);
    }
  };

  // Cleanup preview URLs when component unmounts or files change
  useEffect(() => {
    return () => {
      previewUrls.forEach(url => URL.revokeObjectURL(url));
    };
  }, [previewUrls]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (files.length === 0) {
      setError('Please select at least one image');
      return;
    }

    if (!selectedUniversity || !selectedLevel) {
      setError('Please select university and degree level');
      return;
    }

    // Check credits
    const requiredCredits = files.length;
    if (user && user.credits < requiredCredits) {
      setError(`Insufficient credits. You need ${requiredCredits} credits but have ${user.credits}.`);
      return;
    }

    setLoading(true);

    try {
      if (mode === 'single' && files.length === 1) {
        await generationAPI.generateSingle(files[0], selectedUniversity, selectedLevel);
      } else {
        await generationAPI.generateBatch(files, selectedUniversity, selectedLevel);
      }

      setSuccess(true);
      await refreshUser(); // Refresh to update credits

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

  if (!user) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      <main className="flex-grow container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-4xl font-bold mb-2">Generate Graduation Portrait</h1>
          <p className="text-gray-600 mb-8">
            Upload your portrait and select your university to get started
          </p>

          {/* Credits Display */}
          <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-gray-600">Available Credits:</span>
                <span className="ml-2 text-2xl font-bold text-primary-600">{user.credits}</span>
              </div>
              <button
                onClick={() => router.push('/credits')}
                className="text-primary-600 hover:text-primary-700 font-semibold"
              >
                Buy More
              </button>
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
                  Upload Portrait(s)
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer"
                  >
                    <div className="text-gray-400 mb-2">
                      <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </div>
                    <p className="text-sm text-gray-600">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      PNG, JPG, WEBP up to 10MB each
                    </p>
                  </label>
                </div>
                {files.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 mb-3">
                      Selected Files ({files.length}):
                    </p>

                    {/* Image Previews */}
                    <div className={`grid gap-4 mb-3 ${files.length === 1 ? 'grid-cols-1' : 'grid-cols-2 md:grid-cols-3'}`}>
                      {previewUrls.map((url, idx) => (
                        <div key={idx} className="relative">
                          <div className="border-2 border-gray-200 rounded-lg overflow-hidden bg-white">
                            <img
                              src={url}
                              alt={files[idx].name}
                              className="w-full h-48 object-cover"
                            />
                          </div>
                          <p className="text-xs text-gray-600 mt-1 truncate" title={files[idx].name}>
                            {files[idx].name}
                          </p>
                        </div>
                      ))}
                    </div>

                    <p className="text-sm text-gray-500 mt-2">
                      Cost: {files.length} credit{files.length > 1 ? 's' : ''}
                    </p>
                  </div>
                )}
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
                    setSelectedLevel(''); // Reset level when university changes
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
                disabled={loading || files.length === 0 || !selectedUniversity || !selectedLevel}
                className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Generating...' : `Generate Portrait${files.length > 1 ? 's' : ''}`}
              </button>
            </form>
          </div>

          {/* Info Box */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Tips for Best Results:</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Use a clear, front-facing portrait</li>
              <li>• Ensure good lighting on your face</li>
              <li>• Avoid sunglasses or heavy filters</li>
              <li>• Higher resolution images work better</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
