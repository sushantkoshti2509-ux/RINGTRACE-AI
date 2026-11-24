import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { ShieldCheck, Activity, Globe, RefreshCw, Zap } from 'lucide-react';

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
    const height = currentMount.clientHeight || 450;
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x070b14, 0.002);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 78);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
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
      createArc(bankNodes[0].pos, bankNodes[1].pos, 0x06b6d4, 'BANK_A', 'BANK_B'), // A -> B
      createArc(bankNodes[1].pos, bankNodes[2].pos, 0x10b981, 'BANK_B', 'BANK_C'), // B -> C
      createArc(bankNodes[2].pos, bankNodes[3].pos, 0xa855f7, 'BANK_C', 'BANK_D'), // C -> D
      createArc(bankNodes[3].pos, bankNodes[0].pos, 0xf59e0b, 'BANK_D', 'BANK_A'), // D -> A (Complete Cycle)
      // Cross-Bank Rapid Fan-Out & Splitter Arcs
      createArc(bankNodes[0].pos, bankNodes[2].pos, 0x06b6d4, 'BANK_A', 'BANK_C'), // A -> C
      createArc(bankNodes[1].pos, bankNodes[3].pos, 0x10b981, 'BANK_B', 'BANK_D'), // B -> D
      // Radial Clearing Links to Central Oversight Switch
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

    // Resize Handler
    const handleResize = () => {
      if (!currentMount) return;
      const w = currentMount.clientWidth;
      const h = currentMount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      camera.lookAt(0, 0, 0);
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

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
      if (currentMount.contains(renderer.domElement)) {
        currentMount.removeChild(renderer.domElement);
      }
      scene.clear();
      renderer.dispose();
    };
  }, [isRotating]);

  return (
    <div className="relative w-full h-[600px] rounded-2xl overflow-hidden bg-gradient-to-b from-[#090e1a] via-[#070b14] to-[#040711] border border-slate-800 shadow-2xl flex flex-col">
      {/* Top Telemetry & Controls Overlay */}
      <div className="absolute top-5 left-6 right-6 z-10 flex flex-col gap-3 pointer-events-none">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.35)] shrink-0">
              <Globe className="w-5 h-5 animate-pulse-slow" />
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-cyan-300 font-extrabold flex items-center gap-2">
                <span>3D Multi-Bank Cyber Clearing Fabric</span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              </div>
              <div className="text-xs text-slate-300 font-medium mt-0.5">
                Cross-Bank Synthetic Settlement & Mule Ring Detection Sphere (Drag to rotate)
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2.5 pointer-events-auto">
            {/* Institution Filter Dropdown */}
            <select
              value={activeBank}
              onChange={(e) => setActiveBank(e.target.value)}
              className="px-3 py-1.5 text-xs rounded-xl bg-slate-900 hover:bg-slate-850 text-cyan-300 border border-slate-700 font-mono font-bold focus:outline-none focus:border-cyan-500 shadow-md cursor-pointer"
            >
              <option value="ALL_BANKS">All Institutions (4 Banks + Central)</option>
              <option value="BANK_A">Bank A (Primary Hub)</option>
              <option value="BANK_B">Bank B (Commercial Node)</option>
              <option value="BANK_C">Bank C (Cooperative Node)</option>
              <option value="BANK_D">Bank D (Federal Node)</option>
              <option value="SWITCH">Central Clearing Switch</option>
            </select>

            <button
              onClick={() => setIsRotating(!isRotating)}
              className="px-3 py-1.5 text-xs font-bold rounded-xl bg-slate-900 hover:bg-slate-850 text-slate-200 border border-slate-700 flex items-center gap-1.5 transition-colors shadow-md cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRotating ? 'animate-spin text-cyan-400' : ''}`} />
              <span>{isRotating ? 'Pause Orbit' : 'Resume Orbit'}</span>
            </button>
          </div>
        </div>

        {/* Institution Color Legend */}
        <div className="flex flex-wrap items-center gap-2 pointer-events-auto">
          <span
            onClick={() => setActiveBank(activeBank === 'BANK_A' ? 'ALL_BANKS' : 'BANK_A')}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-mono cursor-pointer transition-all border ${
              activeBank === 'BANK_A'
                ? 'bg-cyan-500/30 border-cyan-400 text-cyan-200 shadow-md shadow-cyan-500/20'
                : 'bg-slate-900/80 border-cyan-500/30 text-cyan-400 hover:border-cyan-400'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-[#06b6d4]" /> Bank A
          </span>
          <span
            onClick={() => setActiveBank(activeBank === 'BANK_B' ? 'ALL_BANKS' : 'BANK_B')}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-mono cursor-pointer transition-all border ${
              activeBank === 'BANK_B'
                ? 'bg-emerald-500/30 border-emerald-400 text-emerald-200 shadow-md shadow-emerald-500/20'
                : 'bg-slate-900/80 border-emerald-500/30 text-emerald-400 hover:border-emerald-400'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-[#10b981]" /> Bank B
          </span>
          <span
            onClick={() => setActiveBank(activeBank === 'BANK_C' ? 'ALL_BANKS' : 'BANK_C')}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-mono cursor-pointer transition-all border ${
              activeBank === 'BANK_C'
                ? 'bg-purple-500/30 border-purple-400 text-purple-200 shadow-md shadow-purple-500/20'
                : 'bg-slate-900/80 border-purple-500/30 text-purple-400 hover:border-purple-400'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-[#a855f7]" /> Bank C
          </span>
          <span
            onClick={() => setActiveBank(activeBank === 'BANK_D' ? 'ALL_BANKS' : 'BANK_D')}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-mono cursor-pointer transition-all border ${
              activeBank === 'BANK_D'
                ? 'bg-amber-500/30 border-amber-400 text-amber-200 shadow-md shadow-amber-500/20'
                : 'bg-slate-900/80 border-amber-500/30 text-amber-400 hover:border-amber-400'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-[#f59e0b]" /> Bank D
          </span>
          <span
            onClick={() => setActiveBank(activeBank === 'SWITCH' ? 'ALL_BANKS' : 'SWITCH')}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-mono cursor-pointer transition-all border ${
              activeBank === 'SWITCH'
                ? 'bg-yellow-500/30 border-yellow-400 text-yellow-200 shadow-md shadow-yellow-500/20'
                : 'bg-slate-900/80 border-yellow-500/30 text-yellow-400 hover:border-yellow-400'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-[#facc15]" /> Central Switch
          </span>
        </div>
      </div>

      {/* 3D Canvas Mount Point */}
      <div ref={mountRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Bottom Telemetry HUD */}
      <div className="absolute bottom-4 left-5 right-5 z-10 grid grid-cols-2 md:grid-cols-4 gap-2.5 pointer-events-none">
        <div className="p-2.5 rounded-xl bg-slate-900/85 backdrop-blur-md border border-slate-800/80">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" /> Security Grid
          </div>
          <div className="text-sm font-bold text-white mt-0.5">Dual-Bank Active</div>
          <div className="text-[10px] text-emerald-400 font-mono">100% Zero Unilateral Freeze</div>
        </div>

        <div className="p-2.5 rounded-xl bg-slate-900/85 backdrop-blur-md border border-slate-800/80">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Zap className="w-3.5 h-3.5 text-amber-400" /> Monitored Gateways
          </div>
          <div className="text-sm font-bold text-white mt-0.5">4 Institutions + Central</div>
          <div className="text-[10px] text-cyan-400 font-mono">Bank A, Bank B, Bank C, Bank D</div>
        </div>

        <div className="p-2.5 rounded-xl bg-slate-900/85 backdrop-blur-md border border-slate-800/80">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Activity className="w-3.5 h-3.5 text-emerald-400" /> Ring Interception
          </div>
          <div className="text-sm font-bold text-emerald-400 font-mono mt-0.5">33 Mule Rings</div>
          <div className="text-[10px] text-slate-400">100% Ground-Truth Recall</div>
        </div>

        <div className="p-2.5 rounded-xl bg-slate-900/85 backdrop-blur-md border border-slate-800/80">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">Volume & Pulses</div>
          <div className="text-sm font-bold text-cyan-300 font-mono mt-0.5">₹8.04 Cr ({pulseCount.toLocaleString()} pkts)</div>
          <div className="text-[10px] text-slate-400">27,743 Reconciled Txns</div>
        </div>
      </div>
    </div>
  );
}
