'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { api, WorkLog, Project } from '@/lib/api';
import { authStorage } from '@/lib/auth';

export default function WorklogEditPage() {
  const router = useRouter();
  const params = useParams();
  const worklogId = params.id as string;

  const [worklog, setWorklog] = useState<WorkLog | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    project_id: '',
    work_date: '',
    start_time: '',
    end_time: '',
    duration_minutes: 0,
    work_content: '',
  });

  useEffect(() => {
    loadData();
  }, [worklogId]);

  const loadData = async () => {
    const token = authStorage.getToken();
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const [worklogData, projectsData] = await Promise.all([
        api.worklogs.get(token, worklogId),
        api.projects.list(token, { per_page: 100 }),
      ]);

      setWorklog(worklogData);
      setProjects(projectsData.projects);

      // フォームデータを初期化
      setFormData({
        project_id: worklogData.project_id,
        work_date: worklogData.work_date,
        start_time: worklogData.start_time || '',
        end_time: worklogData.end_time || '',
        duration_minutes: worklogData.duration_minutes,
        work_content: worklogData.work_content || '',
      });
    } catch (error) {
      console.error('データの取得に失敗:', error);
      alert('データの取得に失敗しました');
      router.push('/worklogs');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.project_id || formData.duration_minutes < 1) {
      alert('案件と作業時間（1分以上）を入力してください');
      return;
    }

    const token = authStorage.getToken();
    if (!token) return;

    setSubmitting(true);
    try {
      await api.worklogs.update(token, worklogId, formData);
      alert('工数を更新しました');
      router.push('/worklogs');
    } catch (error) {
      console.error('工数の更新に失敗:', error);
      alert('工数の更新に失敗しました');
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">読み込み中...</div>
      </div>
    );
  }

  if (!worklog) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">工数データが見つかりません</p>
          <Link href="/worklogs">
            <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md">
              工数入力一覧に戻る
            </button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">工数編集</h1>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 案件選択 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                案件 <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={formData.project_id}
                onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">選択してください</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.management_no} - {project.machine_no || '（機番なし）'}
                  </option>
                ))}
              </select>
            </div>

            {/* 作業日 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                作業日 <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                required
                value={formData.work_date}
                onChange={(e) => setFormData({ ...formData, work_date: e.target.value })}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 開始時刻 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  開始時刻
                </label>
                <input
                  type="time"
                  value={formData.start_time}
                  onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* 終了時刻 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  終了時刻
                </label>
                <input
                  type="time"
                  value={formData.end_time}
                  onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* 作業時間（分） */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                作業時間（分） <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                required
                min="1"
                value={formData.duration_minutes}
                onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) || 0 })}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="mt-1 text-sm text-gray-500">
                {Math.floor(formData.duration_minutes / 60)}時間{formData.duration_minutes % 60}分
              </p>
            </div>

            {/* 作業内容 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                作業内容
              </label>
              <textarea
                rows={4}
                value={formData.work_content}
                onChange={(e) => setFormData({ ...formData, work_content: e.target.value })}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="作業内容を入力してください"
              />
            </div>

            {/* ボタン */}
            <div className="flex justify-end gap-4 pt-4 border-t">
              <Link href="/worklogs">
                <button
                  type="button"
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  キャンセル
                </button>
              </Link>
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:bg-blue-300"
              >
                {submitting ? '更新中...' : '更新'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
