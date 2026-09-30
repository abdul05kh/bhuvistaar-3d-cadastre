import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Eye, Layers, Maximize2, RotateCcw, AlertTriangle, Box } from 'lucide-react';
import { ParentParcel, SpatialUnit } from '../../types';

interface Cadastral3DViewerProps {
  parcel: ParentParcel | null;
  units: SpatialUnit[];
  aiCandidates?: any[];
  selectedUnitId: string | null;
  selectedCandidateId?: string | null;
  onSelectUnit: (unitId: string) => void;
  onSelectCandidate?: (candidateId: string) => void;
  hasOverlapDefect: boolean;
  overlapElevationRange?: { min: number; max: number };
}

export const Cadastral3DViewer: React.FC<Cadastral3DViewerProps> = ({
  parcel,
  units,
  aiCandidates = [],
  selectedUnitId,
  selectedCandidateId = null,
  onSelectUnit,
  onSelectCandidate,
  hasOverlapDefect,
  overlapElevationRange = { min: 106.0, max: 106.5 },
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const meshMapRef = useRef<Map<string, THREE.Mesh>>(new Map());

  // Viewer options
  const [isExploded, setIsExploded] = useState(false);
  const [showWireframe, setShowWireframe] = useState(false);
  const [showOverlapMesh, setShowOverlapMesh] = useState(true);
  const [isolatedUnitId, setIsolatedUnitId] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x070d1a);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(45, 35, 55);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Ambient & Directional Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight1.position.set(50, 80, 50);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x94a3b8, 0.6);
    dirLight2.position.set(-50, -40, -50);
    scene.add(dirLight2);

    // Ground Grid & Helpers
    const grid = new THREE.GridHelper(80, 40, 0x223249, 0x162338);
    grid.position.y = -0.05;
    scene.add(grid);

    // Simple Orbit Controls implementation without external addon
    let isDragging = false;
    let isPanning = false;
    let prevMouseX = 0;
    let prevMouseY = 0;
    let spherical = new THREE.Spherical().setFromVector3(camera.position);
    let target = new THREE.Vector3(0, 5, 0);

    const onMouseDown = (e: MouseEvent) => {
      if (e.button === 0) isDragging = true;
      if (e.button === 2) isPanning = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const onMouseMove = (e: MouseEvent) => {
      const deltaX = e.clientX - prevMouseX;
      const deltaY = e.clientY - prevMouseY;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;

      if (isDragging) {
        spherical.theta -= deltaX * 0.007;
        spherical.phi = Math.max(0.1, Math.min(Math.PI / 2 - 0.05, spherical.phi - deltaY * 0.007));
        camera.position.setFromSpherical(spherical).add(target);
        camera.lookAt(target);
      } else if (isPanning) {
        const right = new THREE.Vector3();
        camera.getWorldDirection(right);
        right.cross(camera.up).normalize();
        target.addScaledVector(right, -deltaX * 0.05);
        target.y += deltaY * 0.05;
        camera.position.setFromSpherical(spherical).add(target);
        camera.lookAt(target);
      }
    };

    const onMouseUp = () => {
      isDragging = false;
      isPanning = false;
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      spherical.radius = Math.max(10, Math.min(180, spherical.radius + e.deltaY * 0.05));
      camera.position.setFromSpherical(spherical).add(target);
      camera.lookAt(target);
    };

    // Raycaster for selecting units
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onClick = (e: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const meshes: THREE.Mesh[] = Array.from(meshMapRef.current.values());
      const intersects = raycaster.intersectObjects(meshes);

      if (intersects.length > 0) {
        const clickedMesh = intersects[0].object as THREE.Mesh;
        for (const [id, mesh] of meshMapRef.current.entries()) {
          if (mesh === clickedMesh || mesh.children.includes(clickedMesh)) {
            if (id.startsWith('cand_')) {
              onSelectCandidate?.(id.replace('cand_', ''));
            } else {
              onSelectUnit(id);
            }
            break;
          }
        }
      }
    };

    const domElement = renderer.domElement;
    domElement.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    domElement.addEventListener('wheel', onWheel, { passive: false });
    domElement.addEventListener('click', onClick);
    domElement.addEventListener('contextmenu', (e) => e.preventDefault());

    // Resize
    const handleResize = () => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    // Animation Loop
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(animId);
      domElement.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      domElement.removeEventListener('wheel', onWheel);
      domElement.removeEventListener('click', onClick);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, []);

  // Update Geometry and Scene Elements when data changes
  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene) return;

    // Clear previous geometry meshes (keep lights & grid)
    const objectsToRemove: THREE.Object3D[] = [];
    scene.traverse((obj) => {
      if (obj.name && (obj.name.startsWith('unit_') || obj.name.startsWith('parcel_') || obj.name.startsWith('ai_candidate_') || obj.name === 'overlap_box')) {
        objectsToRemove.push(obj);
      }
    });
    objectsToRemove.forEach((obj) => scene.remove(obj));
    meshMapRef.current.clear();

    if (!parcel) return;

    // Calculate Parcel Centroid for centering the local scene
    const parcelCoords = parcel.geometry.coordinates[0];
    let sumX = 0;
    let sumY = 0;
    const n = parcelCoords.length - 1; // last point equals first
    for (let i = 0; i < n; i++) {
      sumX += parcelCoords[i][0];
      sumY += parcelCoords[i][1];
    }
    const originX = sumX / n;
    const originY = sumY / n;

    // 1. Render Parcel Boundary
    const parcelShape = new THREE.Shape();
    parcelCoords.forEach((pt, i) => {
      const localX = pt[0] - originX;
      const localZ = pt[1] - originY;
      if (i === 0) parcelShape.moveTo(localX, localZ);
      else parcelShape.lineTo(localX, localZ);
    });

    const parcelPoints = parcelShape.getPoints();
    const parcelGeometry = new THREE.BufferGeometry().setFromPoints(
      parcelPoints.map((p) => new THREE.Vector3(p.x, 0.05, -p.y))
    );
    const parcelLine = new THREE.LineLoop(
      parcelGeometry,
      new THREE.LineDashedMaterial({ color: 0xeab308, dashSize: 2, gapSize: 1, linewidth: 2 })
    );
    parcelLine.computeLineDistances();
    parcelLine.name = 'parcel_boundary';
    scene.add(parcelLine);

    // 2. Render Spatial Units (3D Floor Prisms)
    const baseElevation = 100.0; // Normalized ground datum elevation

    units.forEach((u, index) => {
      if (isolatedUnitId && isolatedUnitId !== u.id) return;

      const footprintCoords = u.footprint_geom.coordinates[0];
      const unitShape = new THREE.Shape();
      footprintCoords.forEach((pt, i) => {
        const localX = pt[0] - originX;
        const localZ = pt[1] - originY;
        if (i === 0) unitShape.moveTo(localX, localZ);
        else unitShape.lineTo(localX, localZ);
      });

      const floorHeight = Math.max(0.1, u.z_max - u.z_min);
      const extrudeSettings = {
        depth: floorHeight,
        bevelEnabled: false,
      };

      const geom = new THREE.ExtrudeGeometry(unitShape, extrudeSettings);
      geom.rotateX(Math.PI / 2); // Orient extrusion vertically (Y up)

      const isSelected = u.id === selectedUnitId;
      const isL01 = u.level_code === 'L01';
      const isL02 = u.level_code === 'L02';
      const isConflicting = hasOverlapDefect && (isL01 || isL02);

      // Color scheme based on status and selection
      let colorHex = 0x3b82f6; // default blue
      if (u.level_code === 'B1') colorHex = 0x475569; // basement slate
      else if (u.level_code === 'G') colorHex = 0x0284c7; // ground ocean
      else if (isL01) colorHex = isConflicting ? 0xf97316 : 0x0ea5e9; // orange if defect
      else if (isL02) colorHex = isConflicting ? 0xef4444 : 0x10b981; // red if defect

      if (isSelected) colorHex = 0x60a5fa; // bright highlight

      const mat = new THREE.MeshStandardMaterial({
        color: colorHex,
        roughness: 0.35,
        metalness: 0.15,
        wireframe: showWireframe,
        transparent: true,
        opacity: isSelected ? 0.95 : isConflicting ? 0.75 : 0.85,
      });

      const mesh = new THREE.Mesh(geom, mat);

      // Vertical positioning
      let yPos = u.z_min - baseElevation;
      if (isExploded) {
        yPos += index * 3.5; // Separate floors vertically by 3.5m
      }
      mesh.position.y = yPos;
      mesh.name = `unit_${u.id}`;

      // Add CAD edges outline
      const edges = new THREE.EdgesGeometry(geom);
      const edgeLine = new THREE.LineSegments(
        edges,
        new THREE.LineBasicMaterial({
          color: isSelected ? 0xffffff : isConflicting ? 0xff4444 : 0x1e293b,
          linewidth: isSelected ? 2 : 1,
        })
      );
      mesh.add(edgeLine);

      scene.add(mesh);
      meshMapRef.current.set(u.id, mesh);
    });

    // 3. Render 3D Conflict Overlap Zone (VRT-003 Translucent Box)
    if (hasOverlapDefect && showOverlapMesh && !isolatedUnitId) {
      const overlapHeight = overlapElevationRange.max - overlapElevationRange.min; // 0.50m
      if (overlapHeight > 0) {
        // Use building dimensions 24m x 18m centered around footprint
        const overlapGeom = new THREE.BoxGeometry(24.4, overlapHeight, 18.4);
        const overlapMat = new THREE.MeshStandardMaterial({
          color: 0xff0033,
          transparent: true,
          opacity: 0.65,
          emissive: 0xcc0000,
          emissiveIntensity: 0.5,
        });

        const overlapMesh = new THREE.Mesh(overlapGeom, overlapMat);
        // Position at overlap altitude [106.0m -> 106.5m] -> middle is 106.25m
        let overlapY = overlapElevationRange.min - baseElevation + overlapHeight / 2;
        if (isExploded) {
          overlapY += 2 * 3.5;
        }
        overlapMesh.position.set(0, overlapY, 0);
        overlapMesh.name = 'overlap_box';

        // Add warning wireframe box
        const wireGeom = new THREE.EdgesGeometry(overlapGeom);
        const wireMat = new THREE.LineBasicMaterial({ color: 0xffffff, linewidth: 2 });
        overlapMesh.add(new THREE.LineSegments(wireGeom, wireMat));

        scene.add(overlapMesh);
      }
    }

    // 4. Render AI Candidate Proposals (Translucent Cyan/Amber Prisms with Dashed Outlines)
    if (aiCandidates && aiCandidates.length > 0) {
      aiCandidates.forEach((cand, idx) => {
        if (!cand.footprint_geojson || !cand.footprint_geojson.coordinates) return;
        const footprintCoords = cand.footprint_geojson.coordinates[0];
        const candShape = new THREE.Shape();
        footprintCoords.forEach((pt: number[], i: number) => {
          const localX = pt[0] - originX;
          const localZ = pt[1] - originY;
          if (i === 0) candShape.moveTo(localX, localZ);
          else candShape.lineTo(localX, localZ);
        });

        const floorHeight = Math.max(0.1, cand.z_max - cand.z_min);
        const extrudeSettings = {
          depth: floorHeight,
          bevelEnabled: false,
        };

        const geom = new THREE.ExtrudeGeometry(candShape, extrudeSettings);
        geom.rotateX(Math.PI / 2);

        const isSelected = cand.candidate_id === selectedCandidateId;
        const isAccepted = cand.status === 'ACCEPTED';
        const isRejected = cand.status === 'REJECTED';

        let candColor = 0x06b6d4; // cyan proposal
        if (cand.confidence_band === 'LOW') candColor = 0xf43f5e; // red/low confidence
        if (isSelected) candColor = 0x38bdf8; // bright highlight
        if (isAccepted) candColor = 0x10b981; // emerald
        if (isRejected) candColor = 0x64748b; // slate

        const mat = new THREE.MeshStandardMaterial({
          color: candColor,
          roughness: 0.25,
          metalness: 0.1,
          transparent: true,
          opacity: isSelected ? 0.65 : 0.40,
          wireframe: showWireframe,
        });

        const mesh = new THREE.Mesh(geom, mat);
        let yPos = cand.z_min - baseElevation;
        if (isExploded) {
          yPos += (idx + units.length) * 3.5;
        }
        mesh.position.set(0, yPos, 0);

        // Dashed wireframe edges for AI candidate
        const edges = new THREE.EdgesGeometry(geom);
        const wire = new THREE.LineSegments(
          edges,
          new THREE.LineDashedMaterial({ color: isSelected ? 0x67e8f9 : 0x22d3ee, dashSize: 1, gapSize: 0.5 })
        );
        wire.computeLineDistances();
        mesh.add(wire);

        mesh.name = `ai_candidate_${cand.candidate_id}`;
        scene.add(mesh);
        meshMapRef.current.set(`cand_${cand.candidate_id}`, mesh);
      });
    }
  }, [parcel, units, aiCandidates, selectedUnitId, selectedCandidateId, isExploded, showWireframe, showOverlapMesh, isolatedUnitId, hasOverlapDefect]);

  // Camera presets
  const handleResetCamera = () => {
    if (!cameraRef.current) return;
    cameraRef.current.position.set(45, 35, 55);
    cameraRef.current.lookAt(0, 5, 0);
  };

  const handleTopView = () => {
    if (!cameraRef.current) return;
    cameraRef.current.position.set(0, 90, 0.1);
    cameraRef.current.lookAt(0, 0, 0);
  };

  const handleIsoView = () => {
    if (!cameraRef.current) return;
    cameraRef.current.position.set(40, 40, 40);
    cameraRef.current.lookAt(0, 5, 0);
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden' }}>
      {/* 3D Canvas */}
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

      {/* Floating Toolbar */}
      <div
        style={{
          position: 'absolute',
          top: '12px',
          left: '14px',
          display: 'flex',
          gap: '6px',
          backgroundColor: 'rgba(14, 23, 38, 0.85)',
          padding: '4px 6px',
          borderRadius: '6px',
          border: '1px solid var(--border-subtle)',
          backdropFilter: 'blur(4px)',
          zIndex: 10,
        }}
      >
        <button className="btn btn-sm" onClick={handleResetCamera} title="Reset Camera Perspective">
          <RotateCcw size={12} />
          Reset
        </button>
        <button className="btn btn-sm" onClick={handleTopView} title="2D Top-Down View (Cadastral Plan)">
          Plan 2D
        </button>
        <button className="btn btn-sm" onClick={handleIsoView} title="Isometric View">
          Iso 3D
        </button>
        <div style={{ width: '1px', backgroundColor: 'var(--border-subtle)', margin: '0 4px' }} />
        <button
          className={`btn btn-sm ${isExploded ? 'btn-primary' : ''}`}
          onClick={() => setIsExploded(!isExploded)}
          title="Explode floor intervals vertically for clear ceiling/floor inspection"
        >
          <Layers size={12} />
          {isExploded ? 'Collapse' : 'Explode'}
        </button>
        <button
          className={`btn btn-sm ${showWireframe ? 'btn-primary' : ''}`}
          onClick={() => setShowWireframe(!showWireframe)}
          title="Toggle Wireframe mode"
        >
          <Box size={12} />
          Wireframe
        </button>
        {selectedUnitId && (
          <button
            className={`btn btn-sm ${isolatedUnitId ? 'btn-warning' : ''}`}
            onClick={() => setIsolatedUnitId(isolatedUnitId ? null : selectedUnitId)}
            title="Isolate current selected unit"
          >
            <Maximize2 size={12} />
            {isolatedUnitId ? 'Show All' : 'Isolate'}
          </button>
        )}
      </div>

      {/* Conflict Legend / Warning Banner */}
      {hasOverlapDefect && (
        <div
          style={{
            position: 'absolute',
            bottom: '16px',
            left: '16px',
            backgroundColor: 'rgba(239, 68, 68, 0.9)',
            color: '#ffffff',
            padding: '8px 14px',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            boxShadow: '0 4px 12px rgba(239, 68, 68, 0.4)',
            fontSize: '12px',
            fontWeight: 600,
            zIndex: 10,
          }}
        >
          <AlertTriangle size={16} />
          <div>
            <div>VRT-003 BLOCKER DETECTED</div>
            <div style={{ fontSize: '11px', fontWeight: 400, opacity: 0.95 }}>
              0.50m collision between L01 (ceil 106.50m) and L02 (floor 106.00m)
            </div>
          </div>
          <button
            className="btn btn-sm"
            style={{ backgroundColor: 'rgba(0,0,0,0.3)', color: '#fff', border: 'none', marginLeft: '6px' }}
            onClick={() => setShowOverlapMesh(!showOverlapMesh)}
          >
            {showOverlapMesh ? 'Hide Mesh' : 'Show Mesh'}
          </button>
        </div>
      )}

      {/* Multi-Layer Cadastral & Height Legend */}
      <div
        style={{
          position: 'absolute',
          top: '12px',
          right: '14px',
          backgroundColor: 'rgba(10, 18, 30, 0.9)',
          padding: '8px 14px',
          borderRadius: '8px',
          border: '1px solid #1e3a5f',
          fontSize: '11px',
          color: 'var(--text-secondary)',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          zIndex: 10,
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
        }}
      >
        <div>
          <span style={{ fontWeight: 700, color: '#f8fafc', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            3D Semantic Layers
          </span>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '3px', marginTop: '4px', fontSize: '10px' }}>
            <span style={{ color: '#38bdf8' }}>⬚ PARCEL: 2D Ground Boundary</span>
            <span style={{ color: '#60a5fa' }}>🏢 GOVERNED UNIT: Extruded Prism</span>
            <span style={{ color: '#c084fc' }}>🤖 AI CANDIDATE: Advisory Proposal</span>
            <span style={{ color: '#f87171', fontWeight: 600 }}>⚠️ BLOCKER: VRT-003 Overlap</span>
            <span style={{ color: '#94a3b8' }}>✕ REJECTED: Inactive / Historical</span>
            <span style={{ color: '#fbbf24', fontWeight: 600 }}>★ SELECTED: Active Inspector</span>
          </div>
        </div>

        <div style={{ borderTop: '1px solid #1e293b', paddingTop: '6px' }}>
          <span style={{ fontWeight: 700, color: '#f8fafc', fontSize: '10px', textTransform: 'uppercase' }}>
            Elevation Bounds (MSL)
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', marginTop: '3px', fontSize: '10px', fontFamily: 'monospace' }}>
            <span>L02: 106.00m - 109.00m</span>
            <span style={{ color: hasOverlapDefect ? '#f87171' : 'inherit', fontWeight: hasOverlapDefect ? 700 : 400 }}>
              L01: 103.00m - {hasOverlapDefect ? '106.50m (!)' : '106.00m'}
            </span>
            <span>G00: 100.00m - 103.00m</span>
            <span>B01:  97.00m - 100.00m</span>
          </div>
        </div>
      </div>
    </div>
  );
};
