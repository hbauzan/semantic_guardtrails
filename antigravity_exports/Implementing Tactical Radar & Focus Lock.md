# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

# SSA PROTOCOL V12: TACTICAL STABILIZATION & RADIAL RADAR

## ROLE & MISSION
**Role:** Senior IT Architect / Visual Computing Lead.
**Mission:** Eliminate `SecurityError` console spam, stabilize input focus mechanics, refactor the Auto-Fit camera for 1024D deterministic behavior, and replace the legacy 3D compass with a tactical 2D SVG Radial Radar.

## 1. INTERACTION & FOCUS STABILIZATION (Zero-Friction Inputs)
*   **State Management:** In `ArithmeticHUD.tsx`, implement a global or local `isTyping` boolean state.
*   **Focus Logic:** 
    *   Set `isTyping` to `true` on `onFocus` and `false` on `onBlur` for ALL input fields (Master Baseline, Stress Test Query, Context Injector, etc.).
*   **Surgical PointerLock:** 
    *   Bind the `enabled` prop of `<PointerLockControls>` to `!isTyping`.
    *   Ensure the canvas only requests pointer lock upon an explicit click on the empty Canvas area. 
    *   Implement a global event listener or wrapper to catch and suppress `SecurityError` exceptions related to `requestPointerLock` being called without a direct user gesture.

## 2. DETERMINISTIC AUTO-FIT (Camera Refactor)
*   **Bounding Geometry:** Refactor the `CameraAutoFit` component and the `calculate` function. Upon `EXECUTE AUDIT`, calculate a deterministic bounding radius (`maxRadius`) that encapsulates:
    1.  The Origin `[0,0,0]` (Master Baseline).
    2.  The furthest Stress Thread coordinate on the XZ plane.
    3.  The Firewall Tolerance Ring radius ($D_{fire}$).
*   **Framing Strategy:** Purge the generic lerp bounding box logic. Force the camera to a **Cenital View** (High Y-axis, looking down at the origin) with a calculated Z-offset to ensure the entire `maxRadius` fits perfectly within the frustum. 
    *   *Formula constraint:* The final position must be mathematically deterministic (e.g., `Y = maxRadius * 1.5`, `Z = maxRadius * 0.5`, looking at `[0,0,0]`). It must yield the exact same camera transform every time for the same $D_n$.

## 3. RADIAL RADAR (Tactical Minimap)
*   **Purge Legacy:** Delete the `CompassHUD` component (the 3 fixed 3D lines).
*   **Tactical Radar HUD:** Implement a 2D circular SVG overlay fixed at the bottom-right corner of the screen.
    *   **Center:** Represents `[0,0,0]` (Master Baseline).
    *   **Boundary Ring:** A red SVG circle representing the `firewallThreshold`.
    *   **Blips:** Render small SVG dots representing the Stress Test thread(s).
    *   **Telemetry:** Map the 3D world coordinates `(X, Z)` to the 2D SVG coordinates `(cx, cy)` using a fixed scale relative to the current `maxRadius`.

## 4. SCRIPT PIPELINE UPDATES
*   Update `run_server.sh` and `run_tests.sh` to ensure they properly clear any necessary caches and execute cleanly.
*   **Execution Mandate:** You must execute these scripts and verify the output until you confirm that the server runs without errors and all tests pass.

## 5. DOCUMENTATION & TESTING MANDATES (STRICT COMPLIANCE)
*   **Documentation Loop:** Every functional change MUST be accompanied by:
    1.  An update to `manifest.json` (setting features to `true`: `tactical_stabilization`, `radial_radar_hud`, `is_typing_focus_lock`, `deterministic_auto_fit`).
    2.  An update to `architecture_spec.md` reflecting the new logic (specifically updating Section 6 regarding the new deterministic Auto-Fit and the Radar system).
*   **Testing Sovereignty:** `backend/perform_tests.py` is the System Heartbeat.
    *   If a logic change requires a new validation, you must suggest the specific test function to add.
    *   *Requirement:* Suggest a test function to validate the deterministic math of the new Cenital Auto-Fit logic.

**OUTPUT FORMAT:** 
Provide the exact code modifications required, followed by the updated `manifest.json` and `architecture_spec.md` sections, and the new test function for `perform_tests.py`. All generated text and code MUST be in English.

*Edited relevant file*

*Grep searched codebase*

*Grep searched codebase*

*Grep searched codebase*

*Grep searched codebase*

*Viewed [ArithmeticHUD.tsx](file:///Users/hbauzan/treepwood/semantic_guardtrails/frontend/src/components/ArithmeticHUD.tsx) *

*Viewed [manifest.json](file:///Users/hbauzan/treepwood/semantic_guardtrails/manifest.json) *

*Viewed [architecture_spec.md](file:///Users/hbauzan/treepwood/semantic_guardtrails/architecture_spec.md) *

*Viewed [perform_tests.py](file:///Users/hbauzan/treepwood/semantic_guardtrails/backend/perform_tests.py) *

*Viewed [run_server.sh](file:///Users/hbauzan/treepwood/semantic_guardtrails/run_server.sh) *

*Viewed [run_tests.sh](file:///Users/hbauzan/treepwood/semantic_guardtrails/run_tests.sh) *

*Viewed [store.ts](file:///Users/hbauzan/treepwood/semantic_guardtrails/frontend/src/store.ts) *

*Edited relevant file*

### User Input

This is a system-generated message that is sent due to the user's review policy. Proceed with the decision that you think is the most optimal here.

*Edited relevant file*

*Edited relevant file*

*Viewed [App.tsx](file:///Users/hbauzan/treepwood/semantic_guardtrails/frontend/src/App.tsx) *

*Grep searched codebase*

*Grep searched codebase*

*Viewed [task.md](file:///Users/hbauzan/.gemini/antigravity/brain/33457a1e-03af-4fa7-8627-ae5b27805e03/task.md) *

*Edited relevant file*

*Edited relevant file*

*User accepted the command `npm run dev &`*

*Checked command status*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*User accepted the command `bash run_tests.sh`*

*Checked command status*

*Edited relevant file*