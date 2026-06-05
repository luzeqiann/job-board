import { FilterState } from "@/types";

export function StatsBar({ totalResults, filters }: { totalResults: number; filters: FilterState }) {
  const n = filters.companies.length + filters.locations.length + filters.jobTypes.length + filters.categories.length + (filters.showNewOnly?1:0) + (filters.keyword?1:0);
  return <div className="text-sm text-gray-500">共 <span className="font-semibold text-gray-700">{totalResults}</span> 个岗位{n>0 && <span className="ml-1">(已筛选 {n} 个条件)</span>}</div>;
}
