# BhuVistaar — 3D Cadastral Intelligence & Validation Platform

*Machine-assisted 3D Cadastral Extension & Validation Layer for SIH26011*  
**Built and Maintained by Team VoidBreakers**

---

> [!IMPORTANT]
> **PROTOTYPE STATUS & LEGAL DISCLAIMER**  
> BhuVistaar is an engineering prototype developed for Smart India Hackathon (SIH 2026) under Problem Statement `SIH26011` (Ministry of Rural Development / Department of Land Resources).  
> - BhuVistaar is **NOT** an official Government of India system.
> - BhuVistaar does **NOT** alter, mutate, or replace the official 14-digit ULPIN (Bhu-Aadhaar).
> - Prototype Volumetric Unique Identifiers (**VUID**) are prototype data-layer keys and are **NOT** official 3D ULPINs.
> - The platform performs deterministic geometric and vertical validation; it does **NOT** adjudicate legal land titles or ownership rights.
> - All officer authorization headers operate strictly in `SIMULATED_PROTOTYPE` mode.

---

## 🏛️ Problem Overview & Core Thesis
Conventional land records associate land rights to a flat 2D parcel polygon identified by a 14-digit **ULPIN**. However, vertical property strata—such as multi-storey apartments, basements, utility shafts, and elevated structures—cannot be disambiguated in 2D space without losing volumetric fidelity.

BhuVistaar introduces a structured machine-assisted layer that:
1. **Preserves the parent ULPIN** as the authoritative immutable cadastral root.
2. **Derives 3D spatial units** via deterministic extrusion and vertical stratification.
3. **Assigns deterministic prototype VUIDs** that are representation-invariant (independent of CAD drawing vertex order or polygon winding).
4. **Executes Gate A deterministic validation** (`GEO`, `VRT`, `TOP`, `ID`) to detect physical and cadastral inconsistencies (such as overlapping floor strata and boundary encroachments) prior to human review.
5. **Maintains unbroken provenance** linking each 3D spatial unit back to its underlying survey and architectural evidence.

---

## 🛠️ Technology Stack
- **Geospatial & Computational Geometry:** Shapely 2.0, PyProj 3.8, GeoAlchemy2, NumPy
- **Authoritative Spatial Database:** PostgreSQL 16 + PostGIS 3.4 (`EPSG:32643` canonical metric storage)
- **Backend API:** FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn
- **Quality Assurance & Verification:** Pytest, Hypothesis (property-based testing), HTTPX

---

## 🚀 Running Slice 1A Locally

### 1. Requirements
- Python 3.12+
- Docker & Docker Compose (for PostGIS spatial database)

### 2. Install Dependencies
```bash
py -3.12 -m pip install -e ".[dev]"
```

### 3. Launch PostGIS Database via Docker Compose
```bash
docker compose up -d db
```

### 4. Run the Full Test Suite
```bash
py -3.12 -m pytest tests/ -v
```

### 5. Launch the FastAPI Development Server
```bash
uvicorn backend.main:app --reload --port 8000
```
Interactive API documentation will be available at: `http://localhost:8000/docs`

---

## 👥 Contributors & Team Attribution
Refer to [CONTRIBUTORS.md](file:///d:/projects/BhuVistaar/CONTRIBUTORS.md) for core team members, role breakdowns, and multi-author commit attribution protocol.
