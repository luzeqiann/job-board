"use client";
import { Job } from "@/types";
import { MapPinIcon, CalendarIcon, BuildingIcon, ExternalLinkIcon } from "lucide-react";
import { NewBadge } from "./NewBadge";

export function JobCard({ job }: { job: Job }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-lg font-semibold text-gray-900 truncate">{job.title}</h3>
            {job.isNew && <NewBadge />}
          </div>
          <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-gray-500">
            <span className="flex items-center gap-1"><BuildingIcon className="w-4 h-4" />{job.company}</span>
            <span className="flex items-center gap-1"><MapPinIcon className="w-4 h-4" />{job.locationCity || job.location || "未知"}</span>
            <span className="flex items-center gap-1"><CalendarIcon className="w-4 h-4" />{job.postDate}</span>
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            <span className={job.jobType === "校招" ? "badge-campus" : "badge-social"}>{job.jobType}</span>
            <span className="badge-campus">{job.category}</span>
          </div>
          {job.tags && job.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {job.tags.slice(0, 8).map(t => <span key={t} className="tag-chip">{t}</span>)}
            </div>
          )}
          <p className="mt-3 text-sm text-gray-600 line-clamp-2">
            {job.requirements?.slice(0, 200) || job.description?.slice(0, 200) || ""}
          </p>
        </div>
        <a href={job.url} target="_blank" rel="noopener noreferrer"
           className="flex-shrink-0 inline-flex items-center gap-1 px-3 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors">
          <ExternalLinkIcon className="w-4 h-4" />查看
        </a>
      </div>
    </div>
  );
}
