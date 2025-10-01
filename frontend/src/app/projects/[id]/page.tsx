'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { api, Project } from '@/lib/api';
import { authStorage } from '@/lib/auth';

export default function ProjectDetailPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    const token = authStorage.getToken();
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const data = await api.projects.get(token, projectId);
      setProject(data);
    } catch (error) {
      console.error('案件の取得に失敗:', error);
      alert('案件の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('この案件を削除してもよろしいですか？')) {
      return;
    }

    const token = authStorage.getToken();
    if (!token) return;

    setDeleting(true);
    try {
      await api.projects.delete(token, projectId);
      alert('案件を削除しました');
      router.push('/projects');
    } catch (error) {
      console.error('削除に失敗:', error);
      alert('削除に失敗しました');
      setDeleting(false);
    }
  };

  const formatMinutesToHours = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}時間${mins}分`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">読み込み中...</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center text-gray-500">案件が見つかりません</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">案件詳細</h1>
          <div className="flex gap-4">
            <Link href={`/projects/${projectId}/edit`}>
              <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md">
                編集
              </button>
            </Link>
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md disabled:bg-gray-400"
            >
              {deleting ? '削除中...' : '削除'}
            </button>
            <Link href="/projects">
              <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md">
                一覧に戻る
              </button>
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 管理No */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                管理No
              </label>
              <div className="text-lg text-gray-900">{project.management_no}</div>
            </div>

            {/* 機番 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                機番
              </label>
              <div className="text-lg text-gray-900">{project.machine_no || '-'}</div>
            </div>

            {/* 機種シリーズ */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                機種シリーズ
              </label>
              <div className="text-lg text-gray-900">{project.machine_series_name || '-'}</div>
            </div>

            {/* 問合せ */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                問合せ
              </label>
              <div className="text-lg text-gray-900">{project.toiawase_name || '-'}</div>
            </div>

            {/* 作業区分 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                作業区分
              </label>
              <div className="text-lg text-gray-900">{project.sagyou_kubun_name || '-'}</div>
            </div>

            {/* 進捗 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                進捗
              </label>
              <div className="text-lg text-gray-900">{project.shinchoku_name || '-'}</div>
            </div>

            {/* 予定工数 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                予定工数
              </label>
              <div className="text-lg text-gray-900">
                {project.estimated_hours ? formatMinutesToHours(project.estimated_hours) : '-'}
              </div>
            </div>

            {/* 実績工数 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                実績工数
              </label>
              <div className="text-lg text-gray-900">
                {formatMinutesToHours(project.actual_hours)}
              </div>
            </div>

            {/* 仕掛日 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                仕掛日
              </label>
              <div className="text-lg text-gray-900">{project.start_date || '-'}</div>
            </div>

            {/* 完成日 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                完成日
              </label>
              <div className="text-lg text-gray-900">{project.completion_date || '-'}</div>
            </div>

            {/* 出荷日 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                出荷日
              </label>
              <div className="text-lg text-gray-900">{project.shipment_date || '-'}</div>
            </div>

            {/* 納入日 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                納入日
              </label>
              <div className="text-lg text-gray-900">{project.delivery_date || '-'}</div>
            </div>

            {/* 備考（全幅表示） */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                備考
              </label>
              <div className="text-lg text-gray-900 whitespace-pre-wrap">
                {project.memo || '-'}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
