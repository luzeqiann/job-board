export function Footer() {
  return (
    <footer className="bg-gray-100 border-t border-gray-200 mt-12">
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <p className="text-center text-xs text-gray-400">数据来源: 各公司官方招聘网站 &middot; 自动更新: 每日21:00 &middot; 仅供个人学习研究使用 &middot; 非商业用途</p>
        <p className="text-center text-xs text-gray-400 mt-1">&copy; {new Date().getFullYear()} 华南AI岗位聚合 &middot; Powered by GitHub Actions + Next.js</p>
      </div>
    </footer>
  );
}
