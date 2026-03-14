import React, { useState, useRef, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Sphere, Text, PointerLockControls, Billboard, Ring } from '@react-three/drei';
import * as THREE from 'three';
import { useKeyboardControls } from '../hooks/useKeyboardControls';
import { SemanticThread } from './SemanticThread';
import { ChatHUD } from './ChatHUD';
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
      // Only blur if clicking directly on the canvas
      if (target.tagName === 'CANVAS') {
        if (document.activeElement && document.activeElement instanceof HTMLElement) {
          document.activeElement.blur();
        }

        const isCurrentlyTyping = useSemanticStore.getState().isTyping;
        if (isCurrentlyTyping) return;

        if (controlsRef.current && controlsRef.current.lock) {
          try {
            const promise = controlsRef.current.lock();
            if (promise && promise.catch) {
              promise.catch(() => { }); // Gracefully swallow lingering SecurityError
            }
          } catch (err) {
            // Ignore synchronous errors
          }
        }
      }
    };
    // Use mousedown to blur the active element before the click event triggers the lock
    document.addEventListener('mousedown', handleFocus);
    return () => document.removeEventListener('mousedown', handleFocus);
  }, []);

  // We explicitly manage PointerLockControls by keeping it enabled for mouse movement,
  // but we prevent its default spammy auto-lock by passing a non-existent selector.
  const isTyping = useSemanticStore(state => state.isTyping);

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

    // 4. Apply Logarithmic Acceleration relative to Camera Orientation
    inputVector.applyEuler(state.camera.rotation);
    const effectiveAccel = BASE_ACCEL * Math.pow(1.05, currentBoost);

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

  // enabled={!isTyping} allows mouse movement when not typing
  // selector="#prevent-default-click" ensures Drei doesn't bind its own click listener to document
  return <PointerLockControls ref={controlsRef} makeDefault enabled={!isTyping} selector="#prevent-default-click" />;
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

  const baselineA = values.length >= 1 ? values[0] : 0;
  const targetN = values.length >= 2 ? values[1] : 0; // The actual target hovered right now
  // We compute delta for the specific dimension
  const delta = Math.abs(baselineA - targetN);

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
      {values.length >= 1 && <div style={{ color: colors.baselineColor }}>A_i: {baselineA.toFixed(4)}</div>}
      <div style={{ color: '#00ccff' }}>B_i (Input): {targetN.toFixed(4)}</div>
      <div style={{ color: '#ff3333', marginTop: '2px', borderTop: '1px solid #444', paddingTop: '2px' }}>
        Abs Error: {delta.toFixed(4)}
      </div>
    </div>
  );
};

// XZ Plane Raycaster Probe
const ProbeSystem: React.FC<{ nodes: NodeData[], xStretch: number, uiScaleFactor: number }> = ({ nodes, xStretch, uiScaleFactor }) => {
  const { camera } = useThree();
  const setHoveredDimensionIndex = useSemanticStore(state => state.setHoveredDimensionIndex);
  const setSelectedValues = useSemanticStore(state => state.setSelectedValues);
  const setHoveredNode = useSemanticStore(state => state.setHoveredNode);
  const setSelectedThread = useSemanticStore(state => state.setSelectedThread);

  useEffect(() => {
    const handleMouseClick = () => {
      if (document.pointerLockElement) {
        // We are locked and looking around...
        const hoveredNode = useSemanticStore.getState().hoveredNode;
        if (hoveredNode) {
          setSelectedThread(hoveredNode);
        } else {
          setSelectedThread(null);
        }
      }
    };
    document.addEventListener('mousedown', handleMouseClick);
    return () => document.removeEventListener('mousedown', handleMouseClick);
  }, [setSelectedThread]);

  useFrame(() => {
    if (nodes.length < 2) { // Only need baseline and stress test nodes
      setHoveredDimensionIndex(null);
      setHoveredNode(null);
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
            let dn = 0; // default to 0 for Euclidean
            if (magA > 0 && magN > 0) {
              const diffSquaredSum = vA.reduce((sum, val, idx) => {
                const diff = val - (n.vector![idx] || 0);
                return sum + (diff * diff);
              }, 0);
              dn = Math.sqrt(diffSquaredSum);
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

          setHoveredNode(nodes[closestNodeIdx]);

          if (targetedIndex >= 0 && targetedIndex < 1024) {
            setHoveredDimensionIndex(targetedIndex);
            const values = [
              nodes[0]?.vector && nodes[0].vector.length > targetedIndex ? nodes[0].vector[targetedIndex] : 0, // baseline A
              nodes[closestNodeIdx]?.vector && nodes[closestNodeIdx].vector!.length > targetedIndex ? nodes[closestNodeIdx].vector![targetedIndex] : 0 // current target layer B
            ];
            setSelectedValues(values);
            return;
          }
        }
      }
    }

    setHoveredNode(null);
    setHoveredDimensionIndex(null);
  });

  return null;
};

const CameraAutoFit: React.FC<{ maxRadius: number | null, onComplete: () => void }> = ({ maxRadius, onComplete }) => {
  const { controls } = useThree();
  const [animating, setAnimating] = useState(false);

  useEffect(() => {
    if (maxRadius !== null && maxRadius > 0) {
      setAnimating(true);
    }
  }, [maxRadius]);

  useFrame((state, delta) => {
    if (!animating || maxRadius === null) return;

    // Cenital View Deterministic Framing
    const targetPos = new THREE.Vector3(0, maxRadius * 1.5, maxRadius * 0.5);
    const targetLookAt = new THREE.Vector3(0, 0, 0);

    // Lerp camera position
    state.camera.position.lerp(targetPos, delta * 2.5);

    // Depending on if PointerLock is engaged, updating lookAt can conflict.
    // If we have OrbitControls, we update target. If no specific controls block it, we lookAt.
    if (controls && (controls as any).target) {
      (controls as any).target.lerp(targetLookAt, delta * 2.5);
    } else {
      // Attempt smoothing
      const currentTarget = new THREE.Vector3(0, 0, -1).applyQuaternion(state.camera.quaternion).add(state.camera.position);
      currentTarget.lerp(targetLookAt, delta * 2.5);
      state.camera.lookAt(currentTarget);
    }

    // Stop animating when close enough
    if (state.camera.position.distanceTo(targetPos) < 1.0) {
      setAnimating(false);
      state.camera.position.copy(targetPos);
      state.camera.lookAt(targetLookAt);
      onComplete();
    }
  });

  return null;
};

const RadarHUD: React.FC<{ nodes: NodeData[], maxRadius: number | null }> = ({ nodes, maxRadius }) => {
  const firewallThreshold = useSemanticStore(state => state.firewallThreshold);
  const uiScaleFactor = useSemanticStore(state => state.uiScaleFactor);

  if (!maxRadius || maxRadius <= 0) return null;

  const radarSize = 200;
  const center = radarSize / 2;
  const scale = (radarSize / 2 - 10) / maxRadius; // 10px padding

  const ringRadius = firewallThreshold * 1.5 * uiScaleFactor * 50.0 * scale;

  return (
    <div style={{
      position: 'absolute',
      bottom: '20px',
      right: '20px',
      width: `${radarSize}px`,
      height: `${radarSize}px`,
      borderRadius: '50%',
      background: 'rgba(0, 20, 20, 0.6)',
      border: '2px solid #00ffff',
      boxShadow: '0 0 15px rgba(0, 255, 255, 0.3)',
      zIndex: 10,
      pointerEvents: 'none'
    }}>
      <svg width={radarSize} height={radarSize} style={{ position: 'absolute', top: 0, left: 0 }}>
        {/* Crosshairs */}
        <line x1={center} y1="0" x2={center} y2={radarSize} stroke="rgba(0, 255, 255, 0.3)" strokeWidth="1" />
        <line x1="0" y1={center} x2={radarSize} y2={center} stroke="rgba(0, 255, 255, 0.3)" strokeWidth="1" />

        {/* Firewall Boundary */}
        <circle cx={center} cy={center} r={ringRadius} fill="none" stroke="#ff0000" strokeWidth="2" strokeDasharray="4 4" />

        {/* Nodes */}
        {nodes.map((node, idx) => {
          const cx = center + node.position[0] * scale;
          const cy = center + node.position[2] * scale;
          const isMaster = idx === 0;
          return (
            <circle
              key={idx}
              cx={cx}
              cy={cy}
              r={isMaster ? 4 : 3}
              fill={node.color}
              stroke={isMaster ? '#fff' : '#000'}
              strokeWidth="1"
            />
          );
        })}
      </svg>
      <div style={{
        position: 'absolute',
        top: '-20px',
        width: '100%',
        textAlign: 'center',
        color: '#00ffff',
        fontSize: '0.75rem',
        fontFamily: 'monospace',
        textTransform: 'uppercase'
      }}>Tactical Radar</div>
    </div>
  );
};


const ArithmeticHUD: React.FC = () => {
  // Suppress THREE.Clock deprecation warning caused by React Three Fiber internals
  // and SecurityError from pointer lock without gesture
  useEffect(() => {
    const origWarn = console.warn;
    console.warn = (...args) => {
      if (typeof args[0] === 'string' && args[0].includes('THREE.Clock: This module has been deprecated')) return;
      origWarn(...args);
    };

    const origError = console.error;
    console.error = (...args) => {
      if (args.length > 0 && args[0] instanceof DOMException && args[0].name === 'SecurityError') {
        // Suppress PointerLock SecurityError spam
        return;
      }
      origError(...args);
    }

    // Global error listener for unhandled rejections related to pointer lock
    const handleRejection = (e: PromiseRejectionEvent) => {
      if (e.reason && e.reason.name === 'SecurityError') {
        e.preventDefault();
      }
    };
    window.addEventListener('unhandledrejection', handleRejection);

    return () => {
      console.warn = origWarn;
      console.error = origError;
      window.removeEventListener('unhandledrejection', handleRejection);
    };
  }, []);

  const [wordA, setWordA] = useState('rey');
  const [showInjector, setShowInjector] = useState(false);
  const [injectorText, setInjectorText] = useState('');
  const [injectorStatus, setInjectorStatus] = useState('');

  const uiScaleFactor = useSemanticStore((state) => state.uiScaleFactor);
  const setUiScaleFactor = useSemanticStore((state) => state.setUiScaleFactor);
  const xStretch = useSemanticStore((state) => state.xStretch);
  const setXStretch = useSemanticStore((state) => state.setXStretch);
  const amplitude = useSemanticStore((state) => state.amplitude);
  const setAmplitude = useSemanticStore((state) => state.setAmplitude);
  const boostFactor = useSemanticStore((state) => state.boostFactor);
  const setBoostFactor = useSemanticStore((state) => state.setBoostFactor);

  const stressTestQuery = useSemanticStore((state) => state.stressTestQuery);
  const setStressTestQuery = useSemanticStore((state) => state.setStressTestQuery);
  const firewallThreshold = useSemanticStore((state) => state.firewallThreshold);
  const setFirewallThreshold = useSemanticStore((state) => state.setFirewallThreshold);
  const setIsTyping = useSemanticStore((state) => state.setIsTyping);
  const uploadStatus = useSemanticStore((state) => state.uploadStatus);
  const setUploadStatus = useSemanticStore((state) => state.setUploadStatus);
  const isProcessing = useSemanticStore((state) => state.isProcessing);
  const setIsProcessing = useSemanticStore((state) => state.setIsProcessing);
  const setCurrentTaskId = useSemanticStore((state) => state.setCurrentTaskId);
  const ramUsageMb = useSemanticStore((state) => state.ramUsageMb);
  const setRamUsageMb = useSemanticStore((state) => state.setRamUsageMb);

  const colors = useSemanticStore((state) => state.colors);
  const setBaselineColor = useSemanticStore((state) => state.setBaselineColor);

  const topResults = useSemanticStore((state) => state.results);
  const setResults = useSemanticStore((state) => state.setResults);
  const selectedThread = useSemanticStore(state => state.selectedThread);
  const chatImpactNode = useSemanticStore(state => state.chatImpactNode);

  const [nodes, setNodes] = useState<NodeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [cameraMaxRadius, setCameraMaxRadius] = useState<number | null>(null);

  const [isStressInputFocused, setIsStressInputFocused] = useState(false);

  const handleInject = async () => {
    if (!injectorText.trim()) return;
    setInjectorStatus('Injecting...');
    try {
      const lines = injectorText.split('\n');
      const terms: Record<string, string> = {};
      lines.forEach(line => {
        if (line.includes(':')) {
          const [k, v] = line.split(':');
          terms[k.trim()] = v.trim();
        }
      });

      const res = await fetch('http://127.0.0.1:8000/corpus/inject-pack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: "Manual Context",
          color: "#ff00ff",
          description: "Context injected from HUD UI",
          terms: terms
        })
      });
      if (!res.ok) throw new Error('Failed to inject context');
      setInjectorStatus('Injection Successful');
      setTimeout(() => {
        setShowInjector(false);
        setInjectorStatus('');
        setInjectorText('');
      }, 1500);
    } catch (err: any) {
      setInjectorStatus(`Error: ${err.message}`);
    }
  };

  const handleUploadPdf = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setInjectorStatus('Vectorizing PDF (Initiating)...');
    setIsProcessing(true);
    setUploadStatus(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://127.0.0.1:8000/corpus/upload-pdf', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) throw new Error('Failed to upload PDF');

      const data = await res.json();
      const taskId = data.task_id;
      setCurrentTaskId(taskId);
      setInjectorStatus('Processing Vectors...');

      const pollInterval = window.setInterval(async () => {
        try {
          const statusRes = await fetch(`http://127.0.0.1:8000/corpus/task-status/${taskId}`);
          if (statusRes.ok) {
            const statusData = await statusRes.json();

            if (statusData.total_chunks > 0) {
              const progress = Math.round((statusData.processed_chunks / statusData.total_chunks) * 100);
              setUploadStatus(progress);
            }
            if (statusData.ram_usage_mb !== undefined) {
              setRamUsageMb(statusData.ram_usage_mb);
            }

            if (statusData.status === 'completed') {
              window.clearInterval(pollInterval);
              setInjectorStatus('Knowledge Updated! Refreshing Radar...');
              setIsProcessing(false);
              setCurrentTaskId(null);

              setTimeout(() => {
                calculate();
                setShowInjector(false);
                setInjectorStatus('');
                setUploadStatus(0);
                setRamUsageMb(0);
              }, 1500);
            } else if (statusData.status === 'CRITICAL_MEMORY_ABORT') {
              window.clearInterval(pollInterval);
              setInjectorStatus('CRITICAL MEMORY ABORT: 4GB RAM Cap Exceeded');
              setIsProcessing(false);
              setCurrentTaskId(null);
            } else if (statusData.status === 'error') {
              window.clearInterval(pollInterval);
              setInjectorStatus('Error processing PDF');
              setIsProcessing(false);
              setCurrentTaskId(null);
            }
          }
        } catch (pollErr) {
          console.error("Polling error", pollErr);
        }
      }, 500);

    } catch (err: any) {
      setInjectorStatus(`Error: ${err.message}`);
      setIsProcessing(false);
    } finally {
      // Clear the input so the user can select the same file again if they want
      e.target.value = '';
    }
  };

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
    setResults([]); // Clear previous results
    try {
      const newNodes: NodeData[] = [];

      // 1. Audit Master Baseline
      const baselineTokenizeRes = await fetch('http://127.0.0.1:8000/tokenize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: wordA, include_raw_vector: true })
      });
      if (!baselineTokenizeRes.ok) throw new Error(`Error en /tokenize para ${wordA}`);
      const baselineTokenizeData = await baselineTokenizeRes.json();

      let baselineVector: number[] = [];
      if (baselineTokenizeData.tokens && baselineTokenizeData.tokens.length > 0) {
        const mainToken = baselineTokenizeData.tokens[0];
        if (mainToken.vector) {
          baselineVector = mainToken.vector;
        }
      }

      newNodes.push({
        word: wordA,
        position: [0, 0, 0], // Explicitly lock anchor to [0,0,0]
        color: colors.baselineColor,
        vector: baselineVector,
        token_id: Math.random()
      });

      // 2. Extract Stress Test Query (if provided)
      if (stressTestQuery.trim() !== '') {
        const stressRes = await fetch('http://127.0.0.1:8000/tokenize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: stressTestQuery, include_raw_vector: true })
        });
        if (stressRes.ok) {
          const stressData = await stressRes.json();
          if (stressData.tokens && stressData.tokens.length > 0) {
            const stressToken = stressData.tokens[0];
            const pos = extractCoords(stressToken); // Radial mapping is determined during render based on Dn
            const vec = stressToken.vector || [];
            newNodes.push({
              word: stressTestQuery,
              position: pos,
              color: '#ff3300', // Warning Orange/Red default
              vector: vec,
              token_id: Math.random()
            });
          }
        }
      }

      setNodes(newNodes);

      // --- AUTO-FIT CAMERA LOGIC ---
      let maxDn = 0;

      if (newNodes.length > 1 && newNodes[1].vector && baselineVector.length > 0) {
        const vA = baselineVector;
        const magA = getVectorMagnitude(vA);
        const magN = getVectorMagnitude(newNodes[1].vector!);
        if (magA > 0 && magN > 0) {
          const diffSquaredSum = vA.reduce((sum, val, idx) => {
            const diff = val - (newNodes[1].vector![idx] || 0);
            return sum + (diff * diff);
          }, 0);
          maxDn = Math.sqrt(diffSquaredSum);

          const angle = Math.atan2(newNodes[1].vector![2], newNodes[1].vector![0]);
          const normX = Math.cos(angle);
          const normZ = Math.sin(angle);
          const BASE_SPREAD = 50.0;

          // Update stress node visual position
          newNodes[1].position = [
            normX * maxDn * uiScaleFactor * BASE_SPREAD,
            0,
            normZ * maxDn * uiScaleFactor * BASE_SPREAD
          ];
        }
      }

      setNodes([...newNodes]); // Force update with new positions

      // Calculate max bounding radius for deterministic cenital framing
      const ringRadius = firewallThreshold * 1.5 * uiScaleFactor * 50.0;
      const maxNodeRadius = maxDn * uiScaleFactor * 50.0;
      const maxRadius = Math.max(ringRadius, maxNodeRadius) + (50 * uiScaleFactor); // add small padding

      setCameraMaxRadius(maxRadius);

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

  const selectedDnRaw = React.useMemo(() => {
    if (!selectedThread || !selectedThread.vector || nodes.length < 1 || !nodes[0].vector) return null;
    const vA = nodes[0].vector;
    const n = selectedThread.vector;
    const diffSquaredSum = vA.reduce((sum, val, idx) => {
      const diff = val - (n[idx] || 0);
      return sum + (diff * diff);
    }, 0);
    return Math.sqrt(diffSquaredSum);
  }, [selectedThread, nodes]);

  const displayNodes = React.useMemo(() => {
    let result = [...nodes];
    if (chatImpactNode && nodes.length > 0 && nodes[0].vector) {
      const vA = nodes[0].vector;
      const magA = getVectorMagnitude(vA);
      const vecN = chatImpactNode.vector;
      const magN = getVectorMagnitude(vecN);
      let dn = 0;
      if (magA > 0 && magN > 0) {
        const diffSquaredSum = vA.reduce((sum, val, idx) => {
          const diff = val - (vecN[idx] || 0);
          return sum + (diff * diff);
        }, 0);
        dn = Math.sqrt(diffSquaredSum);
      }
      const angle = Math.atan2(vecN[2], vecN[0]);
      const BASE_SPREAD = 50.0;

      const pos = [
        Math.cos(angle) * dn * uiScaleFactor * BASE_SPREAD,
        0,
        Math.sin(angle) * dn * uiScaleFactor * BASE_SPREAD
      ] as [number, number, number];

      result.push({
        word: chatImpactNode.word,
        position: pos,
        color: chatImpactNode.color,
        vector: vecN,
        token_id: Math.random()
      });
    }
    return result;
  }, [nodes, chatImpactNode, uiScaleFactor]);

  // Firewall Status Check
  const firewallStatus = React.useMemo(() => {
    if (nodes.length < 2 || !nodes[0].vector || !nodes[1].vector) return null;
    const vRes = nodes[0].vector; // Master Baseline Result (index 0)
    const vTest = nodes[1].vector; // Stress Test Query (index 1)

    const diffSquaredSum = vRes.reduce((sum, val, idx) => {
      const diff = val - (vTest[idx] || 0);
      return sum + (diff * diff);
    }, 0);
    const dn = Math.sqrt(diffSquaredSum);

    return {
      distance: dn,
      isBlocked: dn >= firewallThreshold
    };
  }, [nodes, firewallThreshold]);

  return (
    <>
      <TelemetryHUD nodesCount={displayNodes.length > 0 ? displayNodes.length * 1024 : 0} xStretch={xStretch} />
      <CrosshairHUD />
      <TargetingHUD />
      <ChatHUD />

      {/* L2 Analysis Panel */}
      {selectedThread && selectedDnRaw !== null && (
        <div style={{
          position: 'absolute',
          top: '20px',
          right: '20px',
          zIndex: 10,
          background: 'rgba(0, 0, 0, 0.95)',
          border: '1px solid #ff00ff',
          padding: '15px 20px',
          borderRadius: '8px',
          color: '#ff00ff',
          fontFamily: 'monospace',
          minWidth: '300px',
          boxShadow: '0 0 20px rgba(255, 0, 255, 0.3)',
        }}>
          <h3 style={{ margin: '0 0 15px 0', borderBottom: '1px solid #ff00ff', paddingBottom: '5px', textTransform: 'uppercase' }}>
            L2 Inspection: {selectedThread.word}
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#fff' }}>
              <span>Raw L2 Distance ($D_n$):</span>
              <span style={{ color: '#00ffff', fontWeight: 'bold' }}>{selectedDnRaw.toFixed(5)}</span>
            </div>
            <div style={{ padding: '8px', background: 'rgba(0,0,0,0.5)', borderRadius: '4px', fontSize: '0.8rem', color: '#aaa', border: '1px solid #333' }}>
              <div>Live Formula:</div>
              <div style={{ color: '#fff', fontStyle: 'italic', marginTop: '4px' }}>sqrt(sum((A_i - B_i)^2))</div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#fff', marginTop: '5px' }}>
              <span>Derived Similarity Config:</span>
              <span style={{ color: '#00ff00', fontWeight: 'bold' }}>{((1 / (1 + selectedDnRaw)) * 100).toFixed(2)}%</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '5px', textAlign: 'right', borderBottom: '1px solid #333', paddingBottom: '10px' }}>
              Confidence Formula: 1 / (1 + D_n)
            </div>

            {/* Noise Delta Map */}
            <div style={{ marginTop: '10px' }}>
              <div style={{ color: '#ffea00', fontSize: '0.85rem', marginBottom: '5px', textTransform: 'uppercase', fontWeight: 'bold' }}>Noise Vectors (Delta &gt; 0.2)</div>
              {displayNodes.length > 0 && displayNodes[0].vector && selectedThread.vector ? (
                (() => {
                  const vA = displayNodes[0].vector;
                  const vN = selectedThread.vector;
                  const diffs = vA.map((val: number, idx: number) => ({ index: idx, delta: Math.abs(val - (vN[idx] || 0)) }))
                    .filter((d: { delta: number }) => d.delta > 0.2)
                    .sort((a: { delta: number }, b: { delta: number }) => b.delta - a.delta)
                    .slice(0, 5);

                  if (diffs.length === 0) return <div style={{ fontSize: '0.8rem', color: '#00ff00' }}>No significant noise detected.</div>;

                  return diffs.map((d: { index: number, delta: number }, i: number) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '3px' }}>
                      <span style={{ color: '#aaa' }}>DIM-{d.index}</span>
                      <span style={{ color: '#ff3300' }}>+{d.delta.toFixed(4)}</span>
                    </div>
                  ));
                })()
              ) : null}
            </div>
          </div>
        </div>
      )}

      {/* Context Injector Modal */}
      {showInjector && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 50,
          background: 'rgba(0, 10, 10, 0.95)',
          border: '1px solid #00ffff',
          padding: '20px',
          borderRadius: '8px',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          minWidth: '400px',
          boxShadow: '0 0 30px rgba(0, 255, 255, 0.5)'
        }}>
          <h3 style={{ margin: 0, color: '#00ffff', textTransform: 'uppercase', borderBottom: '1px solid #00ffff', paddingBottom: '5px' }}>Inject Knowledge Context</h3>
          <p style={{ margin: 0, color: '#aaa', fontSize: '0.8rem' }}>Format: term : definition (one per line)</p>
          <textarea
            value={injectorText}
            onFocus={() => setIsTyping(true)}
            onBlur={() => setIsTyping(false)}
            onChange={(e) => setInjectorText(e.target.value)}
            placeholder="Term : A comprehensive description."
            style={{ width: '100%', height: '100px', background: '#000', color: '#fff', border: '1px solid #005555', padding: '10px', fontFamily: 'monospace', borderRadius: '4px', resize: 'vertical' }}
          />
          <div style={{ padding: '10px', border: '1px dashed #005555', borderRadius: '4px', textAlign: 'center', background: 'rgba(0,0,0,0.5)' }}>
            <span style={{ color: '#00ffff', fontSize: '0.8rem', display: 'block', marginBottom: '8px', textTransform: 'uppercase' }}>Physical Knowledge Ingestion (PDF)</span>
            <input
              type="file"
              accept=".pdf"
              onChange={handleUploadPdf}
              disabled={isProcessing}
              style={{
                color: '#aaa',
                fontFamily: 'monospace',
                fontSize: '0.8rem',
                cursor: isProcessing ? 'not-allowed' : 'pointer'
              }}
            />
            {isProcessing && (
              <div style={{ marginTop: '10px', background: '#002222', borderRadius: '4px', height: '8px', width: '100%', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${uploadStatus}%`,
                  background: '#00ffff',
                  boxShadow: '0 0 10px #00ffff',
                  transition: 'width 0.3s ease-out'
                }} />
              </div>
            )}
            {isProcessing && ramUsageMb > 0 && (
              <div style={{ marginTop: '5px', color: '#ffcc00', fontSize: '0.75rem', fontFamily: 'monospace' }}>
                Worker RAM: {ramUsageMb} MB
              </div>
            )}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: injectorStatus.includes('Error') || injectorStatus.includes('CRITICAL') ? '#ff3333' : '#00ff00', fontSize: '0.8rem' }}>{injectorStatus}</span>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => setShowInjector(false)}
                style={{ background: 'transparent', border: '1px solid #555', color: '#aaa', padding: '8px 15px', borderRadius: '4px', cursor: 'pointer' }}
              >
                Cancel
              </button>
              <button
                onClick={handleInject}
                style={{ background: '#003333', border: '1px solid #00ffff', color: '#00ffff', padding: '8px 15px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
              >
                Inject Pack
              </button>
            </div>
          </div>
        </div>
      )}

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
          THE AUDITOR'S CONSOLE
        </h2>

        {/* --- ZONE ALPHA: MASTER BASELINE --- */}
        <div style={{ borderBottom: '1px solid #005555', paddingBottom: '10px' }}>
          <div style={{ color: '#00ccff', fontSize: '0.9rem', marginBottom: '10px', fontWeight: 'bold' }}>ZONE ALPHA: MASTER BASELINE</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <label style={{ fontSize: '0.8rem', color: colors.baselineColor }}>Baseline Input</label>
            <div style={{ display: 'flex', gap: '5px' }}>
              <input
                value={wordA}
                onFocus={() => setIsTyping(true)}
                onBlur={() => setIsTyping(false)}
                onChange={(e) => setWordA(e.target.value)}
                style={{ flex: 1, padding: '8px', background: '#000', border: `1px solid ${colors.baselineColor}`, color: '#fff', borderRadius: '4px' }}
              />
              <input type="color" value={colors.baselineColor} onChange={(e) => setBaselineColor(e.target.value)} style={{ width: '40px', padding: '0', border: 'none', background: 'none' }} />
            </div>
          </div>
        </div>

        {/* --- ZONE BETA: STRESS TEST SANDBOX --- */}
        <div style={{ borderBottom: '1px solid #005555', paddingBottom: '10px' }}>
          <div style={{ color: '#ffcc00', fontSize: '0.9rem', marginBottom: '10px', fontWeight: 'bold' }}>ZONE BETA: STRESS TEST SANDBOX</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <label style={{ fontSize: '0.8rem', color: '#ff3300' }}>STRESS_TEST_QUERY</label>
            <div style={{ display: 'flex', gap: '5px' }}>
              <input
                value={stressTestQuery}
                onFocus={() => { setIsStressInputFocused(true); setIsTyping(true); }}
                onBlur={() => { setIsStressInputFocused(false); setIsTyping(false); }}
                onChange={(e) => setStressTestQuery(e.target.value)}
                placeholder="Enter query to stress test against BASELINE"
                style={{
                  flex: 1,
                  padding: '8px',
                  background: '#000',
                  border: `1px solid #ff3300`,
                  color: '#fff',
                  borderRadius: '4px',
                  boxShadow: isStressInputFocused ? '0 0 15px #ff3300' : 'none',
                  outline: 'none',
                  transition: 'box-shadow 0.2s ease-in-out'
                }}
              />
            </div>
          </div>
        </div>

        {/* --- FIREWALL STATUS HUD --- */}
        <div style={{ padding: '10px', background: firewallStatus ? (firewallStatus.isBlocked ? 'rgba(255, 0, 0, 0.2)' : 'rgba(0, 255, 0, 0.2)') : 'rgba(0,0,0,0.5)', border: `1px solid ${firewallStatus ? (firewallStatus.isBlocked ? '#ff0000' : '#00ff00') : '#555'}`, borderRadius: '4px' }}>
          <div style={{ fontSize: '0.8rem', color: '#aaa', marginBottom: '5px', textTransform: 'uppercase' }}>Firewall Status</div>
          {firewallStatus ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: firewallStatus.isBlocked ? '#ff3333' : '#00ff00' }}>
                STATE: {firewallStatus.isBlocked ? 'BLOCKED' : 'SAFE'}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#fff' }}>
                <span>L2 Distance ($D_n$):</span>
                <span>{firewallStatus.distance.toFixed(4)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#fff' }}>
                <span>Tolerance (Threshold):</span>
                <span>{firewallThreshold.toFixed(1)}</span>
              </div>
            </div>
          ) : (
            <div style={{ color: '#666', fontSize: '0.8rem' }}>AWAITING TEST VECTOR...</div>
          )}
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

          <label style={{ fontSize: '0.8rem', color: '#ffcc00', display: 'flex', justifyContent: 'space-between', marginTop: '5px' }}>
            <span>Firewall Tolerance</span>
            <span>{firewallThreshold.toFixed(1)}</span>
          </label>
          <input
            type="range"
            min="5.0"
            max="100.0"
            step="0.5"
            value={firewallThreshold}
            onChange={(e) => setFirewallThreshold(parseFloat(e.target.value))}
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
          {loading ? 'CALCULATING...' : 'EXECUTE AUDIT'}
        </button>

        <button
          onClick={() => setShowInjector(true)}
          style={{
            padding: '8px',
            background: 'rgba(0,0,0,0.5)',
            color: '#ff00ff',
            border: '1px dashed #ff00ff',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold',
            marginTop: '5px',
            textTransform: 'uppercase',
            transition: 'all 0.3s',
            fontSize: '0.8rem'
          }}
        >
          [+] INJECT CONTEXT
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
        <ProbeSystem nodes={displayNodes} xStretch={xStretch} uiScaleFactor={uiScaleFactor} />
        <CameraAutoFit maxRadius={cameraMaxRadius} onComplete={() => setCameraMaxRadius(null)} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <FlightControls />

        {/* Threshold Boundary Rings */}
        <group rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]}>
          {/* Inner safe ring */}
          <Ring args={[(firewallThreshold * 0.5 * uiScaleFactor * 50.0) - 0.5, firewallThreshold * 0.5 * uiScaleFactor * 50.0, 64]}>
            <meshBasicMaterial color="#005500" transparent opacity={0.3} side={THREE.DoubleSide} />
          </Ring>
          {/* The exact firewall threshold ring */}
          <Ring args={[(firewallThreshold * uiScaleFactor * 50.0) - 1.0, firewallThreshold * uiScaleFactor * 50.0, 128]}>
            <meshBasicMaterial color="#ff0000" transparent opacity={0.8} side={THREE.DoubleSide} />
          </Ring>
          {/* Outer warning ring */}
          <Ring args={[(firewallThreshold * 1.5 * uiScaleFactor * 50.0) - 0.5, firewallThreshold * 1.5 * uiScaleFactor * 50.0, 128]}>
            <meshBasicMaterial color="#ff3300" transparent opacity={0.2} side={THREE.DoubleSide} />
          </Ring>
        </group>

        {/* Render nodes and text */}
        {displayNodes.map((node, i) => {
          // Word A defaults to [0, 0, 0], others calculate Radial Cosine Distance.
          let pos = [0, 0, 0] as [number, number, number];
          if (i > 0 && node.vector && node.vector.length > 0) {
            const vA = displayNodes[0]?.vector || [];
            const magA = getVectorMagnitude(vA);
            const magN = getVectorMagnitude(node.vector);
            let dn = 0;
            if (magA > 0 && magN > 0) {
              const diffSquaredSum = vA.reduce((sum, val, idx) => {
                const diff = val - (node.vector![idx] || 0);
                return sum + (diff * diff);
              }, 0);
              dn = Math.sqrt(diffSquaredSum);
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
        {displayNodes.map((node, i) => {
          if (!node.vector || node.vector.length === 0) return null;

          // Radial Cosine Distance Calculation for Threads
          let pos = [0, 0, 0] as [number, number, number];
          if (i > 0 && node.vector && node.vector.length > 0) {
            const vA = displayNodes[0]?.vector || [];
            const magA = getVectorMagnitude(vA);
            const magN = getVectorMagnitude(node.vector);
            let dn = 0;
            if (magA > 0 && magN > 0) {
              const diffSquaredSum = vA.reduce((sum, val, idx) => {
                const diff = val - (node.vector![idx] || 0);
                return sum + (diff * diff);
              }, 0);
              dn = Math.sqrt(diffSquaredSum);
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

          // Render Firewall Thread Logic
          let threadIsBlocked = false;
          let labelText = `${node.word} [${i === 0 ? "BASELINE" : "STRESS"}]`;

          if (i === 1 && firewallStatus) { // Stress test node is at index 1
            threadIsBlocked = firewallStatus.isBlocked;
          }

          if (chatImpactNode && i === displayNodes.length - 1) {
            threadIsBlocked = chatImpactNode.is_blocked;
            labelText = `${node.word} [CHAT PROMPT]`;
          }

          return (
            <group key={`ribbon-${node.token_id || i}`} position={pos}>
              <Billboard position={[-(512 * xStretch) - 20, 0, 0]}>
                <Text
                  color={threadIsBlocked ? '#ff3300' : node.color}
                  fontSize={12}
                  anchorX="center"
                  anchorY="middle"
                  outlineWidth={0.5}
                  outlineColor="#000000"
                  fontStyle="italic"
                >
                  {labelText}
                </Text>
              </Billboard>
              <SemanticThread data={node.vector} xStretch={xStretch} position={[0, 0, 0]} amplitude={amplitude} baseColor={node.color} isBlocked={threadIsBlocked} />
            </group>
          )
        })}

        {/* Grid helper for scale reference */}
        <gridHelper args={[20, 20, '#222222', '#111111']} position={[0, -5, 0]} />
      </Canvas>

      {/* Radar Map Overlay - Relocated to standard HTML DOM overlay */}
      <RadarHUD maxRadius={cameraMaxRadius} nodes={displayNodes} />
    </>
  );
};

export default ArithmeticHUD;
