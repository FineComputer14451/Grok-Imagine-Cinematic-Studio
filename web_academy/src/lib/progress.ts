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
  deliveryChecked: string[];
  erosforgeLessons: string[];
  erosforgeQuizBest: number;
  deliveryPackLessons: string[];
  deliveryPackQuizBest: number;
  continuityLessons: string[];
  continuityQuizBest: number;
  completeTier: (id: number) => void;
  completeAgent: (id: string) => void;
  recordQuiz: (score: number) => void;
  markMastered: (id: string) => void;
  unmarkMastered: (id: string) => void;
  setGraduateName: (name: string) => void;
  claimGraduate: () => void;
  toggleDelivery: (id: string) => void;
  setDeliverySection: (ids: string[], checked: boolean) => void;
  clearDelivery: () => void;
  completeErosforgeLesson: (id: string) => void;
  recordErosforgeQuiz: (score: number) => void;
  completeDeliveryPackLesson: (id: string) => void;
  recordDeliveryPackQuiz: (score: number) => void;
  completeContinuityLesson: (id: string) => void;
  recordContinuityQuiz: (score: number) => void;
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
      deliveryChecked: [],
      erosforgeLessons: [],
      erosforgeQuizBest: 0,
      deliveryPackLessons: [],
      deliveryPackQuizBest: 0,
      continuityLessons: [],
      continuityQuizBest: 0,
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
      toggleDelivery: (id) =>
        set((s) => ({
          deliveryChecked: s.deliveryChecked.includes(id)
            ? s.deliveryChecked.filter((x) => x !== id)
            : [...s.deliveryChecked, id],
        })),
      setDeliverySection: (ids, checked) =>
        set((s) => {
          if (checked) {
            const setIds = new Set([...s.deliveryChecked, ...ids]);
            return { deliveryChecked: [...setIds] };
          }
          return {
            deliveryChecked: s.deliveryChecked.filter((x) => !ids.includes(x)),
          };
        }),
      clearDelivery: () => set({ deliveryChecked: [] }),
      completeErosforgeLesson: (id) =>
        set((s) => ({
          erosforgeLessons: s.erosforgeLessons.includes(id)
            ? s.erosforgeLessons
            : [...s.erosforgeLessons, id],
        })),
      recordErosforgeQuiz: (score) =>
        set((s) => ({
          erosforgeQuizBest: Math.max(s.erosforgeQuizBest, score),
        })),
      completeDeliveryPackLesson: (id) =>
        set((s) => ({
          deliveryPackLessons: s.deliveryPackLessons.includes(id)
            ? s.deliveryPackLessons
            : [...s.deliveryPackLessons, id],
        })),
      recordDeliveryPackQuiz: (score) =>
        set((s) => ({
          deliveryPackQuizBest: Math.max(s.deliveryPackQuizBest, score),
        })),
      completeContinuityLesson: (id) =>
        set((s) => ({
          continuityLessons: s.continuityLessons.includes(id)
            ? s.continuityLessons
            : [...s.continuityLessons, id],
        })),
      recordContinuityQuiz: (score) =>
        set((s) => ({
          continuityQuizBest: Math.max(s.continuityQuizBest, score),
        })),
      reset: () =>
        set({
          completedTiers: [],
          completedAgents: [],
          quizBestScore: 0,
          quizAttempts: 0,
          masteredCards: [],
          graduateName: "",
          graduatedAt: null,
          deliveryChecked: [],
          erosforgeLessons: [],
          erosforgeQuizBest: 0,
          deliveryPackLessons: [],
          deliveryPackQuizBest: 0,
          continuityLessons: [],
          continuityQuizBest: 0,
        }),
    }),
    { name: "studio-academy-progress" },
  ),
);
