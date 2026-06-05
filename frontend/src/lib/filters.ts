import { Job, FilterState } from "@/types";

export function applyFilters(jobs: Job[], f: FilterState): Job[] {
  let r = [...jobs];
  if (f.companies.length) r = r.filter(j => f.companies.includes(j.company));
  if (f.jobTypes.length) r = r.filter(j => f.jobTypes.includes(j.jobType));
  if (f.locations.length) r = r.filter(j => f.locations.includes(j.locationCity));
  if (f.categories.length) r = r.filter(j => f.categories.includes(j.category));
  if (f.showNewOnly) r = r.filter(j => j.isNew);
  return r;
}

export function sortJobs(jobs: Job[]): Job[] {
  return [...jobs].sort((a, b) => {
    if (a.isNew && !b.isNew) return -1;
    if (!a.isNew && b.isNew) return 1;
    return b.postDate.localeCompare(a.postDate);
  });
}
