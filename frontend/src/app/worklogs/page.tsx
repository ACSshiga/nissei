'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, WorkLog, Project } from '@/lib/api';
import { authStorage } from '@/lib/auth';

type TabType = 'input' | 'list' | 'summary';

export default function WorklogsPage() {
  const router = useRouter();
  const [worklogs, setWorklogs] = useState<WorkLog[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('input');
  const [editingRow, setEditingRow] = useState<string | null>(null);

  // スプレッドシート行データ（入力用）
  const [rows, setRows] = useState<Array<{
    id: string;
    project_id: string;
    work_date: string;
    start_time: string;
    end_time: string;
    duration_minutes: number;
    work_content: string;
  }>>([
    {
      id: 'new-1',
      project_id: '',
      work_date: new Date().toISOString().split('T')[0],
      start_time: '',
      end_time: '',
      duration_minutes: 0,
      work_content: '',
    },
  ]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const token = authStorage.getToken();
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const [worklogsResponse, projectsResponse] = await Promise.all([
        api.worklogs.list(token, { per_page: 100 }),
        api.projects.list(token, { per_page: 100 }),
      ]);
      setWorklogs(worklogsResponse.worklogs);
      setProjects(projectsResponse.projects);
    } catch (error) {
      console.error('データの取得に失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveRow = async (row: typeof rows[0]) => {
    if (!row.project_id || row.duration_minutes < 1) {
      alert('案件と作業時間（1分以上）を入力してください');
      return;
    }

    const token = authStorage.getToken();
    if (!token) return;

    try {
      const isEditing = editingRow && row.id === editingRow;

      if (isEditing) {
        // 編集モード: update APIを呼び出し
        await api.worklogs.update(token, row.id, {
          project_id: row.project_id,
          work_date: row.work_date,
          start_time: row.start_time || undefined,
          end_time: row.end_time || undefined,
          duration_minutes: row.duration_minutes,
          work_content: row.work_content || undefined,
        });
        alert('工数を更新しました');
        setEditingRow(null);
      } else {
        // 新規作成モード: create APIを呼び出し
        await api.worklogs.create(token, {
          project_id: row.project_id,
          work_date: row.work_date,
          start_time: row.start_time || undefined,
          end_time: row.end_time || undefined,
          duration_minutes: row.duration_minutes,
          work_content: row.work_content || undefined,
        });
        alert('工数を保存しました');
      }

      await loadData();

      // 新しい空行を追加
      setRows([
        {
          id: `new-${Date.now()}`,
          project_id: '',
          work_date: new Date().toISOString().split('T')[0],
          start_time: '',
          end_time: '',
          duration_minutes: 0,
          work_content: '',
        },
      ]);
    } catch (error) {
      console.error('工数の保存に失敗:', error);
      alert('工数の保存に失敗しました');
    }
  };

  const handleEditWorklog = (worklog: WorkLog) => {
    setEditingRow(worklog.id);
    // 編集モードに切り替え、既存データを編集用の行データとして設定
    setRows([{
      id: worklog.id,
      project_id: worklog.project_id,
      work_date: worklog.work_date,
      start_time: worklog.start_time || '',
      end_time: worklog.end_time || '',
      duration_minutes: worklog.duration_minutes,
      work_content: worklog.work_content || '',
    }]);
    setActiveTab('input');
  };

  const handleDeleteWorklog = async (worklogId: string) => {
    if (!confirm('この工数を削除しますか？')) return;

    const token = authStorage.getToken();
    if (!token) return;

    try {
      await api.worklogs.delete(token, worklogId);
      alert('工数を削除しました');
      await loadData();
    } catch (error) {
      console.error('工数の削除に失敗:', error);
      alert('工数の削除に失敗しました');
    }
  };

  const addNewRow = () => {
    setRows([
      ...rows,
      {
        id: `new-${Date.now()}`,
        project_id: '',
        work_date: new Date().toISOString().split('T')[0],
        start_time: '',
        end_time: '',
        duration_minutes: 0,
        work_content: '',
      },
    ]);
  };

  const updateRow = (id: string, field: string, value: any) => {
    setRows(rows.map(row => row.id === id ? { ...row, [field]: value } : row));
  };

  const formatMinutesToHours = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}:${mins.toString().padStart(2, '0')}`;
  };

  const getProjectName = (projectId: string) => {
    const project = projects.find((p) => p.id === projectId);
    return project ? `${project.management_no}` : '';
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* 左サイドバー - タブ切替 */}
      <div className="w-64 bg-white shadow-lg flex flex-col">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold text-gray-800">工数管理</h1>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <button
            onClick={() => setActiveTab('input')}
            className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'input'
                ? 'bg-blue-600 text-white font-medium'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            📝 工数入力
          </button>

          <button
            onClick={() => setActiveTab('list')}
            className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'list'
                ? 'bg-blue-600 text-white font-medium'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            📋 工数一覧
          </button>

          <button
            onClick={() => setActiveTab('summary')}
            className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'summary'
                ? 'bg-blue-600 text-white font-medium'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            📊 集計
          </button>
        </nav>

        <div className="p-4 border-t">
          <button
            onClick={() => router.push('/dashboard')}
            className="w-full px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
          >
            ← ダッシュボード
          </button>
        </div>
      </div>

      {/* メインコンテンツエリア */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* ヘッダー */}
        <div className="bg-white shadow-sm px-6 py-4 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-800">
              {activeTab === 'input' && '工数入力'}
              {activeTab === 'list' && '工数一覧'}
              {activeTab === 'summary' && '工数集計'}
            </h2>
            <div className="text-sm text-gray-600">
              {new Date().toLocaleDateString('ja-JP', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long'
              })}
            </div>
          </div>
        </div>

        {/* スプレッドシート風コンテンツ */}
        <div className="flex-1 overflow-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500">読み込み中...</div>
            </div>
          ) : (
            <>
              {/* 工数入力タブ */}
              {activeTab === 'input' && (
                <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr className="bg-blue-600 text-white">
                          <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold w-12">#</th>
                          <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold min-w-[200px]">案件 *</th>
                          <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold w-36">作業日 *</th>
                          <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold w-28">開始</th>
                          <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold w-28">終了</th>
                          <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold w-28">時間(分) *</th>
                          <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold min-w-[300px]">作業内容</th>
                          <th className="border border-gray-300 px-4 py-3 text-center text-sm font-semibold w-32">操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        {rows.map((row, index) => (
                          <tr key={row.id} className="hover:bg-gray-50">
                            <td className="border border-gray-300 px-4 py-2 text-sm text-gray-600 text-center">
                              {index + 1}
                            </td>
                            <td className="border border-gray-300 px-2 py-2">
                              <select
                                value={row.project_id}
                                onChange={(e) => updateRow(row.id, 'project_id', e.target.value)}
                                className="w-full px-2 py-1 text-sm border-0 focus:ring-2 focus:ring-blue-500 rounded"
                              >
                                <option value="">選択...</option>
                                {projects.map((project) => (
                                  <option key={project.id} value={project.id}>
                                    {project.management_no} - {project.machine_no}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td className="border border-gray-300 px-2 py-2">
                              <input
                                type="date"
                                value={row.work_date}
                                onChange={(e) => updateRow(row.id, 'work_date', e.target.value)}
                                className="w-full px-2 py-1 text-sm border-0 focus:ring-2 focus:ring-blue-500 rounded"
                              />
                            </td>
                            <td className="border border-gray-300 px-2 py-2">
                              <input
                                type="time"
                                value={row.start_time}
                                onChange={(e) => updateRow(row.id, 'start_time', e.target.value)}
                                className="w-full px-2 py-1 text-sm border-0 focus:ring-2 focus:ring-blue-500 rounded"
                              />
                            </td>
                            <td className="border border-gray-300 px-2 py-2">
                              <input
                                type="time"
                                value={row.end_time}
                                onChange={(e) => updateRow(row.id, 'end_time', e.target.value)}
                                className="w-full px-2 py-1 text-sm border-0 focus:ring-2 focus:ring-blue-500 rounded"
                              />
                            </td>
                            <td className="border border-gray-300 px-2 py-2">
                              <input
                                type="number"
                                value={row.duration_minutes || ''}
                                onChange={(e) => updateRow(row.id, 'duration_minutes', parseInt(e.target.value) || 0)}
                                min="0"
                                className="w-full px-2 py-1 text-sm border-0 focus:ring-2 focus:ring-blue-500 rounded text-right"
                              />
                            </td>
                            <td className="border border-gray-300 px-2 py-2">
                              <input
                                type="text"
                                value={row.work_content}
                                onChange={(e) => updateRow(row.id, 'work_content', e.target.value)}
                                placeholder="作業内容を入力..."
                                className="w-full px-2 py-1 text-sm border-0 focus:ring-2 focus:ring-blue-500 rounded"
                              />
                            </td>
                            <td className="border border-gray-300 px-2 py-2 text-center">
                              <button
                                onClick={() => handleSaveRow(row)}
                                className="px-3 py-1 text-xs font-medium text-white bg-green-600 hover:bg-green-700 rounded"
                              >
                                保存
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="p-4 border-t bg-gray-50">
                    <button
                      onClick={addNewRow}
                      className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                      + 行を追加
                    </button>
                  </div>
                </div>
              )}

              {/* 工数一覧タブ */}
              {activeTab === 'list' && (
                <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                  {worklogs.length === 0 ? (
                    <div className="p-12 text-center text-gray-500">
                      工数データがありません
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full border-collapse">
                        <thead>
                          <tr className="bg-gray-800 text-white">
                            <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold">作業日</th>
                            <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold">案件</th>
                            <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold">開始</th>
                            <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold">終了</th>
                            <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold">時間</th>
                            <th className="border border-gray-300 px-4 py-3 text-left text-sm font-semibold">作業内容</th>
                            <th className="border border-gray-300 px-4 py-3 text-center text-sm font-semibold w-32">操作</th>
                          </tr>
                        </thead>
                        <tbody>
                          {worklogs.map((worklog) => (
                            <tr key={worklog.id} className="hover:bg-gray-50">
                              <td className="border border-gray-300 px-4 py-3 text-sm">{worklog.work_date}</td>
                              <td className="border border-gray-300 px-4 py-3 text-sm">{getProjectName(worklog.project_id)}</td>
                              <td className="border border-gray-300 px-4 py-3 text-sm">{worklog.start_time || '-'}</td>
                              <td className="border border-gray-300 px-4 py-3 text-sm">{worklog.end_time || '-'}</td>
                              <td className="border border-gray-300 px-4 py-3 text-sm text-right">{formatMinutesToHours(worklog.duration_minutes)}</td>
                              <td className="border border-gray-300 px-4 py-3 text-sm">{worklog.work_content || '-'}</td>
                              <td className="border border-gray-300 px-4 py-3 text-center">
                                <div className="flex gap-2 justify-center">
                                  <button
                                    onClick={() => handleEditWorklog(worklog)}
                                    className="px-3 py-1 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded"
                                  >
                                    編集
                                  </button>
                                  <button
                                    onClick={() => handleDeleteWorklog(worklog.id)}
                                    className="px-3 py-1 text-xs font-medium text-white bg-red-600 hover:bg-red-700 rounded"
                                  >
                                    削除
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}

              {/* 集計タブ */}
              {activeTab === 'summary' && (
                <div className="bg-white rounded-lg shadow-lg p-8">
                  <div className="text-center text-gray-500">
                    集計機能は今後実装予定です
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
