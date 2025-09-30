'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, MasterShinchoku, MasterSagyouKubun, MasterToiawase, MachineSeriesMaster } from '@/lib/api';
import { authStorage } from '@/lib/auth';

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  // マスタデータ
  const [shinchokuList, setShinchokuList] = useState<MasterShinchoku[]>([]);
  const [sagyouKubunList, setSagyouKubunList] = useState<MasterSagyouKubun[]>([]);
  const [toiawaseList, setToiawaseList] = useState<MasterToiawase[]>([]);
  const [machineSeriesList, setMachineSeriesList] = useState<MachineSeriesMaster[]>([]);

  // フォームデータ
  const [formData, setFormData] = useState({
    management_no: '',
    machine_series_id: '',
    generation: '',
    tonnage: '',
    spec_tags: '',
    machine_no: '',
    commission_content: '',
    toiawase_id: '',
    sagyou_kubun_id: '',
    estimated_hours: '',
    shinchoku_id: '',
    start_date: '',
    completion_date: '',
    drawing_deadline: '',
  });

  useEffect(() => {
    loadMasters();
  }, []);

  const loadMasters = async () => {
    const token = authStorage.getToken();
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const [shinchoku, sagyouKubun, toiawase, machineSeries] = await Promise.all([
        api.masters.shinchoku.list(token, false),
        api.masters.sagyouKubun.list(token, false),
        api.masters.toiawase.list(token, false),
        api.masters.machineSeries.list(token, false),
      ]);
      setShinchokuList(shinchoku);
      setSagyouKubunList(sagyouKubun);
      setToiawaseList(toiawase);
      setMachineSeriesList(machineSeries);
    } catch (error) {
      console.error('マスタデータの取得に失敗:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = authStorage.getToken();
    if (!token) return;

    setLoading(true);
    try {
      const payload = {
        ...formData,
        machine_series_id: formData.machine_series_id || null,
        toiawase_id: formData.toiawase_id || null,
        sagyou_kubun_id: formData.sagyou_kubun_id || null,
        shinchoku_id: formData.shinchoku_id || null,
        estimated_hours: formData.estimated_hours ? parseInt(formData.estimated_hours) : null,
        start_date: formData.start_date || null,
        completion_date: formData.completion_date || null,
        drawing_deadline: formData.drawing_deadline || null,
      };

      const project = await api.projects.create(token, payload);
      alert('案件を作成しました');
      router.push(`/projects/${project.id}`);
    } catch (error: any) {
      console.error('案件の作成に失敗:', error);
      alert(`案件の作成に失敗しました: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">新規案件作成</h1>
          <Link href="/projects">
            <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md">
              案件一覧に戻る
            </button>
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 基本情報 */}
            <div>
              <h2 className="text-lg font-semibold mb-4">基本情報</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    管理No *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.management_no}
                    onChange={(e) => setFormData({ ...formData, management_no: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    機番
                  </label>
                  <input
                    type="text"
                    value={formData.machine_no}
                    onChange={(e) => setFormData({ ...formData, machine_no: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    機種シリーズ
                  </label>
                  <select
                    value={formData.machine_series_id}
                    onChange={(e) => setFormData({ ...formData, machine_series_id: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">選択してください</option>
                    {machineSeriesList.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.display_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    世代
                  </label>
                  <input
                    type="text"
                    value={formData.generation}
                    onChange={(e) => setFormData({ ...formData, generation: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    トン数
                  </label>
                  <input
                    type="text"
                    value={formData.tonnage}
                    onChange={(e) => setFormData({ ...formData, tonnage: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    仕様タグ
                  </label>
                  <input
                    type="text"
                    value={formData.spec_tags}
                    onChange={(e) => setFormData({ ...formData, spec_tags: e.target.value })}
                    placeholder="複数の場合はカンマ区切り"
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    業務委託内容
                  </label>
                  <textarea
                    rows={3}
                    value={formData.commission_content}
                    onChange={(e) => setFormData({ ...formData, commission_content: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* ステータス・工数 */}
            <div>
              <h2 className="text-lg font-semibold mb-4">ステータス・工数</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    進捗
                  </label>
                  <select
                    value={formData.shinchoku_id}
                    onChange={(e) => setFormData({ ...formData, shinchoku_id: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">選択してください</option>
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
                    value={formData.sagyou_kubun_id}
                    onChange={(e) => setFormData({ ...formData, sagyou_kubun_id: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">選択してください</option>
                    {sagyouKubunList.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.kubun_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    問い合わせ
                  </label>
                  <select
                    value={formData.toiawase_id}
                    onChange={(e) => setFormData({ ...formData, toiawase_id: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">選択してください</option>
                    {toiawaseList.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.status_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    予定工数（分）
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={formData.estimated_hours}
                    onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* 日付 */}
            <div>
              <h2 className="text-lg font-semibold mb-4">日付</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    仕掛日
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    完了日
                  </label>
                  <input
                    type="date"
                    value={formData.completion_date}
                    onChange={(e) => setFormData({ ...formData, completion_date: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    作図期限
                  </label>
                  <input
                    type="date"
                    value={formData.drawing_deadline}
                    onChange={(e) => setFormData({ ...formData, drawing_deadline: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* ボタン */}
            <div className="flex justify-end gap-4">
              <Link href="/projects">
                <button
                  type="button"
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  キャンセル
                </button>
              </Link>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50"
              >
                {loading ? '作成中...' : '案件を作成'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}