import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars, Text, Line } from '@react-three/drei';

const ArithmeticVisualizer = () => {
    const [words, setWords] = useState({ a: 'rey', b: 'hombre', c: 'mujer' });
    const [points, setPoints] = useState<any[]>([]); // Puntos A, B, C y Resultado

    const calculate = async () => {
        const res = await fetch('http://localhost:8000/arithmetic', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ word_a: words.a, word_b: words.b, word_c: words.c, top_k: 1 })
        });
        const data = await res.json();
        // Aquí mapearíamos los resultados a coordenadas 3D para renderizar
        console.log("Resultado:", data.results[0].word);
    };

    return (
        <div style={{ width: '100vw', height: '100vh', background: '#000' }}>
            {/* HUD Simple */}
            <div style={{ position: 'absolute', zIndex: 10, padding: '20px', display: 'flex', gap: '10px' }}>
                <input value={words.a} onChange={e => setWords({ ...words, a: e.target.value })} />
                <span>-</span>
                <input value={words.b} onChange={e => setWords({ ...words, b: e.target.value })} />
                <span>+</span>
                <input value={words.c} onChange={e => setWords({ ...words, c: e.target.value })} />
                <button onClick={calculate}>CALCULAR</button>
            </div>

            <Canvas camera={{ position: [0, 0, 150] }}>
                <OrbitControls />
                <Stars />
                <ambientLight intensity={0.5} />
                {/* Aquí irían los puntos renderizados como esferas neón */}
            </Canvas>
        </div>
    );
};

export default ArithmeticVisualizer;