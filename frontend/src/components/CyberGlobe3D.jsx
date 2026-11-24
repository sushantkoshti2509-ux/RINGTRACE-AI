import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { ShieldCheck, Activity, Globe, RefreshCw, Zap, Building2 } from 'lucide-react';

export default function CyberGlobe3D() {
  const mountRef = useRef(null);
  const [activeBank, setActiveBank] = useState('ALL_BANKS');
  const activeBankRef = useRef(activeBank);
  const [pulseCount, setPulseCount] = useState(1420);
  const [isRotating, setIsRotating] = useState(true);

  useEffect(() => {
    activeBankRef.current = activeBank;
  }, [activeBank]);

  useEffect(() => {
    const currentMount = mountRef.current;
    if (!currentMount) return;

    // Scene, Camera, Renderer
    const width = currentMount.clientWidth || 600;
    const height = currentMount.clientHeight || 520;
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x070b14, 0.0015);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 78);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.domElement.style.display = 'block';
    renderer.domElement.style.margin = 'auto';
    currentMount.appendChild(renderer.domElement);

    // Root Group for rotation
    const globeGroup = new THREE.Group();
    scene.add(globeGroup);

    // 1. Core Wireframe Sphere
    const sphereRadius = 24;
    const sphereGeo = new THREE.SphereGeometry(sphereRadius, 32, 32);
    const sphereMat = new THREE.MeshBasicMaterial({
      color: 0x06b6d4,
      wireframe: true,
      transparent: true,
      opacity: 0.28,
    });
    const sphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
    globeGroup.add(sphereMesh);

    // 2. Inner Glowing Core
    const innerGeo = new THREE.SphereGeometry(sphereRadius * 0.88, 24, 24);
    const innerMat = new THREE.MeshBasicMaterial({
      color: 0x0a1020,
      transparent: true,
      opacity: 0.95,
    });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    globeGroup.add(innerMesh);

    // 3. Surrounding Particle Cloud (Simulating Transaction Packets)
    const particleCount = 450;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const cCyan = new THREE.Color(0x06b6d4);
    const cEmerald = new THREE.Color(0x10b981);
    const cPurple = new THREE.Color(0xa855f7);
    const cRed = new THREE.Color(0xef4444);

    for (let i = 0; i < particleCount; i++) {
      const phi = Math.acos(-1 + (2 * i) / particleCount);
      const theta = Math.sqrt(particleCount * Math.PI) * phi;
      const r = sphereRadius + (Math.random() * 4 - 2);

      positions[i * 3] = r * Math.cos(theta) * Math.sin(phi);
      positions[i * 3 + 1] = r * Math.sin(theta) * Math.sin(phi);
      positions[i * 3 + 2] = r * Math.cos(phi);

      const chosenColor = Math.random() > 0.85 ? cRed : (i % 3 === 0 ? cCyan : (i % 3 === 1 ? cEmerald : cPurple));
      colors[i * 3] = chosenColor.r;
      colors[i * 3 + 1] = chosenColor.g;
      colors[i * 3 + 2] = chosenColor.b;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const particleMat = new THREE.PointsMaterial({
      size: 1.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
    });
    const pointsMesh = new THREE.Points(particleGeo, particleMat);
    globeGroup.add(pointsMesh);

    // 4. Inter-Bank Gateway Hubs (4 Synthetic Institutions + Central Switch)
    const bankNodes = [
      { name: 'Bank A', code: 'BANK_A', pos: new THREE.Vector3(18, 12, 14), color: 0x06b6d4, role: 'Primary Settlement Gateway' },
      { name: 'Bank B', code: 'BANK_B', pos: new THREE.Vector3(-19, 8, 12), color: 0x10b981, role: 'Commercial Clearing Node' },
      { name: 'Bank C', code: 'BANK_C', pos: new THREE.Vector3(2, -18, 15), color: 0xa855f7, role: 'Cooperative Settlement Hub' },
      { name: 'Bank D', code: 'BANK_D', pos: new THREE.Vector3(-14, -14, 14), color: 0xf59e0b, role: 'Federal Retail Gateway' },
      { name: 'Central Switch', code: 'SWITCH', pos: new THREE.Vector3(0, 0, 26), color: 0xfacc15, role: 'Central Clearing & Oversight Switch' },
    ];

    const bankMeshList = [];
    bankNodes.forEach((b, idx) => {
      const nodeGeo = new THREE.SphereGeometry(1.6, 16, 16);
      const nodeMat = new THREE.MeshBasicMaterial({ color: b.color });
      const nodeMesh = new THREE.Mesh(nodeGeo, nodeMat);
      nodeMesh.position.copy(b.pos);
      globeGroup.add(nodeMesh);

      // Pulsing halo ring around each gateway
      const ringGeo = new THREE.RingGeometry(2.2, 2.7, 32);
      const ringMat = new THREE.MeshBasicMaterial({
        color: b.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.6,
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.position.copy(b.pos);
      ringMesh.lookAt(0, 0, 0);
      globeGroup.add(ringMesh);
      bankMeshList.push({ mesh: nodeMesh, ring: ringMesh, code: b.code, idx });
    });

    // 5. 3D Inter-Bank Transaction Arcs
    const createArc = (startVec, endVec, colorHex, sourceBank, targetBank) => {
      const mid = new THREE.Vector3().addVectors(startVec, endVec).multiplyScalar(0.5);
      const distance = startVec.distanceTo(endVec);
      mid.normalize().multiplyScalar(sphereRadius + distance * 0.35);

      const curve = new THREE.QuadraticBezierCurve3(startVec, mid, endVec);
      const points = curve.getPoints(40);
      const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
      const lineMat = new THREE.LineBasicMaterial({
        color: colorHex,
        transparent: true,
        opacity: 0.55,
      });
      const lineMesh = new THREE.Line(lineGeo, lineMat);
      globeGroup.add(lineMesh);
      return { curve, lineMesh, sourceBank, targetBank };
    };

    const arcs = [
      // 4-Bank Primary Cycle (Ground-Truth Mule Loop Topology)
      createArc(bankNodes[0].pos, bankNodes[1].pos, 0xef4444, 'BANK_A', 'BANK_B'), // A -> B
      createArc(bankNodes[1].pos, bankNodes[2].pos, 0xef4444, 'BANK_B', 'BANK_C'), // B -> C
      createArc(bankNodes[2].pos, bankNodes[3].pos, 0xef4444, 'BANK_C', 'BANK_D'), // C -> D
      createArc(bankNodes[3].pos, bankNodes[0].pos, 0xef4444, 'BANK_D', 'BANK_A'), // D -> A return loop

      // Central Switch Remittance Lines (Gold)
      createArc(bankNodes[0].pos, bankNodes[4].pos, 0xfacc15, 'BANK_A', 'SWITCH'), // A -> Central
      createArc(bankNodes[1].pos, bankNodes[4].pos, 0xfacc15, 'BANK_B', 'SWITCH'), // B -> Central
      createArc(bankNodes[2].pos, bankNodes[4].pos, 0xfacc15, 'BANK_C', 'SWITCH'), // C -> Central
      createArc(bankNodes[3].pos, bankNodes[4].pos, 0xfacc15, 'BANK_D', 'SWITCH'), // D -> Central
    ];

    // Pulsing packet traveling along arcs
    const packetGeo = new THREE.SphereGeometry(0.7, 8, 8);
    const packetMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const packets = arcs.map(arc => {
      const pMesh = new THREE.Mesh(packetGeo, packetMat);
      globeGroup.add(pMesh);
      return { mesh: pMesh, curve: arc.curve, progress: Math.random() };
    });

    // 6. Interactive Drag Controls
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };

    const onMouseDown = (e) => {
      isDragging = true;
      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e) => {
      if (!isDragging) return;
      const deltaX = e.clientX - previousMousePosition.x;
      const deltaY = e.clientY - previousMousePosition.y;

      globeGroup.rotation.y += deltaX * 0.006;
      globeGroup.rotation.x += deltaY * 0.006;

      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    currentMount.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);

    // Resize Handler with ResizeObserver to ensure centered alignment across all tabs and window sizes
    const handleResize = () => {
      if (!currentMount) return;
      const w = currentMount.clientWidth;
      const h = currentMount.clientHeight;
      if (w === 0 || h === 0) return;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      camera.position.set(0, 0, 78);
      camera.lookAt(0, 0, 0);
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    const resizeObserver = new ResizeObserver(() => {
      handleResize();
    });
    resizeObserver.observe(currentMount);

    // Animation Loop
    let animationFrameId;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const time = clock.getElapsedTime();

      // Gentle auto-rotation when not dragging
      if (!isDragging && isRotating) {
        globeGroup.rotation.y += 0.004;
      }

      // Pulse halos and highlight active bank
      const currentActive = activeBankRef.current;
      bankMeshList.forEach((item) => {
        const isMatch = currentActive === 'ALL_BANKS' || item.code === currentActive;
        const scaleBase = isMatch ? 1.0 : 0.65;
        const opacityBase = isMatch ? 0.75 : 0.2;
        const scale = scaleBase + (isMatch ? 0.2 : 0.05) * Math.sin(time * 3 + item.idx);
        item.ring.scale.set(scale, scale, scale);
        item.ring.material.opacity = opacityBase;
      });

      // Highlight active arcs
      arcs.forEach((arc) => {
        const isMatch = currentActive === 'ALL_BANKS' || arc.sourceBank === currentActive || arc.targetBank === currentActive;
        arc.lineMesh.material.opacity = isMatch ? 0.55 : 0.12;
      });

      // Move packets along curves
      packets.forEach(p => {
        p.progress += delta * 0.45;
        if (p.progress > 1) p.progress = 0;
        const pt = p.curve.getPoint(p.progress);
        p.mesh.position.copy(pt);
      });

      renderer.render(scene, camera);
    };

    animate();

    // Pulse counter updater
    const interval = setInterval(() => {
      setPulseCount(prev => prev + Math.floor(Math.random() * 8) + 2);
    }, 1500);

    return () => {
      clearInterval(interval);
      cancelAnimationFrame(animationFrameId);
      currentMount.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      window.removeEventListener('resize', handleResize);
      resizeObserver.disconnect();
      if (currentMount.contains(renderer.domElement)) {
        currentMount.removeChild(renderer.domElement);
      }
      scene.clear();
      renderer.dispose();
    };
  }, [isRotating]);

  return (
    <div className="flex flex-col gap-6">
      {/* Top Header Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 shrink-0">
            <Globe className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-extrabold text-slate-900 tracking-tight">
                3D Multi-Bank Cyber Clearing Fabric
              </h2>
              <span className="bg-blue-50 text-blue-700 border border-blue-200 font-extrabold text-[10px] px-2 py-0.5 rounded-full font-mono">
                WEBGL RADAR
              </span>
            </div>
            <p className="text-xs text-slate-600 font-semibold mt-0.5">
              Spatial visualization of inter-bank settlement rails, multi-hop routing, and synthetic mule rings
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Institution Filter Dropdown */}
          <select
            value={activeBank}
            onChange={(e) => setActiveBank(e.target.value)}
            className="px-3.5 py-2 text-xs rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-900 border border-slate-300 font-mono font-bold focus:outline-none focus:border-blue-600 shadow-xs cursor-pointer"
          >
            <option value="ALL_BANKS">All Institutions (4 Banks + Central)</option>
            <option value="BANK_A">Bank A (Primary Switch)</option>
            <option value="BANK_B">Bank B (Commercial Node)</option>
            <option value="BANK_C">Bank C (Cooperative Node)</option>
            <option value="BANK_D">Bank D (Federal Node)</option>
            <option value="SWITCH">Central Clearing Switch</option>
          </select>

          <button
            onClick={() => setIsRotating(!isRotating)}
            className="px-4 py-2 text-xs font-extrabold rounded-xl bg-white hover:bg-slate-50 text-slate-700 hover:text-slate-900 border border-slate-300 shadow-xs flex items-center gap-2 transition-all cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRotating ? 'animate-spin text-blue-600' : ''}`} />
            <span>{isRotating ? 'Pause Orbit' : 'Resume Orbit'}</span>
          </button>
        </div>
      </div>

      {/* 4-Bank + Central Switch Filter Pills */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          { code: 'BANK_A', name: 'Bank A', role: 'Primary Switch', color: '#0284c7', bg: 'bg-blue-50/70 border-blue-200 text-blue-950' },
          { code: 'BANK_B', name: 'Bank B', role: 'Commercial Gateway', color: '#059669', bg: 'bg-emerald-50/70 border-emerald-200 text-emerald-950' },
          { code: 'BANK_C', name: 'Bank C', role: 'Cooperative Hub', color: '#7c3aed', bg: 'bg-purple-50/70 border-purple-200 text-purple-950' },
          { code: 'BANK_D', name: 'Bank D', role: 'Federal Gateway', color: '#d97706', bg: 'bg-amber-50/70 border-amber-200 text-amber-950' },
          { code: 'SWITCH', name: 'Central Switch', role: 'Clearing Overseer', color: '#4f46e5', bg: 'bg-indigo-50/70 border-indigo-200 text-indigo-950' },
        ].map((b) => {
          const isSelected = activeBank === b.code || activeBank === 'ALL_BANKS';
          return (
            <div
              key={b.code}
              onClick={() => setActiveBank(activeBank === b.code ? 'ALL_BANKS' : b.code)}
              className={`p-3.5 rounded-xl border-2 transition-all cursor-pointer shadow-xs flex items-center justify-between ${b.bg} ${activeBank === b.code ? 'ring-2 ring-blue-500 shadow-md' : 'opacity-90 hover:opacity-100'
                }`}
            >
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: b.color }} />
                <div>
                  <span className="font-extrabold text-xs block">{b.name}</span>
                  <span className="text-[10px] text-slate-600 font-semibold">{b.role}</span>
                </div>
              </div>
              <span className="text-[10px] font-mono font-extrabold px-1.5 py-0.5 rounded bg-white/80 border border-slate-300 text-slate-800">
                {activeBank === b.code ? 'FOCUSED' : 'ACTIVE'}
              </span>
            </div>
          );
        })}
      </div>

      {/* 3D Canvas Box - Centered Sphere Viewport */}
      <div className="relative w-full h-[540px] rounded-2xl overflow-hidden bg-gradient-to-b from-[#090e1a] via-[#070b14] to-[#040711] border border-slate-800 shadow-xl flex items-center justify-center">
        {/* Subtle Canvas Watermark Tag */}
        <div className="absolute top-4 left-5 z-10 pointer-events-none">
          <span className="text-[11px] font-mono font-extrabold text-cyan-400/90 bg-cyan-950/60 border border-cyan-500/30 px-3 py-1 rounded-lg backdrop-blur-md">
            INTERACTIVE 3D CLEARING SPHERE • DRAG TO ROTATE
          </span>
        </div>

        {/* 3D Canvas Mount Point */}
        <div ref={mountRef} className="w-full h-full cursor-grab active:cursor-grabbing flex items-center justify-center" />
      </div>

      {/* Bottom Telemetry HUD Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <div className="text-xs text-slate-600 font-extrabold uppercase tracking-wider flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <span>Security Grid</span>
          </div>
          <div className="text-xl font-extrabold text-slate-900 font-mono mt-2">Dual-Bank Active</div>
          <div className="text-xs text-emerald-700 font-bold mt-1">100% Zero Unilateral Freeze</div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <div className="text-xs text-slate-600 font-extrabold uppercase tracking-wider flex items-center gap-1.5">
            <Zap className="w-4 h-4 text-amber-500" />
            <span>Monitored Gateways</span>
          </div>
          <div className="text-xl font-extrabold text-slate-900 font-mono mt-2">4 Banks + Switch</div>
          <div className="text-xs text-blue-700 font-bold mt-1">Bank A, Bank B, Bank C, Bank D</div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <div className="text-xs text-slate-600 font-extrabold uppercase tracking-wider flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-emerald-600" />
            <span>Ring Interception</span>
          </div>
          <div className="text-xl font-extrabold text-slate-900 font-mono mt-2">33 Mule Rings</div>
          <div className="text-xs text-emerald-700 font-bold mt-1">100% Ground-Truth Recall</div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between">
          <div className="text-xs text-slate-600 font-extrabold uppercase tracking-wider flex items-center gap-1.5">
            <Globe className="w-4 h-4 text-purple-600" />
            <span>Volume & Pulses</span>
          </div>
          <div className="text-xl font-extrabold text-slate-900 font-mono mt-2">
            ₹8.04 Cr <span className="text-xs text-slate-500 font-normal">({pulseCount.toLocaleString()} pkts)</span>
          </div>
          <div className="text-xs text-slate-600 font-bold mt-1">27,743 Reconciled Txns</div>
        </div>
      </div>
    </div>
  );
}
