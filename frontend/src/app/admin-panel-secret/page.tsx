'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, User } from '@/lib/api';
import { authStorage } from '@/lib/auth';

export default function AdminPanelPage() {
  const router = useRouter();
  const [users, setUsers] = useState<Array<User & { is_active: boolean; is_admin: boolean }>>([]);
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<any>(null);

  useEffect(() => {
    checkAdminAndLoadData();
  }, []);

  const checkAdminAndLoadData = async () => {
    const token = authStorage.getToken();
    const user = authStorage.getUser();

    if (!token || !user) {
      router.push('/login');
      return;
    }

    // 管理者権限チェック
    if (!user.is_admin) {
      alert('管理者権限がありません');
      router.push('/dashboard');
      return;
    }

    setCurrentUser(user);
    await loadUsers();
  };

  const loadUsers = async () => {
    const token = authStorage.getToken();
    if (!token) return;

    try {
      const response = await api.admin.listUsers(token);
      setUsers(response.users);
    } catch (error) {
      console.error('ユーザー一覧の取得に失敗:', error);
      alert('ユーザー一覧の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: string, username: string) => {
    if (!confirm(`ユーザー「${username}」を削除しますか？この操作は取り消せません。`)) {
      return;
    }

    const token = authStorage.getToken();
    if (!token) return;

    try {
      await api.admin.deleteUser(token, userId);
      alert('ユーザーを削除しました');
      await loadUsers();
    } catch (error: any) {
      console.error('ユーザー削除に失敗:', error);
      alert(error.message || 'ユーザー削除に失敗しました');
    }
  };

  const handleToggleActive = async (userId: string, currentStatus: boolean) => {
    const token = authStorage.getToken();
    if (!token) return;

    try {
      if (currentStatus) {
        await api.admin.deactivateUser(token, userId);
        alert('ユーザーを非アクティブ化しました');
      } else {
        await api.admin.activateUser(token, userId);
        alert('ユーザーをアクティブ化しました');
      }
      await loadUsers();
    } catch (error: any) {
      console.error('ステータス変更に失敗:', error);
      alert(error.message || 'ステータス変更に失敗しました');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-red-600 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">🔐 管理者パネル</h1>
            <p className="text-sm text-red-100 mt-1">この画面は管理者のみアクセス可能です</p>
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 text-sm font-medium text-red-600 bg-white hover:bg-gray-100 rounded-md"
          >
            ダッシュボードに戻る
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ユーザー管理セクション */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">ユーザー管理</h2>
          </div>

          {loading ? (
            <div className="p-12 text-center text-gray-500">読み込み中...</div>
          ) : users.length === 0 ? (
            <div className="p-12 text-center text-gray-500">ユーザーがいません</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ユーザー名
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      メールアドレス
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ステータス
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      権限
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      登録日
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id} className={user.is_active ? '' : 'bg-gray-100'}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{user.username}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{user.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {user.is_active ? (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            アクティブ
                          </span>
                        ) : (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                            非アクティブ
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {user.is_admin ? (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                            管理者
                          </span>
                        ) : (
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                            一般
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString('ja-JP')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                        <div className="flex justify-center gap-2">
                          <button
                            onClick={() => handleToggleActive(user.id, user.is_active)}
                            disabled={user.id === currentUser?.id}
                            className={`px-3 py-1 text-xs rounded ${
                              user.id === currentUser?.id
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : user.is_active
                                ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                                : 'bg-green-600 text-white hover:bg-green-700'
                            }`}
                          >
                            {user.is_active ? '無効化' : '有効化'}
                          </button>
                          <button
                            onClick={() => handleDeleteUser(user.id, user.username)}
                            disabled={user.id === currentUser?.id}
                            className={`px-3 py-1 text-xs rounded ${
                              user.id === currentUser?.id
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-red-600 text-white hover:bg-red-700'
                            }`}
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

        {/* 今後の機能拡張エリア */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">今後の管理機能</h3>
          <ul className="list-disc list-inside space-y-2 text-sm text-gray-600">
            <li>マスタデータの一括管理</li>
            <li>システム設定の変更</li>
            <li>ログの確認・エクスポート</li>
            <li>バックアップ・リストア機能</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
