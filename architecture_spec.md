# Architecture Specification: Semantic Guardrails

## 1. Stack
* **API Server:** FastAPI (Uvicorn)
* **Vector Engine:** LanceDB (BGE-M3 1024D)
* **Environment:** `sg_env`

## 2. Core Endpoints
* `POST /embed`: Text to 1024D vector.
* `POST /arithmetic`: Vector math (`A - B + C`).

## 3. Tooling
* **Context Packager:** `semantic_guardtrails_packager.py` (Triggered via `run_pack.sh`). Generates unified context bundles for LLM ingestion, enforcing `sg_env` validation and state checks.

## 6. Current Flight Status
### Navigation & Flight Mechanics
*   **Smooth Flight**: Inertia-based camera movement with drag damping (AWSD + QE).
*   **Hyper-Boost x100**: Instantaneous thrust application (Shift key) using dynamic `BOOST_FACTOR` slider, capable of x100 effective speed multiplication. Both acceleration and deceleration are responsive.
*   **Mouse Look**: `PointerLockControls` integrated with global click-to-lock, featuring 2e-compliant input suppression (ignores typing in text fields).

### Visualizations
*   **Semantic Ribbon Trace**: Real-time rendering of 1024D vector geometries strictly utilizing `THREE.InstancedMesh` with a predefined 1024 count for optimal performance, and connected points forming a continuous thread with `THREE.Line`.
    *   **Spatial Positioning Algorithm (Radial Cosine Distance on XZ Plane)**:
        *   **Cosine Distance ($D_n$)**: Calculated relative to the master token (Word A) which is rigidly fixed at the absolute origin `[0, 0, 0]`. If vector magnitude is 0, $D_n$ defaults to 1.
        *   **Radial Mapping (Semantic Disk)**: Thread anchor position is defined purely on the 2D XZ plane. The bearing is derived from dimensions `[0]` and `[2]`: `angle = Math.atan2(vector[2], vector[0])`. Position maps as `[Math.cos(angle) * Dn * ui_scale * 50, 0, Math.sin(angle) * Dn * ui_scale * 50]`.
        *   **Local Space Mapping (Visual DNA)**:
            *   `X`: Linear stretch of the dimensions `(index - 512) * xStretch`. `xStretch` scales dynamically between `0.1` and `40.0`.
            *   `Y`: The $Y$-axis is entirely reserved for dimension magnitude, growing functionally upwards from the anchor floor: `vectorValue * amplitude`. Target amplitude spans to `50.0`.
            *   `Z`: Local Z is 0. Group encapsulation handles global offset on the 2D plane.
    *   **Chromatic Mapping Algorithm**:
        *   `~1.0`: Bright White/Yellow/Green (Emissive).
        *   `~0.0`: Opacity 0.1 / Transparent (Fragment discard via shader).
        *   `~-1.0`: Deep Blue/Violet/Red.

### Deep Observability & Telemetry
*   **Zero-Dependency Native HUD**: Telemetry overlay built built with `requestAnimationFrame` ensuring zero external profiling overhead. Reports active **FPS**, total **Nodes**, current **xStretch**, and total **SECTOR SIZE**.
*   **Infinite Visibility Render bounds**: Canvas camera Frustum is statically configured to `{ near: 1, far: 200000 }` to guarantee no thread dropout at x40 stretches.
*   **Dimension Probe (Crosshair)**: A fixed SVG crosshair mathematically intercepts the specific S-DNA array index (`i ∈ [0, 1023]`) from the camera's viewport orientation.
    *   Targets exact dimensional vectors revealing `DIM-ID` and precise float `MAGNITUDE` arrays across all active semantic threads.