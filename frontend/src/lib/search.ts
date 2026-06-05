import { Job } from "@/types";

const WEIGHTS: Record<string, number> = {
  "ai应用工程师": 100, "rpa开发": 100, "流程自动化": 100,
  "智能客服": 95, "ai训练师": 95, "提示词工程": 95,
  "大模型应用": 100, "对话机器人": 90, "自动化测试": 85,
  "低代码开发": 85, "ai产品": 80,
};

function score(keyword: string, text: string, job: Job): number {
  if (job.title.toLowerCase().includes(keyword)) return 100;
  for (const [kw, w] of Object.entries(WEIGHTS)) {
    if (keyword.includes(kw) || kw.includes(keyword)) {
      return text.includes(keyword) ? w * 10 : w;
    }
  }
  if (text.includes(keyword)) return 50;
  const words = keyword.split(/\s+/);
  const n = words.filter(w => text.includes(w)).length;
  return n > 0 ? n * 10 : 0;
}

export function searchJobs(jobs: Job[], keyword: string): Job[] {
  const kw = keyword.trim().toLowerCase();
  if (!kw) return jobs;
  return jobs
    .map(job => {
      const text = `${job.title} ${job.description} ${job.tags?.join(" ")} ${job.company}`.toLowerCase();
      return { job, s: score(kw, text, job) };
    })
    .filter(({ s }) => s > 0)
    .sort((a, b) => b.s - a.s)
    .map(({ job }) => job);
}
