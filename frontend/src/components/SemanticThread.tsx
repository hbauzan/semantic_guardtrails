import React, { useRef, useMemo, useEffect, useState } from 'react';
import * as THREE from 'three';
import { Line } from '@react-three/drei';

interface SemanticThreadProps {
  data: Float32Array | number[]; // 1024 dimensions
  position?: [number, number, number];
  xStretch?: number;
  amplitude?: number;
  baseColor?: string;
}

export const SemanticThread: React.FC<SemanticThreadProps> = ({
  data,
  position = [0, 0, 0],
  xStretch = 1.0,
  amplitude = 100.0,
  baseColor = '#ffffff'
}) => {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const count = 1024;

  const [linePoints, setLinePoints] = useState<THREE.Vector3[]>([]);

  const parsedBaseColor = useMemo(() => new THREE.Color(baseColor), [baseColor]);

  const shaderMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        uBaseColor: { value: parsedBaseColor }
      },
      vertexShader: `
        attribute float instanceValue;
        varying float vValue;
        
        #include <common>

        void main() {
          vValue = instanceValue;
          vec4 mvPosition = modelViewMatrix * instanceMatrix * vec4(position, 1.0);
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        uniform vec3 uBaseColor;
        varying float vValue;

        void main() {
          vec3 finalColor;
          float alpha = 1.0;

          if (vValue >= 0.5) {
            finalColor = uBaseColor;
          } else if (vValue <= -0.5) {
            finalColor = vec3(0.3, 0.0, 0.8); // Deep Blue/Purple
          } else {
            finalColor = vec3(0.2, 0.2, 0.2);
            alpha = 0.05;
          }

          if (abs(vValue) < 0.1) {
             discard;
          }

          gl_FragColor = vec4(finalColor, alpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide
    });
  }, []);

  useEffect(() => {
    shaderMaterial.uniforms.uBaseColor.value = parsedBaseColor;
  }, [parsedBaseColor, shaderMaterial]);

  const dummy = useMemo(() => new THREE.Object3D(), []);

  useEffect(() => {
    if (!meshRef.current || !data) return;

    // RENDER GUARD: Strictly abort setMatrixAt execution if vector is not exactly 1024 floats
    if (data.length !== 1024 || data.some(v => Number.isNaN(v) || typeof v !== 'number')) {
      return;
    }

    const mesh = meshRef.current;

    const valueArray = new Float32Array(count);
    const dataLen = data.length;

    const points: THREE.Vector3[] = [];

    for (let i = 0; i < count; i++) {
      const val = i < dataLen ? data[i] : 0;
      valueArray[i] = val;

      const x = (i - 512) * xStretch;
      const y = val * amplitude;
      const z = 0;

      dummy.position.set(x, y, z);
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);

      points.push(new THREE.Vector3(x, y, z));
    }

    requestAnimationFrame(() => {
      if (meshRef.current && meshRef.current.geometry) {
        mesh.instanceMatrix.needsUpdate = true;
        mesh.geometry.setAttribute('instanceValue', new THREE.InstancedBufferAttribute(valueArray, 1));
        mesh.geometry.computeBoundingSphere();
      }
    });

    setLinePoints(points);
  }, [data, xStretch, amplitude, dummy]);

  if (!data || data.length !== 1024) return null;

  return (
    <group position={position}>
      <instancedMesh ref={meshRef} args={[undefined, undefined, count]} material={shaderMaterial} frustumCulled={false}>
        <sphereGeometry args={[0.12, 8, 8]} />
      </instancedMesh>
      {linePoints.length > 0 && (
        <Line
          points={linePoints}
          color={baseColor}
          lineWidth={1.5}
          transparent={true}
          opacity={0.8}
          depthWrite={false}
          frustumCulled={false}
        />
      )}
    </group>
  );
};

export default SemanticThread;

