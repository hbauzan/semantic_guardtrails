import React, { useState, useEffect } from 'react';
import { useSemanticStore } from '../store';

interface SystemStats {
    ps: { cpu_percent: number; mem_percent: number; disk_percent: number };
    db: { size_mb: number };
    be: { cpu_percent: number; mem_mb: number };
    ingestion: { active_tasks: number; status: string };
}

interface Props {
    isBlocked: boolean;
}

export const TelemetryMonkeyHUD: React.FC<Props> = ({ isBlocked }) => {
    const isProcessing = useSemanticStore(state => state.isProcessing);
    const ramUsageMb = useSemanticStore(state => state.ramUsageMb);
    const [stats, setStats] = useState<SystemStats | null>(null);

    // ASCII Animation Engine Hook
    const useAsciiAnimation = (state: 'SAFE' | 'WORKING' | 'WARNING' | 'CRITICAL', intervalMs: number) => {
        const [frameIndex, setFrameIndex] = useState(0);

        const frames = {
            'SAFE': [
                `
  __
 w  c(..)o   (
  \\__(-)    __)
      /\\   (
     /(_)___)
    w /|
     | \\
    m  m
`,
                `
  __
 w  c(..)o    )
  \\__(-)   __(
      /\\    )
     /(_)___)
    w /|
     | \\
    m  m
`,
                `
  __
 w  c(..)o   (
  \\__(-)    __)
      /\\   (
     /(_)___)
    w /|
     | \\
    m  m
`
            ],
            'WORKING': [
                `
  __
 w  c(..)o  
  \\__(-)   [===]
      /\\   [===]
     /(_)  [===]
    w /|
     | \\
    m  m
`,
                `
  __
 w  c(..)o  
  \\__(-)   [=  ]
      /\\   [ ==]
     /(_)  [  =]
    w /|
     | \\
    m  m
`,
                `
  __
 w  c(..)o  
  \\__(-)   [  =]
      /\\   [=  ]
     /(_)  [ ==]
    w /|
     | \\
    m  m
`
            ],
            'WARNING': [
                `
  __
 w  c(xx)o   ?
  \\__(o)    ?
      /\\   
     /(_)___)
    w /|
     | \\
    m  m
`,
                `
  __
 w  c(xx)o    !
  \\__(o)       !
      /\\   
     /(_)___)
    w /|
     | \\
    m  m
`
            ],
            'CRITICAL': [
                `
     _
   _[*]_
  /     \\
 | () () |
  \\  ^  /
   |||||
   |||||
`,
                `
     _
   _[*]_
  /     \\
 | (*) (*)|
  \\  ^  /
   |||||
   |||||
`
            ]
        };

        useEffect(() => {
            const currentFrames = frames[state];
            if (currentFrames.length <= 1) return;

            const timer = setInterval(() => {
                setFrameIndex(prev => (prev + 1) % currentFrames.length);
            }, intervalMs);

            return () => clearInterval(timer);
        }, [state, intervalMs]);

        // Reset frame index on state change so we don't out-of-bounds index
        useEffect(() => {
            setFrameIndex(0);
        }, [state]);

        const currentFramesArray = frames[state];
        return currentFramesArray[frameIndex % currentFramesArray.length];
    };

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await fetch('http://127.0.0.1:8000/system/stats');
                if (res.ok) {
                    const data = await res.json();
                    setStats(data);
                }
            } catch (err) {
                console.error("Failed to fetch system stats", err);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 2000);
        return () => clearInterval(interval);
    }, []);

    let monkeyState: 'SAFE' | 'WORKING' | 'WARNING' | 'CRITICAL' = 'SAFE';
    if (isBlocked) {
        monkeyState = 'CRITICAL';
    } else if (ramUsageMb > 4000) {
        monkeyState = 'WARNING';
    } else if (stats && stats.be.mem_mb > 3276) {
        // Note: I separated the logic directly so no overlap error happens with 'WARNING'
        monkeyState = 'WARNING';
    } else if (isProcessing || (stats && stats.ingestion.status === 'processing')) {
        monkeyState = 'WORKING';
    }

    const asciiArt = useAsciiAnimation(monkeyState, 250);

    const asciiColor = monkeyState === 'CRITICAL' ? '#ff0000' : monkeyState === 'WARNING' ? '#ffaa00' : '#00ff00';

    return (
        <div style={{
            position: 'absolute',
            bottom: '20px',
            right: '250px', // to left of radar HUD
            zIndex: 10,
            background: 'rgba(0, 20, 20, 0.8)',
            border: '1px solid #00ff00',
            padding: '10px 15px',
            borderRadius: '4px',
            color: '#00ff00',
            fontFamily: 'monospace',
            fontSize: '0.8rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '5px',
            boxShadow: '0 0 10px rgba(0, 255, 0, 0.2)',
            pointerEvents: 'none',
            width: '260px'
        }}>
            <div style={{ whiteSpace: 'pre', color: asciiColor, lineHeight: '1.2em', margin: '-10px 0 5px 0' }}>
                {asciiArt}
            </div>
            {stats ? (
                <>
                    <div>PS  CPU[ {stats.ps.cpu_percent.toFixed(1)}%] MEM [ {stats.ps.mem_percent.toFixed(1)}%] HD [ {stats.ps.disk_percent.toFixed(1)}%]</div>
                    <div>DB  SIZE[ {stats.db.size_mb.toFixed(1)}MB]</div>
                    <div>BE  CPU [ {stats.be.cpu_percent.toFixed(1)}%] MEM [ {stats.be.mem_mb.toFixed(1)}MB]</div>
                </>
            ) : (
                <div>Awaiting Telemetry...</div>
            )}
        </div>
    );
};
