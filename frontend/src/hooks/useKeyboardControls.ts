import { useEffect, useRef } from 'react';

export const useKeyboardControls = () => {
    const keys = useRef(new Set<string>());

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            const activeElem = document.activeElement;
            if (activeElem && (activeElem.tagName === 'INPUT' || activeElem.tagName === 'TEXTAREA')) return;
            keys.current.add(e.code);
        };
        const handleKeyUp = (e: KeyboardEvent) => {
            keys.current.delete(e.code);
        };
        const handleFocusIn = (e: FocusEvent) => {
            const activeElem = e.target as HTMLElement;
            if (activeElem && (activeElem.tagName === 'INPUT' || activeElem.tagName === 'TEXTAREA')) {
                keys.current.clear();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);
        window.addEventListener('focusin', handleFocusIn);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('keyup', handleKeyUp);
            window.removeEventListener('focusin', handleFocusIn);
        };
    },[]);

    return keys;
};
