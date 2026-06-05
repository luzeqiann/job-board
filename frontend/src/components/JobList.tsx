"use client";
import { Job } from "@/types";
import { JobCard } from "./JobCard";

export function JobList({ jobs }: { jobs: Job[] }) {
  if (jobs.length === 0) {
    return <div className="text-center py-16 text-gray-400"><p className="text-lg">暂无匹配的岗位</p><p className="text-sm mt-2">试试调整搜索或筛选条件</p></div>;
  }
  return <div className="space-y-4">{jobs.map(j => <JobCard key={j.id} job={j} />)}</div>;
}
