import { create } from 'zustand';

interface SemanticState {
    uiScaleFactor: number;
    xStretch: number;
    amplitude: number;
    boostFactor: number;
    colors: {
        baselineColor: string;
    };
    results: Array<{ word: string; score: number; token_id: number }>;
    hoveredDimensionIndex: number | null;
    selectedValues: number[];
    hoveredNode: any | null;
    selectedThread: any | null;
    stressTestQuery: string;
    firewallThreshold: number;
    isTyping: boolean;
    isChatVisible: boolean;
    chatHistory: Array<{ role: string; content: string }>;
    chatImpactNode: any | null;
    firewallEnabled: boolean;
    uploadStatus: number;
    isProcessing: boolean;
    currentTaskId: string | null;
    ramUsageMb: number;
    totalChunks: number;
    processedChunks: number;
    ingestStartTime: number | null;

    setUiScaleFactor: (scale: number) => void;
    setXStretch: (stretch: number) => void;
    setAmplitude: (amp: number) => void;
    setBoostFactor: (factor: number) => void;
    setBaselineColor: (color: string) => void;
    setResults: (results: Array<{ word: string; score: number; token_id: number }>) => void;
    setHoveredDimensionIndex: (idx: number | null) => void;
    setSelectedValues: (vals: number[]) => void;
    setHoveredNode: (node: any | null) => void;
    setSelectedThread: (thread: any | null) => void;
    setStressTestQuery: (query: string) => void;
    setFirewallThreshold: (threshold: number) => void;
    setIsTyping: (typing: boolean) => void;
    setIsChatVisible: (visible: boolean) => void;
    setChatHistory: (history: Array<{ role: string; content: string }>) => void;
    setChatImpactNode: (node: any | null) => void;
    setFirewallEnabled: (enabled: boolean) => void;
    setUploadStatus: (status: number) => void;
    setIsProcessing: (processing: boolean) => void;
    setCurrentTaskId: (id: string | null) => void;
    setRamUsageMb: (mb: number) => void;
    setTotalChunks: (chunks: number) => void;
    setProcessedChunks: (chunks: number) => void;
    setIngestStartTime: (time: number | null) => void;
}

export const useSemanticStore = create<SemanticState>((set) => ({
    uiScaleFactor: 1.0,
    xStretch: 1.0,
    amplitude: 25.0,
    boostFactor: 10.0,
    colors: {
        baselineColor: '#00ffff',
    },
    results: [],
    hoveredDimensionIndex: null,
    selectedValues: [],
    hoveredNode: null,
    selectedThread: null,
    stressTestQuery: '',
    firewallThreshold: 25.0,
    isTyping: false,
    isChatVisible: false,
    chatHistory: [],
    chatImpactNode: null,
    firewallEnabled: false,
    uploadStatus: 0,
    isProcessing: false,
    currentTaskId: null,
    ramUsageMb: 0,
    totalChunks: 0,
    processedChunks: 0,
    ingestStartTime: null,

    setUiScaleFactor: (scale) => set({ uiScaleFactor: scale }),
    setXStretch: (stretch) => set({ xStretch: stretch }),
    setAmplitude: (amp) => set({ amplitude: amp }),
    setBoostFactor: (factor) => set({ boostFactor: factor }),
    setBaselineColor: (color) => set((state) => ({ colors: { ...state.colors, baselineColor: color } })),
    setResults: (results) => set({ results }),
    setHoveredDimensionIndex: (idx) => set({ hoveredDimensionIndex: idx }),
    setSelectedValues: (vals) => set({ selectedValues: vals }),
    setHoveredNode: (node) => set({ hoveredNode: node }),
    setSelectedThread: (thread) => set({ selectedThread: thread }),
    setStressTestQuery: (query) => set({ stressTestQuery: query }),
    setFirewallThreshold: (val) => set({ firewallThreshold: val }),
    setIsTyping: (typing) => set({ isTyping: typing }),
    setIsChatVisible: (visible) => set({ isChatVisible: visible }),
    setChatHistory: (history) => set({ chatHistory: history }),
    setChatImpactNode: (node) => set({ chatImpactNode: node }),
    setFirewallEnabled: (enabled) => set({ firewallEnabled: enabled }),
    setUploadStatus: (status) => set({ uploadStatus: status }),
    setIsProcessing: (processing) => set({ isProcessing: processing }),
    setCurrentTaskId: (id) => set({ currentTaskId: id }),
    setRamUsageMb: (mb) => set({ ramUsageMb: mb }),
    setTotalChunks: (chunks: number) => set({ totalChunks: chunks }),
    setProcessedChunks: (chunks: number) => set({ processedChunks: chunks }),
    setIngestStartTime: (time: number | null) => set({ ingestStartTime: time }),
}));
