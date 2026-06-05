export interface Job {
  id: string;
  company: string;
  title: string;
  location: string;
  locationCity: string;
  jobType: "校招" | "社招";
  category: string;
  postDate: string;
  collectDate: string;
  isNew: boolean;
  url: string;
  description: string;
  requirements: string;
  salary: string;
  source: string;
  sourceUrl: string;
  tags: string[];
}

export interface FilterState {
  companies: string[];
  jobTypes: string[];
  locations: string[];
  categories: string[];
  keyword: string;
  showNewOnly: boolean;
}

export const DEFAULT_FILTERS: FilterState = {
  companies: [], jobTypes: [], locations: [], categories: [],
  keyword: "", showNewOnly: false,
};
