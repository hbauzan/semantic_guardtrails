import React, { useState, useRef, useEffect } from 'react';
import { useSemanticStore } from '../store';

export const ChatHUD: React.FC = () => {
    const isChatVisible = useSemanticStore(state => state.isChatVisible);
    const setIsChatVisible = useSemanticStore(state => state.setIsChatVisible);
    const chatHistory = useSemanticStore(state => state.chatHistory);
    const setChatHistory = useSemanticStore(state => state.setChatHistory);
    const setIsTyping = useSemanticStore(state => state.setIsTyping);
    const setChatImpactNode = useSemanticStore(state => state.setChatImpactNode);
    const setFirewallEnabled = useSemanticStore(state => state.setFirewallEnabled);
    const firewallEnabled = useSemanticStore(state => state.firewallEnabled);

    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const endOfMessagesRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory]);

    if (!isChatVisible) {
        return (
            <button
                onClick={() => setIsChatVisible(true)}
                style={{
                    position: 'absolute', top: '20px', left: '20px', zIndex: 60,
                    background: 'rgba(0, 20, 20, 0.8)', color: '#00ffff', border: '1px solid #00ffff',
                    padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontFamily: 'monospace',
                    boxShadow: '0 0 10px rgba(0, 255, 255, 0.3)'
                }}
            >
                OPEN CHAT
            </button>
        );
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        setIsLoading(true);

        const newHistory = [...chatHistory, { role: 'user', content: userMessage }];
        setChatHistory(newHistory);

        try {
            const response = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: userMessage, model: 'llama3.1', top_k: 3 })
            });

            if (!response.body) throw new Error('No response body');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessage = '';

            const updateAssistantMessage = (chunk: string) => {
                assistantMessage += chunk;
                setChatHistory([...newHistory, { role: 'assistant', content: assistantMessage }]);
            };

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const text = decoder.decode(value, { stream: true });
                const lines = text.split('\n');

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        if (data.type === 'metadata') {
                            setFirewallEnabled(data.firewall_enabled);
                            if (data.vector && data.vector.length > 0) {
                                setChatImpactNode({
                                    word: userMessage,
                                    vector: data.vector,
                                    color: data.is_blocked ? '#ff0000' : '#00ff00',
                                    is_blocked: data.is_blocked
                                });
                            }
                        } else if (data.type === 'content') {
                            updateAssistantMessage(data.text);
                        }
                    } catch (e) {
                        console.error("Error parsing NDJSON line:", e);
                    }
                }
            }
        } catch (error) {
            console.error(error);
            setChatHistory([...newHistory, { role: 'assistant', content: 'Connection Error.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{
            position: 'absolute', top: '0', left: '0', bottom: '0', width: '350px',
            background: 'rgba(5, 10, 15, 0.95)', borderRight: '1px solid #00ffff',
            zIndex: 60, display: 'flex', flexDirection: 'column', fontFamily: 'monospace',
            boxShadow: '5px 0 15px rgba(0, 255, 255, 0.1)'
        }}>
            <div style={{ padding: '15px', borderBottom: '1px solid #00ffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#00ffff', fontWeight: 'bold' }}>SSA L2 CHAT LINK</span>
                <button onClick={() => setIsChatVisible(false)} style={{ background: 'transparent', border: 'none', color: '#00ffff', cursor: 'pointer' }}>X</button>
            </div>

            <div style={{ padding: '10px', display: 'flex', gap: '10px', borderBottom: '1px solid #333' }}>
                <span style={{ color: firewallEnabled ? '#00ff00' : '#888', fontSize: '0.8rem' }}>FW: {firewallEnabled ? 'ON' : 'OFF'}</span>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '15px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {chatHistory.map((msg, idx) => (
                    <div key={idx} style={{ textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                        <span style={{
                            display: 'inline-block', padding: '8px 12px', borderRadius: '4px',
                            background: msg.role === 'user' ? 'rgba(0, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                            color: msg.role === 'user' ? '#00ffff' : '#fff',
                            border: msg.role === 'assistant' ? '1px solid #333' : '1px solid #00ffff',
                            maxWidth: '90%', wordBreak: 'break-word', whiteSpace: 'pre-wrap', fontSize: '0.9rem'
                        }}>
                            {msg.content}
                        </span>
                    </div>
                ))}
                {isLoading && <div style={{ color: '#aaa', fontSize: '0.8rem' }}>Transmitting...</div>}
                <div ref={endOfMessagesRef} />
            </div>

            <form onSubmit={handleSubmit} style={{ padding: '15px', borderTop: '1px solid #00ffff', display: 'flex', gap: '10px' }}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onFocus={() => setIsTyping(true)}
                    onBlur={() => setIsTyping(false)}
                    placeholder="[FW=ON] Enter query..."
                    style={{ flex: 1, background: '#000', color: '#fff', border: '1px solid #00ffff', padding: '10px', fontFamily: 'monospace' }}
                />
                <button type="submit" disabled={isLoading} style={{ background: '#00ffff', color: '#000', border: 'none', padding: '10px 15px', fontWeight: 'bold', cursor: isLoading ? 'not-allowed' : 'pointer' }}>
                    SEND
                </button>
            </form>
        </div>
    );
};
