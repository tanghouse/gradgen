'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { generationAPI, GenerationJob, JobStatus, TierStatus } from '@/lib/api';
import Navbar from '@/components/Navbar';
import ImageComparison from '@/components/ImageComparison';

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [pollingJobIds, setPollingJobIds] = useState<Set<number>>(new Set());
  const [tierStatus, setTierStatus] = useState<TierStatus | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  // Load jobs and tier status
  const loadJobs = async () => {
    try {
      const data = await generationAPI.listJobs();
      setJobs(data);

      // Start polling for pending/processing jobs
      const pendingJobs = data.filter(
        j => j.status === 'pending' || j.status === 'processing'
      );
      setPollingJobIds(new Set(pendingJobs.map(j => j.id)));
    } catch (err) {
      console.error('Failed to load jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadTierStatus = async () => {
    try {
      const status = await generationAPI.getTierStatus();
      setTierStatus(status);
    } catch (err) {
      console.error('Failed to load tier status:', err);
    }
  };

  useEffect(() => {
    if (user) {
      loadJobs();
      loadTierStatus();
    }
  }, [user]);

  // Poll for job updates
  useEffect(() => {
    if (pollingJobIds.size === 0) return;

    const interval = setInterval(async () => {
      const updatedJobs = [...jobs];
      let hasChanges = false;
      let shouldReloadJobs = false;

      for (const jobId of pollingJobIds) {
        try {
          const status = await generationAPI.getJobStatus(jobId);
          const jobIndex = updatedJobs.findIndex(j => j.id === jobId);

          if (jobIndex !== -1) {
            const currentJob = updatedJobs[jobIndex];

            // Check if anything changed
            if (currentJob.status !== status.status ||
                currentJob.completed_images !== status.completed_images) {
              hasChanges = true;
            }

            updatedJobs[jobIndex] = {
              ...updatedJobs[jobIndex],
              status: status.status,
              completed_images: status.completed_images,
            };

            // Stop polling if job is complete or failed, and reload full job data
            if (status.status === 'completed' || status.status === 'failed') {
              setPollingJobIds(prev => {
                const next = new Set(prev);
                next.delete(jobId);
                return next;
              });
              shouldReloadJobs = true;
            }
          }
        } catch (err) {
          console.error(`Failed to poll job ${jobId}:`, err);
        }
      }

      if (hasChanges) {
        setJobs(updatedJobs);
      }

      // Reload full job data when any job completes to get generated_images
      if (shouldReloadJobs) {
        await loadJobs();
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [pollingJobIds, jobs]);

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800',
    };
    return badges[status as keyof typeof badges] || badges.pending;
  };

  const handleDownload = async (imageId: number, filename: string) => {
    try {
      await generationAPI.downloadResult(imageId, `gradgen_${filename}`);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download image. Please try again.');
    }
  };

  if (authLoading || loading) {
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
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
            <p className="text-gray-600">View your generation jobs and download results</p>
          </div>

          {/* Tier Status Banner */}
          {tierStatus && (
            <div className={`mb-8 rounded-lg shadow-lg overflow-hidden ${
              tierStatus.tier === 'premium'
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600'
                : tierStatus.tier === 'premium_exhausted'
                  ? 'bg-gradient-to-r from-green-600 to-teal-600'
                  : tierStatus.has_used_free_tier
                    ? 'bg-gradient-to-r from-gray-600 to-gray-700'
                    : 'bg-gradient-to-r from-blue-600 to-cyan-600'
            }`}>
              <div className="p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-3xl">
                        {tierStatus.tier === 'premium'
                          ? '👑'
                          : tierStatus.tier === 'premium_exhausted'
                            ? '✅'
                            : tierStatus.has_used_free_tier
                              ? '🔒'
                              : '🎁'}
                      </span>
                      <h2 className="text-2xl font-bold">
                        {tierStatus.tier === 'premium'
                          ? 'Premium Account'
                          : tierStatus.tier === 'premium_exhausted'
                            ? 'All Generations Used'
                            : tierStatus.has_used_free_tier
                              ? 'Free Tier Used'
                              : 'Free Tier Available'}
                      </h2>
                    </div>
                    <p className="text-white/90">
                      {tierStatus.tier === 'premium'
                        ? `${tierStatus.premium_generations_remaining} generation${tierStatus.premium_generations_remaining === 1 ? '' : 's'} remaining • 5 photos per generation • No watermarks`
                        : tierStatus.tier === 'premium_exhausted'
                          ? 'Thank you for using GradGen! You\'ve used all your generations.'
                          : tierStatus.has_used_free_tier
                            ? 'Upgrade to Premium to generate more professional photos'
                            : '5 free watermarked photos available • Try it now!'}
                    </p>
                  </div>

                  {tierStatus.tier === 'free' && (
                    <button
                      onClick={() => router.push('/generate')}
                      className="bg-white text-gray-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors shadow-lg"
                    >
                      Try Free Tier
                    </button>
                  )}

                  {(tierStatus.tier === 'needs_payment' || tierStatus.has_used_free_tier) && tierStatus.tier !== 'premium_exhausted' && (
                    <button
                      onClick={() => router.push('/generate')}
                      className="bg-white text-gray-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors shadow-lg"
                    >
                      Upgrade to Premium
                    </button>
                  )}

                  {tierStatus.tier === 'premium' && (
                    <button
                      onClick={() => router.push('/generate')}
                      className="bg-white/20 text-white px-6 py-3 rounded-lg font-semibold hover:bg-white/30 transition-colors"
                    >
                      Generate Photos
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Stats Cards */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="text-sm text-gray-600 mb-1">Total Jobs</div>
              <div className="text-3xl font-bold text-gray-900">{jobs.length}</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="text-sm text-gray-600 mb-1">Completed Jobs</div>
              <div className="text-3xl font-bold text-green-600">
                {jobs.filter(j => j.status === 'completed').length}
              </div>
            </div>
          </div>

          {/* Jobs List */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold">Recent Jobs</h2>
            </div>

            {jobs.length === 0 ? (
              <div className="p-12 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                </div>
                <p className="text-gray-600 mb-4">No jobs yet</p>
                <button
                  onClick={() => router.push('/generate')}
                  className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
                >
                  Generate Your First Portrait
                </button>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {jobs.map((job) => (
                  <div key={job.id} className="p-6 hover:bg-gray-50">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-semibold text-lg">
                          {job.university} - {job.degree_level}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {new Date(job.created_at).toLocaleString()}
                        </p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(job.status)}`}>
                        {job.status}
                      </span>
                    </div>

                    {/* Progress Bar */}
                    {(job.status === 'processing' || job.status === 'completed') && (
                      <div className="mb-4">
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>Progress</span>
                          <span>{job.completed_images} / {job.total_images}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all"
                            style={{ width: `${(job.completed_images / job.total_images) * 100}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Error Message */}
                    {job.error_message && (
                      <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded">
                        {job.error_message}
                      </div>
                    )}

                    {/* Generated Images */}
                    {job.generated_images && job.generated_images.length > 0 && (
                      <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-gray-700 mb-3">
                          {job.completed_images} / {job.total_images} Photos Generated
                          {job.is_watermarked && <span className="ml-2 text-xs text-orange-600">(Watermarked - Free Tier)</span>}
                          {!job.is_watermarked && <span className="ml-2 text-xs text-green-600">(Premium - No Watermark)</span>}
                        </h4>

                        {/* Display photos in a grid (much more efficient!) */}
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                          {job.generated_images.map((img) => (
                            <div key={img.id} className="border border-gray-200 rounded-lg overflow-hidden bg-white">
                              {img.success && img.output_image_path ? (
                                <>
                                  <ImageComparison imageId={img.id} showOriginal={true} />
                                  <div className="p-3">
                                    <button
                                      onClick={() => handleDownload(img.id, img.original_filename)}
                                      className="w-full bg-primary-600 text-white px-3 py-2 rounded text-sm hover:bg-primary-700 transition-colors"
                                    >
                                      Download
                                    </button>
                                  </div>
                                </>
                              ) : (
                                <div className="p-4 text-center">
                                  <span className="text-2xl mb-2 block">❌</span>
                                  <p className="text-xs text-red-600">{img.error_message || 'Failed'}</p>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
