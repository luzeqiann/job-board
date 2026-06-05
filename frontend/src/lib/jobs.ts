import { Job } from "@/types";

export const getUniqueCompanies = (jobs: Job[]) =>
  Array.from(new Set(jobs.map(j => j.company))).sort();

export const getUniqueLocations = (jobs: Job[]) =>
  Array.from(new Set(jobs.map(j => j.locationCity).filter(Boolean))).sort();

export const getUniqueCategories = (jobs: Job[]) =>
  Array.from(new Set(jobs.map(j => j.category).filter(Boolean))).sort();

export const getUniqueJobTypes = (jobs: Job[]) =>
  Array.from(new Set(jobs.map(j => j.jobType).filter(Boolean))).sort();

export const getNewJobCount = (jobs: Job[]) =>
  jobs.filter(j => j.isNew).length;
