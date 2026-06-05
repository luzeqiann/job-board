"use client";
import { FilterState } from "@/types";

type FG = { label: string; key: keyof FilterState; options: string[]; selected: string[] };

export function FilterPanel({ filters, onToggleFilter, onToggleNewOnly, onClearAll, filterGroups, hasActiveFilters }: {
  filters: FilterState;
  onToggleFilter: (g: keyof FilterState, v: string) => void;
  onToggleNewOnly: () => void;
  onClearAll: () => void;
  filterGroups: FG[];
  hasActiveFilters: boolean;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-700">筛选</h3>
        {hasActiveFilters && <button onClick={onClearAll} className="text-xs text-blue-600 hover:text-blue-800">清除全部</button>}
      </div>
      <label className="flex items-center gap-2 cursor-pointer select-none">
        <input type="checkbox" checked={filters.showNewOnly} onChange={onToggleNewOnly} className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
        <span className="text-sm text-gray-600">只显示新增岗位</span>
      </label>
      {filterGroups.map(g => (
        <div key={g.key}>
          <p className="text-xs font-medium text-gray-500 mb-2">{g.label}</p>
          <div className="flex flex-wrap gap-1.5">
            {g.options.map(opt => {
              const sel = g.selected.includes(opt);
              return <button key={opt} onClick={() => onToggleFilter(g.key, opt)} className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${sel ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>{opt}</button>;
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
