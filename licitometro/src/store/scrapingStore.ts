import create from 'zustand';
import { persist } from 'zustand/middleware';
import { ScrapingResult } from '../types/recon';

interface ScrapingState {
  results: Record<string, ScrapingResult>;
  addResult: (jobId: string, result: ScrapingResult) => void;
  getResult: (jobId: string) => ScrapingResult | undefined;
  clearResult: (jobId: string) => void;
  clearAllResults: () => void;
}

export const useScrapingStore = create<ScrapingState>()(
  persist(
    (set, get) => ({
      results: {},
      addResult: (jobId, result) =>
        set((state) => ({
          results: {
            ...state.results,
            [jobId]: result,
          },
        })),
      getResult: (jobId) => get().results[jobId],
      clearResult: (jobId) =>
        set((state) => {
          const { [jobId]: _, ...rest } = state.results;
          return { results: rest };
        }),
      clearAllResults: () => set({ results: {} }),
    }),
    {
      name: 'scraping-store',
    }
  )
);
