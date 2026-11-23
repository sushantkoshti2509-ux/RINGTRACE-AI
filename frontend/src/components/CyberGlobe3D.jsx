import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { ShieldCheck, Activity, Globe, RefreshCw, Zap } from 'lucide-react';

export default function CyberGlobe3D() {
  const mountRef = useRef(null);
  const [activeBank, setActiveBank] = useState('ALL_BANKS');
  const [pulseCount, setPulseCount] = useState(1420);
  const [isRotating, setIsRotating] = useState(true);

  useEffect(() => {
    const currentMount = mountRef.current;
    if (!currentMount) return;

    // Scene, Camera, Renderer
    const width = currentMount.clientWidth || 600;
    const height = currentMount.clientHeight || 450;
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x070b14, 0.002);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 30, 85);

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
      opacity: 0.15,
    });
    const sphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
    globeGroup.add(sphereMesh);

    // 2. Inner Glowing Core
    const innerGeo = new THREE.SphereGeometry(sphereRadius * 0.85, 24, 24);
    const innerMat = new THREE.MeshBasicMaterial({
      color: 0x0f172a,
      transparent: true,
      opacity: 0.8,
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

    // 4. Inter-Bank Gateway Hubs (Bank A, Bank B, Bank C)
    const bankNodes = [
      { name: 'Bank A (Gateway Alpha)', pos: new THREE.Vector3(18, 12, 14), color: 0x06b6d4 },
      { name: 'Bank B (Gateway Beta)', pos: new THREE.Vector3(-19, 8, 12), color: 0x10b981 },
      { name: 'Bank C (Gateway Gamma)', pos: new THREE.Vector3(2, -18, 15), color: 0xa855f7 },
      { name: 'Central Switch', pos: new THREE.Vector3(0, 0, 26), color: 0xf59e0b },
    ];

    const bankMeshList = [];
    bankNodes.forEach(b => {
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
      bankMeshList.push({ mesh: nodeMesh, ring: ringMesh });
    });

    // 5. 3D Inter-Bank Transaction Arcs
    const createArc = (startVec, endVec, colorHex) => {
      const mid = new THREE.Vector3().addVectors(startVec, endVec).multiplyScalar(0.5);
      const distance = startVec.distanceTo(endVec);
      mid.normalize().multiplyScalar(sphereRadius + distance * 0.35);

      const curve = new THREE.QuadraticBezierCurve3(startVec, mid, endVec);
      const points = curve.getPoints(40);
      const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
      const lineMat = new THREE.LineBasicMaterial({
        color: colorHex,
        transparent: true,
        opacity: 0.45,
      });
      const lineMesh = new THREE.Line(lineGeo, lineMat);
      globeGroup.add(lineMesh);
      return { curve, lineMesh };
    };

    const arcs = [
      createArc(bankNodes[0].pos, bankNodes[1].pos, 0x06b6d4),
      createArc(bankNodes[1].pos, bankNodes[2].pos, 0x10b981),
      createArc(bankNodes[2].pos, bankNodes[0].pos, 0xa855f7),
      createArc(bankNodes[0].pos, bankNodes[3].pos, 0xf59e0b),
      createArc(bankNodes[1].pos, bankNodes[3].pos, 0xf59e0b),
      createArc(bankNodes[2].pos, bankNodes[3].pos, 0xf59e0b),
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

      // Pulse halos
      bankMeshList.forEach((item, idx) => {
        const scale = 1 + 0.15 * Math.sin(time * 3 + idx);
        item.ring.scale.set(scale, scale, scale);
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
    <div className="relative w-full h-[460px] rounded-2xl overflow-hidden glass-panel border border-cyan-500/20 shadow-2xl flex flex-col">
      {/* Top Telemetry Overlay */}
      <div className="absolute top-4 left-5 right-5 z-10 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)]">
            <Globe className="w-5 h-5 animate-pulse-slow" />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-cyan-400/90 font-bold flex items-center gap-2">
              <span>3D Cross-Bank Clearing Sphere</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            </div>
            <div className="text-[11px] text-slate-400">
              Interactive Multi-Institution Transaction Fabric (Drag to rotate)
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 pointer-events-auto">
          <button
            onClick={() => setIsRotating(!isRotating)}
            className="px-2.5 py-1 text-xs rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border border-slate-700/60 flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className={`w-3 h-3 ${isRotating ? 'animate-spin text-cyan-400' : ''}`} />
            {isRotating ? 'Pause Orbit' : 'Resume Orbit'}
          </button>
        </div>
      </div>

      {/* 3D Canvas Mount Point */}
      <div ref={mountRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Bottom Telemetry HUD */}
      <div className="absolute bottom-4 left-5 right-5 z-10 grid grid-cols-2 md:grid-cols-4 gap-2.5 pointer-events-none">
        <div className="p-2.5 rounded-xl bg-slate-900/80 backdrop-blur-md border border-slate-800/80">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" /> Security Grid
          </div>
          <div className="text-sm font-bold text-white mt-0.5">Dual-Bank Active</div>
          <div className="text-[10px] text-emerald-400 font-mono">100% Zero Unilateral Freeze</div>
        </div>

        <div className="p-2.5 rounded-xl bg-slate-900/80 backdrop-blur-md border border-slate-800/80">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Zap className="w-3.5 h-3.5 text-amber-400" /> Monitored Gateways
          </div>
          <div className="text-sm font-bold text-white mt-0.5">3 Banks + Central</div>
          <div className="text-[10px] text-cyan-400 font-mono">Bank A, B, C Connected</div>
        </div>

        <div className="p-2.5 rounded-xl bg-slate-900/80 backdrop-blur-md border border-slate-800/80">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Activity className="w-3.5 h-3.5 text-emerald-400" /> Clearing Latency
          </div>
          <div className="text-sm font-bold text-emerald-400 font-mono mt-0.5">11.4 ms</div>
          <div className="text-[10px] text-slate-400">Sub-15ms Target Met</div>
        </div>

        <div className="p-2.5 rounded-xl bg-slate-900/80 backdrop-blur-md border border-slate-800/80">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">Live Fund Pulses</div>
          <div className="text-sm font-bold text-cyan-300 font-mono mt-0.5">{pulseCount.toLocaleString()}</div>
          <div className="text-[10px] text-slate-400">Real-time Ingestion</div>
        </div>
      </div>
    </div>
  );
}
