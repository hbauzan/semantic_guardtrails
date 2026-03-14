# Architecture Specification: Semantic Guardrails

## 1. Stack
* **API Server:** FastAPI (Uvicorn)
* **Vector Engine:** LanceDB (BGE-M3 1024D)
* **Environment:** `sg_env`

## 2. Core Endpoints
* `POST /tokenize`: Returns raw 1024D vector mappings, utilized heavily by the Auditor Console for stress-test inputs and Master Baseline validation.

## 3. Tooling
* **Context Packager:** `semantic_guardtrails_packager.py` (Triggered via `run_pack.sh`). Generates unified context bundles for LLM ingestion, enforcing `sg_env` validation and state checks.

## 6. Current Flight Status
### Navigation & Flight Mechanics
*   **Smooth Flight**: Inertia-based camera movement with drag damping (AWSD + QE).
*   **Hyper-Boost x100**: Instantaneous logarithmic/exponential thrust application (Shift key) using dynamic `BOOST_FACTOR` slider, capable of fine-grained low speed and explosive high speed control.
*   **Mouse Look**: `PointerLockControls` integrated with global click-to-lock, featuring 2e-compliant input suppression (ignores typing in text fields). PointerLock is strictly gesture-enforced to comply with browser security policies.
*   **Tactical Radial Radar HUD**: Replaces legacy 3D Compass. A 2D SVG overlay rendering the Master Baseline at center, a Firewall threshold ring, and mapping semantic threads relative to a calculated deterministic `maxRadius`. Screen-space locked to the bottom right. All 2D SVG overlays (like the Tactical Radial Radar HUD) are rendered strictly in the DOM layer outside the WebGL Canvas.
*   **Deterministic Auto-Fit Camera**: Automatic deterministic camera framing triggered upon `EXECUTE AUDIT`. Computes a `maxRadius` encompassing the Master Baseline, extreme stress threads, and Firewall boundaries. Forces the viewport to a Cenital View (`Y = maxRadius * 1.5`, `Z = maxRadius * 0.5`) staring directly at the absolute origin.

### Visualizations
*   **Semantic Ribbon Trace**: Real-time rendering of 1024D vector geometries strictly utilizing `THREE.InstancedMesh` with a predefined 1024 count for optimal performance, and connected points forming a continuous thread with `THREE.Line`.
    *   **Spatial Positioning Algorithm (Radial Euclidean Distance on XZ Plane)**:
        *   **Euclidean Distance ($D_n$)**: Calculated relative to the master token (Word A) which is rigidly fixed at the absolute origin `[0, 0, 0]`.
        *   **Radial Mapping (Semantic Disk)**: Thread anchor position is defined purely on the 2D XZ plane. The bearing is derived from dimensions `[0]` and `[2]`: `angle = Math.atan2(vector[2], vector[0])`. Position maps as `[Math.cos(angle) * Dn * ui_scale * 50, 0, Math.sin(angle) * Dn * ui_scale * 50]`.
        *   **Local Space Mapping (Visual DNA)**:
            *   `X`: Linear stretch of the dimensions `(index - 512) * xStretch`. `xStretch` scales dynamically between `0.1` and `40.0`.
            *   `Y`: The $Y$-axis is entirely reserved for dimension magnitude, growing functionally upwards from the anchor floor: `vectorValue * amplitude`. Target amplitude spans to `50.0`.
            *   `Z`: Local Z is 0. Group encapsulation handles global offset on the 2D plane.
    *   **Chromatic Mapping Algorithm**:
        *   `~1.0`: Bright White/Yellow/Green (Emissive).
        *   `~0.0`: Opacity 0.1 / Transparent (Fragment discard via shader).
        *   `~-1.0`: Deep Blue/Violet/Red.
    *   **Firewall Threat Indicator**: Setting `isBlocked` prop forces shader material to blink Warning Red, overriding standard chromatic values when Euclidean distance triggers an alert.

### The Dual-Zone Auditor's Console
The UI has been refactored into a **Dual-Zone Security Console**, purging old vector arithmetic visualizations.
*   **Zone Alpha (Master Baseline)**: A single input query rigidly fixed at `[0,0,0]`.
*   **Zone Beta (Stress Test Sandbox)**: Compares `STRESS_TEST_QUERY` vector against the Master Baseline using $D_n$.
*   **Firewall Logic Threshold ($D_{fire}$)**: If distance to `STRESS` $\ge D_{fire}$, HUD shifts to **BLOCKED**.

### Deep Observability & Telemetry
### Deep Observability & Telemetry
*   **Zero-Dependency Native HUD**: Telemetry overlay built built with `requestAnimationFrame` ensuring zero external profiling overhead. Reports active **FPS**, total **Nodes**, current **xStretch**, and total **SECTOR SIZE**.
*   **L2 Analysis Panel**: Upon click-to-inspecting a semantic thread, reveals the raw Euclidean Distance ($D_n$), live mathematical formulation `sqrt(sum((A_i - B_i)^2))`, and derived percentage confidence calculated as `1 / (1 + D_n)`.
    *   **Noise Delta Map**: Explicitly enumerates dimensions exhibiting high variance (`delta > 0.2`) relative to the Master Baseline.
*   **Infinite Visibility Render bounds**: Canvas camera Frustum is statically configured to `{ near: 1, far: 200000 }` to guarantee no thread dropout at x40 stretches.
*   **Dimension Probe (Crosshair)**: A fixed SVG crosshair mathematically intercepts the specific S-DNA array index (`i ∈ [0, 1023]`) from the camera's viewport orientation.
    *   Targets exact dimensional vectors revealing `DIM-ID`, and specifically shows **Dimensional Delta** between the baseline ($A_i$) and the hovered S-DNA thread ($B_i$) along with the `Abs Error`.
*   **Context Injector API**: Integrated lateral modal allowing raw text parsing (`term: definition` formats) streamed directly into the `/corpus/inject-pack` LanceDB backend.