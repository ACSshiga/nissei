'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, Project, MasterShinchoku, MasterSagyouKubun } from '@/lib/api';
import { authStorage } from '@/lib/auth';

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [shinchokuList, setShinchokuList] = useState<MasterShinchoku[]>([]);
  const [sagyouKubunList, setSagyouKubunList] = useState<MasterSagyouKubun[]>([]);
  const [loading, setLoading] = useState(true);
  const [shinchokuFilter, setShinchokuFilter] = useState('');
  const [sagyouKubunFilter, setSagyouKubunFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadMasters();
    loadProjects();
  }, [shinchokuFilter, sagyouKubunFilter]);

  const loadMasters = async () => {
    const token = authStorage.getToken();
    if (!token) return;

    try {
      const [shinchoku, sagyouKubun] = await Promise.all([
        api.masters.shinchoku.list(token, false),
        api.masters.sagyouKubun.list(token, false),
      ]);
      setShinchokuList(shinchoku);
      setSagyouKubunList(sagyouKubun);
    } catch (error) {
      console.error('マスタデータの取得に失敗:', error);
    }
  };

  const loadProjects = async () => {
    const token = authStorage.getToken();
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const response = await api.projects.list(token, {
        shinchoku_id: shinchokuFilter || undefined,
        sagyou_kubun_id: sagyouKubunFilter || undefined,
        per_page: 100,
      });
      setProjects(response.projects);
    } catch (error) {
      console.error('案件一覧の取得に失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredProjects = projects.filter((project) => {
    if (!searchQuery) return true;
    return (
      project.management_no.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.machine_no?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  const formatMinutesToHours = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}時間${mins}分`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">案件一覧</h1>
          <div className="flex gap-4">
            <Link href="/projects/new">
              <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md">
                新規案件
              </button>
            </Link>
            <Link href="/dashboard">
              <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md">
                ダッシュボードに戻る
              </button>
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* フィルター */}
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                進捗
              </label>
              <select
                value={shinchokuFilter}
                onChange={(e) => setShinchokuFilter(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">全て</option>
                {shinchokuList.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.status_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                作業区分
              </label>
              <select
                value={sagyouKubunFilter}
                onChange={(e) => setSagyouKubunFilter(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">全て</option>
                {sagyouKubunList.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.kubun_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                検索（管理No / 機番）
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="管理Noまたは機番で検索"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 案件一覧テーブル */}
        {loading ? (
          <div className="text-center py-12">読み込み中...</div>
        ) : filteredProjects.length === 0 ? (
          <div className="bg-white p-12 rounded-lg shadow text-center text-gray-500">
            案件が見つかりません
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    管理No
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    機番
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    機種シリーズ
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    進捗
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    作業区分
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    予定工数
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    実績工数
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    仕掛日
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredProjects.map((project) => (
                  <tr key={project.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                      <Link href={`/projects/${project.id}`}>
                        {project.management_no}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {project.machine_no || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {project.machine_series_name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {project.shinchoku_name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {project.sagyou_kubun_name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {project.estimated_hours ? formatMinutesToHours(project.estimated_hours) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatMinutesToHours(project.actual_hours)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {project.start_date || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}