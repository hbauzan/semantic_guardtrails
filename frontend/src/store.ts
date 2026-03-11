import { create } from 'zustand';

interface SemanticState {
    uiScaleFactor: number;
    xStretch: number;
    amplitude: number;
    boostFactor: number;
    colors: {
        wordA: string;
        wordB: string;
        wordC: string;
        result: string;
    };
    results: Array<{ word: string; score: number; token_id: number }>;
    hoveredDimensionIndex: number | null;
    selectedValues: number[];

    setUiScaleFactor: (scale: number) => void;
    setXStretch: (stretch: number) => void;
    setAmplitude: (amp: number) => void;
    setBoostFactor: (factor: number) => void;
    setColorA: (color: string) => void;
    setColorB: (color: string) => void;
    setColorC: (color: string) => void;
    setResultColor: (color: string) => void;
    setResults: (results: Array<{ word: string; score: number; token_id: number }>) => void;
    setHoveredDimensionIndex: (idx: number | null) => void;
    setSelectedValues: (vals: number[]) => void;
}

export const useSemanticStore = create<SemanticState>((set) => ({
    uiScaleFactor: 1.0,
    xStretch: 1.0,
    amplitude: 25.0,
    boostFactor: 10.0,
    colors: {
        wordA: '#00ffff',
        wordB: '#ff00ff',
        wordC: '#00ff00',
        result: '#ffff00',
    },
    results: [],
    hoveredDimensionIndex: null,
    selectedValues: [],

    setUiScaleFactor: (scale) => set({ uiScaleFactor: scale }),
    setXStretch: (stretch) => set({ xStretch: stretch }),
    setAmplitude: (amp) => set({ amplitude: amp }),
    setBoostFactor: (factor) => set({ boostFactor: factor }),
    setColorA: (color) => set((state) => ({ colors: { ...state.colors, wordA: color } })),
    setColorB: (color) => set((state) => ({ colors: { ...state.colors, wordB: color } })),
    setColorC: (color) => set((state) => ({ colors: { ...state.colors, wordC: color } })),
    setResultColor: (color) => set((state) => ({ colors: { ...state.colors, result: color } })),
    setResults: (results) => set({ results }),
    setHoveredDimensionIndex: (idx) => set({ hoveredDimensionIndex: idx }),
    setSelectedValues: (vals) => set({ selectedValues: vals }),
}));
