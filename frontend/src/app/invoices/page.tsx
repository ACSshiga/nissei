'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authStorage } from '@/lib/auth';

interface InvoicePreviewItem {
  management_no: string;
  machine_no: string;
  actual_hours: number;
}

interface InvoicePreview {
  month: string;
  total_hours: number;
  items: InvoicePreviewItem[];
}

export default function InvoicesPage() {
  const router = useRouter();
  const [selectedMonth, setSelectedMonth] = useState('');
  const [preview, setPreview] = useState<InvoicePreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // 当月をデフォルト値として設定
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    setSelectedMonth(`${year}-${month}`);

    // 管理者権限チェック
    const user = authStorage.getUser();
    setIsAdmin(user?.is_admin || false);
  }, []);

  const loadPreview = async () => {
    if (!selectedMonth) return;

    const token = authStorage.getToken();
    if (!token) {
      router.push('/login');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/invoices/preview?month=${selectedMonth}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('請求プレビューの取得に失敗しました');
      }

      const data = await response.json();
      setPreview(data);
    } catch (error) {
      console.error('請求プレビューの取得に失敗:', error);
      alert('請求プレビューの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = async () => {
    if (!isAdmin) {
      alert('請求書の確定は管理者のみ実行できます');
      return;
    }

    if (!confirm('請求書を確定しますか？確定後は編集できません。')) {
      return;
    }

    const token = authStorage.getToken();
    if (!token) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/invoices/close?month=${selectedMonth}`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('請求書の確定に失敗しました');
      }

      alert('請求書を確定しました');
      loadPreview(); // 再読み込み
    } catch (error) {
      console.error('請求書の確定に失敗:', error);
      alert('請求書の確定に失敗しました');
    }
  };

  const handleExport = async () => {
    if (!selectedMonth) return;

    const token = authStorage.getToken();
    if (!token) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/invoices/export?month=${selectedMonth}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('CSVエクスポートに失敗しました');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice_${selectedMonth}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('CSVエクスポートに失敗:', error);
      alert('CSVエクスポートに失敗しました');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">請求書管理</h1>
          <Link
            href="/dashboard"
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
          >
            ダッシュボードへ
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 月選択 */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">請求月選択</h2>
          <div className="flex gap-4 items-center">
            <input
              type="month"
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="border rounded px-3 py-2"
            />
            <button
              onClick={loadPreview}
              disabled={loading || !selectedMonth}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-300"
            >
              {loading ? 'Loading...' : 'プレビュー'}
            </button>
          </div>
        </div>

        {/* プレビュー表示 */}
        {preview && (
          <>
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">
                  {preview.month} 請求プレビュー
                </h2>
                <div className="flex gap-2">
                  <button
                    onClick={handleExport}
                    className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                  >
                    CSV出力
                  </button>
                  {isAdmin && (
                    <button
                      onClick={handleClose}
                      className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                    >
                      請求確定
                    </button>
                  )}
                </div>
              </div>

              <div className="mb-4">
                <p className="text-lg">
                  合計工数: <span className="font-bold">{preview.total_hours}H</span>
                </p>
              </div>

              {preview.items.length === 0 ? (
                <p className="text-gray-500">請求対象の工数がありません</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          管理No
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          委託業務内容
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          実工数
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {preview.items.map((item, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.management_no}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.machine_no}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                            {item.actual_hours}H
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
