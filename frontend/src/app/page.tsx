export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">
          Nissei 工数管理システム
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          工数管理と請求処理のためのシステム
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/login"
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            ログイン
          </a>
          <a
            href="/register"
            className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
          >
            新規登録
          </a>
        </div>
      </div>
    </main>
  )
}