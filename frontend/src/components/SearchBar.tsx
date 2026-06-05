"use client";
import { SearchIcon, XIcon } from "lucide-react";

export function SearchBar({ value, onChange, placeholder = "搜索岗位名称、公司、技能关键词..." }: { value: string; onChange: (v: string) => void; placeholder?: string }) {
  return (
    <div className="relative">
      <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
      <input type="text" value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder}
        className="w-full pl-10 pr-10 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white shadow-sm text-sm" />
      {value && <button onClick={() => onChange("")} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" aria-label="清除"><XIcon className="w-5 h-5" /></button>}
    </div>
  );
}
