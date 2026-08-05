import { create } from "zustand";
import { persist } from "zustand/middleware";

type ProgressState = {
  completedTiers: number[];
  completedAgents: string[];
  quizBestScore: number;
  quizAttempts: number;
  masteredCards: string[];
  graduateName: string;
  graduatedAt: string | null;
  completeTier: (id: number) => void;
  completeAgent: (id: string) => void;
  recordQuiz: (score: number) => void;
  markMastered: (id: string) => void;
  unmarkMastered: (id: string) => void;
  setGraduateName: (name: string) => void;
  claimGraduate: () => void;
  reset: () => void;
};

export const useProgress = create<ProgressState>()(
  persist(
    (set) => ({
      completedTiers: [],
      completedAgents: [],
      quizBestScore: 0,
      quizAttempts: 0,
      masteredCards: [],
      graduateName: "",
      graduatedAt: null,
      completeTier: (id) =>
        set((s) => ({
          completedTiers: s.completedTiers.includes(id)
            ? s.completedTiers
            : [...s.completedTiers, id],
        })),
      completeAgent: (id) =>
        set((s) => ({
          completedAgents: s.completedAgents.includes(id)
            ? s.completedAgents
            : [...s.completedAgents, id],
        })),
      recordQuiz: (score) =>
        set((s) => ({
          quizBestScore: Math.max(s.quizBestScore, score),
          quizAttempts: s.quizAttempts + 1,
        })),
      markMastered: (id) =>
        set((s) => ({
          masteredCards: s.masteredCards.includes(id)
            ? s.masteredCards
            : [...s.masteredCards, id],
        })),
      unmarkMastered: (id) =>
        set((s) => ({
          masteredCards: s.masteredCards.filter((x) => x !== id),
        })),
      setGraduateName: (name) => set({ graduateName: name }),
      claimGraduate: () =>
        set({ graduatedAt: new Date().toISOString() }),
      reset: () =>
        set({
          completedTiers: [],
          completedAgents: [],
          quizBestScore: 0,
          quizAttempts: 0,
          masteredCards: [],
          graduateName: "",
          graduatedAt: null,
        }),
    }),
    { name: "studio-academy-progress" },
  ),
);
