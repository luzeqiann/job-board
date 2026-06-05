"use client";
import { BriefcaseIcon, SparklesIcon } from "lucide-react";

export function Header({ totalJobs, newJobs, lastUpdate }: { totalJobs: number; newJobs: number; lastUpdate: string }) {
  const fmt = (iso: string) => {
    if (!iso) return "";
    try { return new Date(iso).toLocaleString("zh-CN", { year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit" }); }
    catch { return iso; }
  };
  return (
    <header className="bg-gradient-to-r from-blue-700 to-blue-900 text-white">
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3"><BriefcaseIcon className="w-8 h-8" />华南AI岗位聚合</h1>
            <p className="mt-2 text-blue-200 text-sm sm:text-base">关注广州、深圳 AI应用工程师 / RPA开发 / 大模型应用 岗位</p>
          </div>
          <div className="flex gap-6 text-sm">
            <div className="text-center"><p className="text-2xl font-bold">{totalJobs}</p><p className="text-blue-200">岗位总数</p></div>
            <div className="text-center"><p className="text-2xl font-bold text-yellow-300">{newJobs}</p><p className="text-blue-200"><SparklesIcon className="w-4 h-4 inline mr-1" />新增</p></div>
          </div>
        </div>
        {lastUpdate && <p className="mt-3 text-xs text-blue-300">最后更新: {fmt(lastUpdate)}</p>}
      </div>
    </header>
  );
}
