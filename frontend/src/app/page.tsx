"use client";

import { useState, useMemo, useEffect } from "react";
import { Job, FilterState, DEFAULT_FILTERS } from "@/types";
import { Header } from "@/components/Header";
import { SearchBar } from "@/components/SearchBar";
import { FilterPanel } from "@/components/FilterPanel";
import { JobList } from "@/components/JobList";
import { StatsBar } from "@/components/StatsBar";
import { Footer } from "@/components/Footer";
import { getUniqueCompanies, getUniqueLocations, getUniqueCategories, getUniqueJobTypes, getNewJobCount } from "@/lib/jobs";
import { searchJobs } from "@/lib/search";
import { applyFilters, sortJobs } from "@/lib/filters";

const BASE = "/job-board";

export default function HomePage() {
  const [allJobs, setAllJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [meta, setMeta] = useState<{ lastRun?: string }>({});
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);

  useEffect(() => {
    fetch(`${BASE}/merged.json`).then(r => r.ok ? r.json() : []).then(setAllJobs).catch(() => setAllJobs([])).finally(() => setLoading(false));
    fetch(`${BASE}/meta.json`).then(r => r.json()).then(setMeta).catch(() => {});
  }, []);

  const companies = useMemo(() => getUniqueCompanies(allJobs), [allJobs]);
  const locations = useMemo(() => getUniqueLocations(allJobs), [allJobs]);
  const categories = useMemo(() => getUniqueCategories(allJobs), [allJobs]);
  const jobTypes = useMemo(() => getUniqueJobTypes(allJobs), [allJobs]);
  const newJobCount = useMemo(() => getNewJobCount(allJobs), [allJobs]);

  const displayJobs = useMemo(() => {
    let jobs = applyFilters(allJobs, filters);
    if (filters.keyword) jobs = searchJobs(jobs, filters.keyword);
    return sortJobs(jobs);
  }, [allJobs, filters]);

  const toggle = (group: keyof FilterState, value: string) => setFilters(p => {
    const cur = p[group] as string[];
    if (typeof cur === "boolean") return p;
    return { ...p, [group]: cur.includes(value) ? cur.filter(v => v !== value) : [...cur, value] };
  });

  const hasActive = !!(filters.companies.length || filters.jobTypes.length || filters.locations.length || filters.categories.length || filters.showNewOnly || filters.keyword.length);

  const groups = [
    { label: "公司", key: "companies" as const, options: companies, selected: filters.companies },
    { label: "地点", key: "locations" as const, options: locations, selected: filters.locations },
    { label: "岗位类型", key: "categories" as const, options: categories, selected: filters.categories },
    { label: "招聘类型", key: "jobTypes" as const, options: jobTypes, selected: filters.jobTypes },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      <Header totalJobs={allJobs.length} newJobs={newJobCount} lastUpdate={meta.lastRun || ""} />
      <main className="flex-1 max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 w-full">
        <div className="mb-6"><SearchBar value={filters.keyword} onChange={v => setFilters(p => ({ ...p, keyword: v }))} /></div>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <aside className="lg:col-span-1">
            <FilterPanel filters={filters} onToggleFilter={toggle} onToggleNewOnly={() => setFilters(p => ({ ...p, showNewOnly: !p.showNewOnly }))}
              onClearAll={() => setFilters(DEFAULT_FILTERS)} filterGroups={groups} hasActiveFilters={hasActive} />
          </aside>
          <section className="lg:col-span-3">
            <div className="mb-4"><StatsBar totalResults={displayJobs.length} filters={filters} /></div>
            {loading ? <div className="text-center py-16 text-gray-400"><div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" /><p>加载中...</p></div>
              : <JobList jobs={displayJobs} />}
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
