import React, { useState, useRef, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Sphere, Text, Line, PointerLockControls } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useKeyboardControls } from '../hooks/useKeyboardControls';

const FlightControls: React.FC = () => {
    const controlsRef = useRef<any>(null);
    const keys = useKeyboardControls();

    // Physics Constants
    const DRAG = 0.92;
    const BASE_ACCEL = 2.0;
    const MAX_THRUST = 10.0;
    const THRUST_BUILDUP = 1.5;

    // Physics State
    const velocity = useRef(new THREE.Vector3());
    const thrustAccumulator = useRef(0.0);

    // Force Lock on Click (Global Listener)
    useEffect(() => {
        const handleLock = (e: MouseEvent) => {
            if ((e.target as HTMLElement).tagName === 'INPUT') return;
            if (controlsRef.current) {
                controlsRef.current.lock();
            }
        };
        document.addEventListener('click', handleLock);
        return () => document.removeEventListener('click', handleLock);
    },[]);

    useFrame((state, delta) => {
        // 1. Inertia (Damping)
        velocity.current.multiplyScalar(DRAG);

        // 2. Accumulative Thrust (Exponential)
        const isBoosting = keys.current.has('ShiftLeft') || keys.current.has('ShiftRight');
        if (isBoosting) {
            thrustAccumulator.current = Math.min(thrustAccumulator.current + (delta * THRUST_BUILDUP), 1.0);
        } else {
            thrustAccumulator.current = Math.max(thrustAccumulator.current - (delta * THRUST_BUILDUP * 2.0), 0.0);
        }
        const currentBoost = 1.0 + (MAX_THRUST * Math.pow(thrustAccumulator.current, 2));

        // 3. Calculate Input Direction
        const inputVector = new THREE.Vector3();
        if (keys.current.has('KeyW')) inputVector.z -= 1;
        if (keys.current.has('KeyS')) inputVector.z += 1;
        if (keys.current.has('KeyA')) inputVector.x -= 1;
        if (keys.current.has('KeyD')) inputVector.x += 1;
        if (keys.current.has('KeyQ')) inputVector.y -= 1;
        if (keys.current.has('KeyE')) inputVector.y += 1;

        if (inputVector.lengthSq() > 0) {
            inputVector.normalize();
        }

        // 4. Apply Acceleration relative to Camera Orientation
        inputVector.applyEuler(state.camera.rotation);
        const effectiveAccel = BASE_ACCEL * currentBoost;
        velocity.current.addScaledVector(inputVector, effectiveAccel * delta);

        // 5. Apply Velocity to Camera
        state.camera.position.add(velocity.current);
    });

    return <PointerLockControls ref={controlsRef} makeDefault />;
};

type NodeData = {
  word: string;
  position: [number, number, number];
  color: string;
};

const ArithmeticHUD: React.FC = () => {
  const [wordA, setWordA] = useState('rey');
  const [wordB, setWordB] = useState('hombre');
  const [wordC, setWordC] = useState('mujer');
  const [nodes, setNodes] = useState<NodeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const extractCoords = (data: any): [number, number, number] => {
    if (data.xyz && data.xyz.length >= 3) return [data.xyz[0], data.xyz[1], data.xyz[2]];
    if (data.point && data.point.length >= 3) return [data.point[0], data.point[1], data.point[2]];
    if (data.vector && data.vector.length >= 3) return [data.vector[0], data.vector[1], data.vector[2]];
    if (data.embedding && data.embedding.length >= 3) return [data.embedding[0], data.embedding[1], data.embedding[2]];
    if (Array.isArray(data) && data.length >= 3) return [data[0], data[1], data[2]];
    return [Math.random() * 5, Math.random() * 5, Math.random() * 5]; // Fallback
  };

  const calculate = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Get arithmetic result
      const arithRes = await fetch('http://127.0.0.1:8000/arithmetic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word_a: wordA, word_b: wordB, word_c: wordC, top_k: 1 })
      });
      
      if (!arithRes.ok) throw new Error('Error en /arithmetic');
      const arithData = await arithRes.json();
      
      let resultWord = 'Resultado';
      if (Array.isArray(arithData) && arithData.length > 0) resultWord = arithData[0].word || arithData[0].text;
      else if (arithData.results && arithData.results.length > 0) resultWord = arithData.results[0].word || arithData.results[0].text;
      else if (arithData.word) resultWord = arithData.word;
      else if (arithData.result) resultWord = arithData.result;

      // 2. Extract coordinates for all 4 words
      const words = [wordA, wordB, wordC, resultWord];
      const newNodes: NodeData[] = [];
      const colors = ['#00ffff', '#ff00ff', '#00ff00', '#ffff00'];

      for (let i = 0; i < words.length; i++) {
        const word = words[i];
        const embedRes = await fetch('http://127.0.0.1:8000/embed', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: word })
        });
        if (!embedRes.ok) throw new Error(`Error en /embed para ${word}`);
        const embedData = await embedRes.json();
        
        newNodes.push({
          word,
          position: extractCoords(embedData),
          color: colors[i]
        });
      }

      setNodes(newNodes);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  // Trapeze line points
  const linePoints = nodes.length === 4 ? [
    nodes[0].position, // A
    nodes[1].position, // B
    nodes[2].position, // C
    nodes[3].position, // Result
    nodes[0].position  // Back to A for closed shape
  ] : [];

  return (
    <>
      {/* Absolute HUD */}
      <div style={{
        position: 'absolute',
        top: '20px',
        left: '20px',
        zIndex: 10,
        background: 'rgba(0, 20, 20, 0.8)',
        border: '1px solid #00ffff',
        padding: '20px',
        borderRadius: '8px',
        display: 'flex',
        flexDirection: 'column',
        gap: '15px',
        boxShadow: '0 0 15px rgba(0, 255, 255, 0.2)',
        color: '#00ffff',
        fontFamily: 'monospace',
        minWidth: '250px'
      }}>
        <h2 style={{ margin: 0, fontSize: '1.2rem', textTransform: 'uppercase', letterSpacing: '2px', textAlign: 'center' }}>
          Vector Math
        </h2>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          <label style={{ fontSize: '0.8rem', color: '#00ccff' }}>Palabra A (+)</label>
          <input 
            value={wordA} 
            onChange={(e) => setWordA(e.target.value)}
            style={{ padding: '8px', background: '#000', border: '1px solid #005555', color: '#fff', borderRadius: '4px' }}
          />
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          <label style={{ fontSize: '0.8rem', color: '#ff00ff' }}>Palabra B (-)</label>
          <input 
            value={wordB} 
            onChange={(e) => setWordB(e.target.value)}
            style={{ padding: '8px', background: '#000', border: '1px solid #550055', color: '#fff', borderRadius: '4px' }}
          />
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          <label style={{ fontSize: '0.8rem', color: '#00ff00' }}>Palabra C (+)</label>
          <input 
            value={wordC} 
            onChange={(e) => setWordC(e.target.value)}
            style={{ padding: '8px', background: '#000', border: '1px solid #005500', color: '#fff', borderRadius: '4px' }}
          />
        </div>

        <button 
          onClick={calculate}
          disabled={loading}
          style={{
            padding: '10px',
            background: loading ? '#333' : '#003333',
            color: loading ? '#888' : '#00ffff',
            border: '1px solid #00ffff',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
            marginTop: '10px',
            textTransform: 'uppercase',
            transition: 'all 0.3s'
          }}
        >
          {loading ? 'Calculando...' : 'Calcular'}
        </button>
        
        {error && <div style={{ color: '#ff3333', fontSize: '0.8rem', marginTop: '5px' }}>{error}</div>}
      </div>

      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 0, 15], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <FlightControls />
        
        {/* Render nodes and text */}
        {nodes.map((node, i) => (
          <group key={i} position={node.position}>
            <Sphere args={[0.3, 16, 16]}>
              <meshStandardMaterial color={node.color} emissive={node.color} emissiveIntensity={0.5} />
            </Sphere>
            <Text
              position={[0, 0.6, 0]}
              fontSize={0.5}
              color={node.color}
              anchorX="center"
              anchorY="middle"
              outlineWidth={0.05}
              outlineColor="#000000"
            >
              {node.word}
            </Text>
          </group>
        ))}

        {/* Semantic Trapeze */}
        {nodes.length === 4 && (
          <Line
            points={linePoints}
            color="#ffffff"
            lineWidth={2}
            dashed={false}
          />
        )}
        
        {/* Grid helper for scale reference */}
        <gridHelper args={[20, 20, '#222222', '#111111']} position={[0, -5, 0]} />
      </Canvas>
    </>
  );
};

export default ArithmeticHUD;
