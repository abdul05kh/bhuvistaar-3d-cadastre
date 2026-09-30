# BhuVistaar — Judge Demonstration Guide

This guide is designed for technical presenters demonstrating BhuVistaar to Smart India Hackathon judges.

---

## 1. Quick Demo Setup & Reset

Before beginning the demonstration, ensure the system is in a clean baseline state:
1. Open the UI at `http://localhost:5173`.
2. Click **Reset Demo** in the top navigation bar or select **1. VRT-003 Overlap (Flagship)** from the Field Simulation dropdown.
3. Verify that:
   - Parent ULPIN `12345678901234` is loaded.
   - Floor units B01, G00, L01, L02 are visible in the 3D viewer.
   - The red conflict box highlights the 0.50m collision between L01 and L02.
   - The status banner displays `1 BLOCKER (VRT-003)`.

---

## 2. Navigating the 3 Demonstration Modes

### Mode A: 3-Minute Golden Walkthrough (Recommended)
- Click **30s Tour** for an executive visual summary.
- Follow the 10 sequential steps in the top `DemoScenarioBar`.
- Turn on **Presenter Cue** to display the cue card:
  - *What you are seeing*
  - *Why it matters to judges*
  - *Recommended next action*

### Mode B: Technical Deep Dive
- Click **Why? FAQ** to answer fundamental architecture questions (*Why 3D? Why VUID? Why AI?*).
- Click **System Readiness** to show live container health probes, PostGIS connectivity, and the non-destructive data integrity audit.
- Open bottom tabs:
  - `Disagreements`: Show Case A (`AI_VALIDATION_DISAGREEMENT`).
  - `Validation`: Show exact fact-grounded breakdown (-0.50m gap vs -0.001m tolerance).
  - `Evidence Triad`: Side-by-side comparison of Total Station survey vs Architectural elevation vs 3D model.
  - `Audit Timeline`: Show append-only event stream with correlation IDs.

### Mode C: Field Simulation & Recovery
- Select from the Field Simulation dropdown:
  - `ai_unavailable`: Demonstrate that validation, human review, and governance continue when AI is offline.
  - `stale_evidence`: Show that mutating an evidence file marks existing candidates as `STALE_EVIDENCE`.
  - `failure_recovery`: Demonstrate network upload interruption and clean resume without duplicate record creation.
