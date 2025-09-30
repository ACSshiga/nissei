'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authStorage } from '@/lib/auth';

export default function MastersPage() {
  const router = useRouter();

  useEffect(() => {
    const token = authStorage.getToken();
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const masterTypes = [
    {
      id: 'shinchoku',
      title: '進捗マスタ',
      description: '案件の進捗ステータスを管理します',
      href: '/masters/shinchoku',
    },
    {
      id: 'sagyou-kubun',
      title: '作業区分マスタ',
      description: '作業の分類（盤配、線加工、委託など）を管理します',
      href: '/masters/sagyou-kubun',
    },
    {
      id: 'toiawase',
      title: '問い合わせマスタ',
      description: '問い合わせステータスを管理します',
      href: '/masters/toiawase',
    },
    {
      id: 'machine-series',
      title: '機種シリーズマスタ',
      description: '機種シリーズ（NEX, FNX, TNSなど）の情報を管理します',
      href: '/masters/machine-series',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">マスタ管理</h1>
          <Link href="/dashboard">
            <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md">
              ダッシュボードに戻る
            </button>
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {masterTypes.map((master) => (
            <Link key={master.id} href={master.href}>
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">{master.title}</h2>
                <p className="text-gray-600">{master.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}