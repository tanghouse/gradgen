'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white shadow-sm">
      <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-primary-600">
          GradGen
        </Link>

        <div className="flex items-center space-x-6">
          {user ? (
            <>
              <Link href="/generate" className="text-gray-600 hover:text-gray-900">
                Generate
              </Link>
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                My Photos
              </Link>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">{user.email}</span>
                <button
                  onClick={logout}
                  className="text-gray-600 hover:text-gray-900"
                >
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link href="/login" className="text-gray-600 hover:text-gray-900">
                Login
              </Link>
              <Link
                href="/register"
                className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
              >
                Try Free
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
