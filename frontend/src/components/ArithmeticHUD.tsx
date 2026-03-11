import React, { useState, useRef, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Sphere, Text, PointerLockControls, Billboard } from '@react-three/drei';
import * as THREE from 'three';
import { useKeyboardControls } from '../hooks/useKeyboardControls';
import { SemanticThread } from './SemanticThread';
import { useSemanticStore } from '../store';

const FlightControls: React.FC = () => {
  const controlsRef = useRef<any>(null);
  const keys = useKeyboardControls();

  // Physics Constants
  const DRAG = 0.92;
  const BASE_ACCEL = 2.0;

  const boostFactor = useSemanticStore(state => state.boostFactor);

  // Physics State
  const velocity = useRef(new THREE.Vector3());

  // Focus Management on Click
  useEffect(() => {
    const handleFocus = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      // Only blur if clicking directly on the canvas (Drei handles PointerLock internally)
      if (target.tagName === 'CANVAS') {
        if (document.activeElement && document.activeElement instanceof HTMLElement) {
          document.activeElement.blur();
        }
      }
    };
    // Use mousedown to blur the active element before the click event triggers the lock
    document.addEventListener('mousedown', handleFocus);
    return () => document.removeEventListener('mousedown', handleFocus);
  }, []);

  useFrame((state, delta) => {
    // 1. Inertia (Damping)
    velocity.current.multiplyScalar(DRAG);

    // 2. Instantaneous Boost
    const isBoosting = keys.current.has('ShiftLeft') || keys.current.has('ShiftRight');
    const currentBoost = isBoosting ? boostFactor : 1.0;

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

    if (isBoosting) {
      if (inputVector.lengthSq() > 0) {
        velocity.current.copy(inputVector).multiplyScalar(effectiveAccel * delta);
      } else {
        velocity.current.set(0, 0, 0); // Decelerate instantly
      }
    } else {
      velocity.current.addScaledVector(inputVector, effectiveAccel * delta);
    }

    // 5. Apply Velocity to Camera
    state.camera.position.add(velocity.current);
  });

  return <PointerLockControls ref={controlsRef} makeDefault />;
};

type NodeData = {
  word: string;
  position: [number, number, number];
  color: string;
  vector?: number[];
  token_id?: number;
};

const TelemetryHUD: React.FC<{ nodesCount: number, xStretch: number }> = ({ nodesCount, xStretch }) => {
  const [fps, setFps] = useState(0);
  const frames = useRef(0);
  const lastTime = useRef(performance.now());

  useEffect(() => {
    let animationFrameId: number;
    const loop = () => {
      const now = performance.now();
      frames.current++;
      if (now >= lastTime.current + 1000) {
        setFps(Math.round((frames.current * 1000) / (now - lastTime.current)));
        frames.current = 0;
        lastTime.current = now;
      }
      animationFrameId = requestAnimationFrame(loop);
    };
    animationFrameId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div style={{
      position: 'absolute',
      bottom: '20px',
      left: '20px',
      zIndex: 10,
      background: 'rgba(0, 20, 20, 0.8)',
      border: '1px solid #00ff00',
      padding: '10px 15px',
      borderRadius: '4px',
      color: '#00ff00',
      fontFamily: 'monospace',
      fontSize: '0.9rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '5px',
      boxShadow: '0 0 10px rgba(0, 255, 0, 0.2)',
      pointerEvents: 'none'
    }}>
      <div>FPS: {fps}</div>
      <div>NODES: {nodesCount}</div>
      <div style={{ color: '#ff00ff' }}>SECTOR: {(1024 * xStretch).toLocaleString()} UNITS</div>
      <div>ACTIVE MODEL: BGE-M3 (1024D)</div>
      <div style={{ color: '#00ffff' }}>CURRENT X-STRETCH: {xStretch.toFixed(1)}x</div>
    </div>
  );
};

const CrosshairHUD: React.FC = () => (
  <div style={{
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    zIndex: 10,
    pointerEvents: 'none'
  }}>
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="2" fill="#00ffff" />
      <path d="M12 2V8M12 22V16M2 12H8M22 12H16" stroke="#00ffff" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  </div>
);

const TargetingHUD: React.FC = () => {
  const index = useSemanticStore(state => state.hoveredDimensionIndex);
  const values = useSemanticStore(state => state.selectedValues);
  const colors = useSemanticStore(state => state.colors);

  if (index === null) return null;

  return (
    <div style={{
      position: 'absolute',
      top: '50%',
      left: '50%',
      transform: 'translate(40px, -50%)',
      zIndex: 10,
      background: 'rgba(0, 10, 10, 0.85)',
      border: '1px solid #ffcc00',
      padding: '8px 12px',
      borderRadius: '4px',
      color: '#ffcc00',
      fontFamily: 'monospace',
      fontSize: '0.85rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '4px',
      pointerEvents: 'none',
      boxShadow: '0 0 10px rgba(255, 204, 0, 0.2)'
    }}>
      <div style={{ fontWeight: 'bold', borderBottom: '1px solid #ffcc00', paddingBottom: '2px', marginBottom: '2px' }}>
        DIM-ID: {index}
      </div>
      <div style={{ color: '#aaa', fontSize: '0.75rem', marginBottom: '2px' }}>MAGNITUDE</div>
      {values.length >= 1 && <div style={{ color: colors.wordA }}>A: {values[0].toFixed(4)}</div>}
      {values.length >= 2 && <div style={{ color: colors.wordB }}>B: {values[1].toFixed(4)}</div>}
      {values.length >= 3 && <div style={{ color: colors.wordC }}>C: {values[2].toFixed(4)}</div>}
      {values.length >= 4 && <div style={{ color: colors.result }}>RES: {values[3].toFixed(4)}</div>}
    </div>
  );
};

// XZ Plane Raycaster Probe
const ProbeSystem: React.FC<{ nodes: NodeData[], xStretch: number, uiScaleFactor: number }> = ({ nodes, xStretch, uiScaleFactor }) => {
  const { camera } = useThree();
  const setHoveredDimensionIndex = useSemanticStore(state => state.setHoveredDimensionIndex);
  const setSelectedValues = useSemanticStore(state => state.setSelectedValues);

  useFrame(() => {
    if (nodes.length < 4) {
      setHoveredDimensionIndex(null);
      return;
    }

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);

    // Raycast towards Y=0 plane (the Semantic Disk floor)
    if (Math.abs(raycaster.ray.direction.y) > 0.0001) {
      const t = (0 - raycaster.ray.origin.y) / raycaster.ray.direction.y;
      if (t > 0) {
        const hitPoint = raycaster.ray.origin.clone().add(raycaster.ray.direction.clone().multiplyScalar(t));

        let closestNodeIdx = -1;
        let minZDist = Infinity;
        let closestPosX = 0;

        for (let i = 0; i < nodes.length; i++) {
          const n = nodes[i];
          let posZ = 0;
          let posX = 0;

          if (i > 0 && n.vector && n.vector.length >= 3 && nodes[0]?.vector) {
            const vA = nodes[0].vector;
            const magA = Math.sqrt(vA.reduce((sum, val) => sum + val * val, 0));
            const magN = Math.sqrt(n.vector.reduce((sum, val) => sum + val * val, 0));
            let dn = 1;
            if (magA > 0 && magN > 0) {
              const dot = vA.reduce((sum, val, idx) => sum + val * (n.vector![idx] || 0), 0);
              dn = 1 - (dot / (magA * magN));
            }
            const angle = Math.atan2(n.vector[2], n.vector[0]);
            posX = Math.cos(angle) * dn * uiScaleFactor * 50.0;
            posZ = Math.sin(angle) * dn * uiScaleFactor * 50.0;
          }

          const distZ = Math.abs(hitPoint.z - posZ);
          if (distZ < minZDist) {
            minZDist = distZ;
            closestNodeIdx = i;
            closestPosX = posX;
          }
        }

        if (closestNodeIdx !== -1 && minZDist < 10.0) {
          let targetedIndex = Math.round(((hitPoint.x - closestPosX) / xStretch) + 512);

          if (targetedIndex >= 0 && targetedIndex < 1024) {
            setHoveredDimensionIndex(targetedIndex);
            const values = nodes.map(n => (n.vector && n.vector.length > targetedIndex) ? n.vector[targetedIndex] : 0);
            setSelectedValues(values);
            return;
          }
        }
      }
    }

    setHoveredDimensionIndex(null);
  });

  return null;
};


const ArithmeticHUD: React.FC = () => {
  // Suppress THREE.Clock deprecation warning caused by React Three Fiber internals
  useEffect(() => {
    const origWarn = console.warn;
    console.warn = (...args) => {
      if (typeof args[0] === 'string' && args[0].includes('THREE.Clock: This module has been deprecated')) return;
      origWarn(...args);
    };
    return () => {
      console.warn = origWarn;
    };
  }, []);

  const [wordA, setWordA] = useState('rey');
  const [wordB, setWordB] = useState('hombre');
  const [wordC, setWordC] = useState('mujer');

  const uiScaleFactor = useSemanticStore((state) => state.uiScaleFactor);
  const setUiScaleFactor = useSemanticStore((state) => state.setUiScaleFactor);
  const xStretch = useSemanticStore((state) => state.xStretch);
  const setXStretch = useSemanticStore((state) => state.setXStretch);
  const amplitude = useSemanticStore((state) => state.amplitude);
  const setAmplitude = useSemanticStore((state) => state.setAmplitude);
  const boostFactor = useSemanticStore((state) => state.boostFactor);
  const setBoostFactor = useSemanticStore((state) => state.setBoostFactor);

  const colors = useSemanticStore((state) => state.colors);
  const setColorA = useSemanticStore((state) => state.setColorA);
  const setColorB = useSemanticStore((state) => state.setColorB);
  const setColorC = useSemanticStore((state) => state.setColorC);
  const setResultColor = useSemanticStore((state) => state.setResultColor);

  const topResults = useSemanticStore((state) => state.results);
  const setResults = useSemanticStore((state) => state.setResults);

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
    setResults([]);
    try {
      // 1. Get arithmetic result
      const arithRes = await fetch('http://127.0.0.1:8000/arithmetic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word_a: wordA, word_b: wordB, word_c: wordC, top_k: 3 })
      });

      if (!arithRes.ok) throw new Error('Error en /arithmetic');
      const arithData = await arithRes.json();

      let resultWord = 'Resultado';
      if (Array.isArray(arithData) && arithData.length > 0) {
        resultWord = arithData[0].word || arithData[0].text;
        setResults(arithData.map((res: any) => ({
          ...res,
          token_id: Number(res.token_id || res.id || 0)
        })));
      }
      else if (arithData.results && arithData.results.length > 0) {
        resultWord = arithData.results[0].word || arithData.results[0].text;
        setResults(arithData.results.map((res: any) => ({
          ...res,
          token_id: Number(res.token_id || res.id || 0)
        })));
      }

      // 2. Extract coordinates and raw 1024D vectors
      const words = [wordA, wordB, wordC, resultWord];
      const newNodes: NodeData[] = [];
      const nodeColors = [colors.wordA, colors.wordB, colors.wordC, colors.result];

      for (let i = 0; i < words.length; i++) {
        const word = words[i];
        const tokenizeRes = await fetch('http://127.0.0.1:8000/tokenize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: word, include_raw_vector: true })
        });
        if (!tokenizeRes.ok) throw new Error(`Error en /tokenize para ${word}`);
        const tokenizeData = await tokenizeRes.json();

        let position: [number, number, number] = [0, 0, 0];
        let vector: number[] = [];

        if (tokenizeData.tokens && tokenizeData.tokens.length > 0) {
          const mainToken = tokenizeData.tokens[0];
          position = extractCoords(mainToken);
          if (mainToken.vector) {
            vector = mainToken.vector;
          }
        }

        // If vector array wasn't attached for some reason, use the result_vector from arithmetic if it's the result
        if (vector.length === 0 && i === 3 && arithData.vector) {
          vector = arithData.vector;
        }

        newNodes.push({
          word,
          position,
          color: nodeColors[i],
          vector,
          token_id: Math.random() // Unique ID as fallback, ideally token_id from backend
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

  // Helper for vector math
  const getVectorMagnitude = (vec: number[]) => {
    return Math.sqrt(vec.reduce((sum, val) => sum + val * val, 0));
  };

  return (
    <>
      <TelemetryHUD nodesCount={nodes.length > 0 ? nodes.length * 1024 : 0} xStretch={xStretch} />
      <CrosshairHUD />
      <TargetingHUD />

      {/* Absolute HUD */}
      <div
        onPointerDown={(e) => e.stopPropagation()}
        style={{
          pointerEvents: 'auto',
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
          <label style={{ fontSize: '0.8rem', color: colors.wordA }}>Palabra A (+)</label>
          <div style={{ display: 'flex', gap: '5px' }}>
            <input
              value={wordA}
              onChange={(e) => setWordA(e.target.value)}
              style={{ flex: 1, padding: '8px', background: '#000', border: `1px solid ${colors.wordA}`, color: '#fff', borderRadius: '4px' }}
            />
            <input type="color" value={colors.wordA} onChange={(e) => setColorA(e.target.value)} style={{ width: '40px', padding: '0', border: 'none', background: 'none' }} />
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          <label style={{ fontSize: '0.8rem', color: colors.wordB }}>Palabra B (-)</label>
          <div style={{ display: 'flex', gap: '5px' }}>
            <input
              value={wordB}
              onChange={(e) => setWordB(e.target.value)}
              style={{ flex: 1, padding: '8px', background: '#000', border: `1px solid ${colors.wordB}`, color: '#fff', borderRadius: '4px' }}
            />
            <input type="color" value={colors.wordB} onChange={(e) => setColorB(e.target.value)} style={{ width: '40px', padding: '0', border: 'none', background: 'none' }} />
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          <label style={{ fontSize: '0.8rem', color: colors.wordC }}>Palabra C (+)</label>
          <div style={{ display: 'flex', gap: '5px' }}>
            <input
              value={wordC}
              onChange={(e) => setWordC(e.target.value)}
              style={{ flex: 1, padding: '8px', background: '#000', border: `1px solid ${colors.wordC}`, color: '#fff', borderRadius: '4px' }}
            />
            <input type="color" value={colors.wordC} onChange={(e) => setColorC(e.target.value)} style={{ width: '40px', padding: '0', border: 'none', background: 'none' }} />
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          <label style={{ fontSize: '0.8rem', color: colors.result }}>Resultado (=)</label>
          <div style={{ display: 'flex', gap: '5px' }}>
            <span style={{ flex: 1, padding: '8px', background: '#000', border: `1px solid ${colors.result}`, color: '#aaa', borderRadius: '4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {nodes.length === 4 ? nodes[3].word : '???'}
            </span>
            <input type="color" value={colors.result} onChange={(e) => setResultColor(e.target.value)} style={{ width: '40px', padding: '0', border: 'none', background: 'none' }} />
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', marginTop: '5px' }}>
          <label style={{ fontSize: '0.8rem', color: '#00ccff', display: 'flex', justifyContent: 'space-between' }}>
            <span>UI Scale Factor</span>
            <span>{uiScaleFactor.toFixed(1)}</span>
          </label>
          <input
            type="range"
            min="1.0"
            max="10.0"
            step="0.1"
            value={uiScaleFactor}
            onChange={(e) => setUiScaleFactor(parseFloat(e.target.value))}
            style={{ width: '100%', cursor: 'pointer' }}
          />

          <label style={{ fontSize: '0.8rem', color: '#00ccff', display: 'flex', justifyContent: 'space-between', marginTop: '5px' }}>
            <span>DNA Stretch</span>
            <span>{xStretch.toFixed(1)}</span>
          </label>
          <input
            type="range"
            min="0.1"
            max="40.0"
            step="0.1"
            value={xStretch}
            onChange={(e) => setXStretch(parseFloat(e.target.value))}
            style={{ width: '100%', cursor: 'pointer' }}
          />

          <label style={{ fontSize: '0.8rem', color: '#00ccff', display: 'flex', justifyContent: 'space-between', marginTop: '5px' }}>
            <span>Amplitude</span>
            <span>{amplitude.toFixed(0)}</span>
          </label>
          <input
            type="range"
            min="1.0"
            max="50.0"
            step="1.0"
            value={amplitude}
            onChange={(e) => setAmplitude(parseFloat(e.target.value))}
            style={{ width: '100%', cursor: 'pointer' }}
          />

          <label style={{ fontSize: '0.8rem', color: '#ff00ff', display: 'flex', justifyContent: 'space-between', marginTop: '5px' }}>
            <span>Boost Factor</span>
            <span>x{boostFactor.toFixed(0)}</span>
          </label>
          <input
            type="range"
            min="10.0"
            max="500.0"
            step="1.0"
            value={boostFactor}
            onChange={(e) => setBoostFactor(parseFloat(e.target.value))}
            style={{ width: '100%', cursor: 'pointer' }}
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

        {topResults.length > 0 && (
          <div style={{ marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '8px', borderTop: '1px solid #005555', paddingTop: '10px' }}>
            <div style={{ color: '#00ccff', fontSize: '0.9rem', marginBottom: '5px' }}>TOP 3 VECINOS</div>
            {topResults.map((res, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                <span style={{ color: '#fff' }}>{res.word}</span>
                <span style={{ color: '#00ff00' }}>{(res.score * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        )}

        {error && <div style={{ color: '#ff3333', fontSize: '0.8rem', marginTop: '5px' }}>{error}</div>}
      </div>

      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 0, 15], fov: 50, near: 1, far: 200000 }}>
        <ambientLight intensity={0.5} />
        <ProbeSystem nodes={nodes} xStretch={xStretch} uiScaleFactor={uiScaleFactor} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <FlightControls />

        {/* Render nodes and text */}
        {nodes.map((node, i) => {
          // Word A defaults to [0, 0, 0], others calculate Radial Cosine Distance.
          let pos = [0, 0, 0] as [number, number, number];
          if (i > 0 && node.vector && node.vector.length > 0) {
            const vA = nodes[0]?.vector || [];
            const magA = getVectorMagnitude(vA);
            const magN = getVectorMagnitude(node.vector);
            let dn = 1;
            if (magA > 0 && magN > 0) {
              const dot = vA.reduce((sum, val, idx) => sum + val * (node.vector![idx] || 0), 0);
              dn = 1 - (dot / (magA * magN));
            }
            if (node.vector.length >= 3) {
              // 2D Directional Mapping: XZ Layout (Semantic Disk)
              const angle = Math.atan2(node.vector[2], node.vector[0]);
              const normX = Math.cos(angle);
              const normZ = Math.sin(angle);

              const BASE_SPREAD = 50.0;
              pos = [
                normX * dn * uiScaleFactor * BASE_SPREAD,
                0, // Strictly anchored to the floor
                normZ * dn * uiScaleFactor * BASE_SPREAD
              ];
            }
          }
          return (
            <group key={i} position={pos}>
              <Sphere args={[0.3, 16, 16]}>
                <meshStandardMaterial color={node.color} emissive={node.color} emissiveIntensity={0.5} />
              </Sphere>
              <Text
                position={[0, 0, 0]}
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
          );
        })}

        {/* Semantic Ribbon Traces */}
        {nodes.map((node, i) => {
          if (!node.vector || node.vector.length === 0) return null;

          // Radial Cosine Distance Calculation for Threads
          let pos = [0, 0, 0] as [number, number, number];
          if (i > 0 && node.vector && node.vector.length > 0) {
            const vA = nodes[0]?.vector || [];
            const magA = getVectorMagnitude(vA);
            const magN = getVectorMagnitude(node.vector);
            let dn = 1;
            if (magA > 0 && magN > 0) {
              const dot = vA.reduce((sum, val, idx) => sum + val * (node.vector![idx] || 0), 0);
              dn = 1 - (dot / (magA * magN));
            }
            if (node.vector.length >= 3) {
              // 2D Directional Mapping: XZ Layout (Semantic Disk)
              const angle = Math.atan2(node.vector[2], node.vector[0]);
              const normX = Math.cos(angle);
              const normZ = Math.sin(angle);

              const BASE_SPREAD = 50.0;
              pos = [
                normX * dn * uiScaleFactor * BASE_SPREAD,
                0, // Strictly anchored to the floor
                normZ * dn * uiScaleFactor * BASE_SPREAD
              ];
            }
          }

          return (
            <group key={`ribbon-${node.token_id || i}`} position={pos}>
              <Billboard position={[-(512 * xStretch) - 20, 0, 0]}>
                <Text
                  color={node.color}
                  fontSize={12}
                  anchorX="center"
                  anchorY="middle"
                  outlineWidth={0.5}
                  outlineColor="#000000"
                  fontStyle="italic"
                >
                  {node.word} [{i === 0 ? "A" : i === 1 ? "B" : i === 2 ? "C" : "RES"}]
                </Text>
              </Billboard>
              <SemanticThread data={node.vector} xStretch={xStretch} position={[0, 0, 0]} amplitude={amplitude} baseColor={node.color} />
            </group>
          )
        })}

        {/* Grid helper for scale reference */}
        <gridHelper args={[20, 20, '#222222', '#111111']} position={[0, -5, 0]} />
      </Canvas>
    </>
  );
};

export default ArithmeticHUD;
