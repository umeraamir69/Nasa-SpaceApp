import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CASE_META } from "../caseContent.js";

const RADIUS = 1;
const VERDICT_COLOR = { detected: "#e4572e", negative: "#48cae4", marginal: "#f0b429" };

function latLonToVec3(lat, lon, r) {
  const phi = ((90 - lat) * Math.PI) / 180;
  const theta = ((lon + 180) * Math.PI) / 180;
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
    r * Math.cos(phi),
    r * Math.sin(phi) * Math.sin(theta),
  );
}

function graticule(color, opacity) {
  const pts = [];
  for (let lat = -75; lat <= 75; lat += 15) {
    let prev = null;
    for (let lon = -180; lon <= 180; lon += 4) {
      const p = latLonToVec3(lat, lon, RADIUS + 0.001);
      if (prev) pts.push(prev.clone(), p.clone());
      prev = p;
    }
  }
  for (let lon = -180; lon < 180; lon += 15) {
    let prev = null;
    for (let lat = -90; lat <= 90; lat += 4) {
      const p = latLonToVec3(lat, lon, RADIUS + 0.001);
      if (prev) pts.push(prev.clone(), p.clone());
      prev = p;
    }
  }
  const geo = new THREE.BufferGeometry().setFromPoints(pts);
  return new THREE.LineSegments(
    geo,
    new THREE.LineBasicMaterial({ color, transparent: true, opacity }),
  );
}

function stars() {
  // Deterministic pseudo-random shell so every load looks the same.
  let seed = 42;
  const rnd = () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 4294967296;
  };
  const pts = [];
  for (let i = 0; i < 450; i++) {
    const v = new THREE.Vector3(rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1);
    if (v.lengthSq() < 1e-6) continue;
    pts.push(v.normalize().multiplyScalar(6 + rnd() * 14));
  }
  const geo = new THREE.BufferGeometry().setFromPoints(pts);
  return new THREE.Points(
    geo,
    new THREE.PointsMaterial({ color: 0x8fa3b8, size: 0.035, sizeAttenuation: true }),
  );
}

export default function Globe({ cases, onOpen }) {
  const mountRef = useRef(null);
  const openRef = useRef(onOpen);
  openRef.current = onOpen;
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return undefined;
    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      setFailed(true);
      return undefined;
    }
    const W = mount.clientWidth || 600;
    const H = mount.clientHeight || 380;
    renderer.setSize(W, H);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    mount.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, W / H, 0.1, 100);
    camera.position.set(0, 0.6, 3.1);

    scene.add(new THREE.AmbientLight(0xbfd0e0, 0.75));
    const sun = new THREE.DirectionalLight(0xfff2df, 1.6);
    sun.position.set(-4, 2, 3);
    scene.add(sun);

    const globe = new THREE.Mesh(
      new THREE.SphereGeometry(RADIUS, 48, 32),
      new THREE.MeshStandardMaterial({ color: 0x18242f, roughness: 0.95, metalness: 0 }),
    );
    scene.add(globe);
    scene.add(graticule(0x33506a, 0.55));
    scene.add(stars());

    const markers = [];
    for (const cas of cases || []) {
      const b = cas?.bounds;
      if (!b || !Number.isFinite(b.south)) continue;
      const lat = (b.south + b.north) / 2;
      const lon = (b.west + b.east) / 2;
      const verdict = (CASE_META[cas.case_id] || {}).verdict || "detected";
      const m = new THREE.Mesh(
        new THREE.SphereGeometry(0.028, 16, 12),
        new THREE.MeshBasicMaterial({ color: VERDICT_COLOR[verdict] || "#e4572e" }),
      );
      m.position.copy(latLonToVec3(lat, lon, RADIUS + 0.012));
      m.userData.caseId = cas.case_id;
      m.userData.label = cas.label || cas.case_id;
      scene.add(m);
      markers.push(m);
    }

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.enablePan = false;
    controls.minDistance = 1.7;
    controls.maxDistance = 6;
    const calm = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    controls.autoRotate = !calm;
    controls.autoRotateSpeed = 0.7;

    const ray = new THREE.Raycaster();
    const ptr = new THREE.Vector2();
    let downAt = null;
    const pick = (e) => {
      const rect = renderer.domElement.getBoundingClientRect();
      ptr.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      ptr.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      ray.setFromCamera(ptr, camera);
      const hit = ray.intersectObjects(markers, false)[0];
      return hit ? hit.object.userData.caseId : null;
    };
    const onDown = (e) => {
      downAt = [e.clientX, e.clientY];
    };
    const onUp = (e) => {
      if (!downAt) return;
      const dx = e.clientX - downAt[0];
      const dy = e.clientY - downAt[1];
      downAt = null;
      if (dx * dx + dy * dy > 25) return; // it was a drag, not a tap
      const id = pick(e);
      if (id) openRef.current?.(id);
    };
    let lastHover = 0;
    const onMove = (e) => {
      const now = Date.now();
      if (now - lastHover < 60) return;
      lastHover = now;
      renderer.domElement.style.cursor = pick(e) ? "pointer" : "grab";
    };
    renderer.domElement.addEventListener("pointerdown", onDown);
    renderer.domElement.addEventListener("pointerup", onUp);
    renderer.domElement.addEventListener("pointermove", onMove);

    const ro = new ResizeObserver(() => {
      const w = mount.clientWidth || 600;
      const h = mount.clientHeight || 380;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });
    ro.observe(mount);

    let raf = 0;
    const loop = () => {
      raf = requestAnimationFrame(loop);
      controls.update();
      renderer.render(scene, camera);
    };
    loop();

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      renderer.domElement.removeEventListener("pointerdown", onDown);
      renderer.domElement.removeEventListener("pointerup", onUp);
      renderer.domElement.removeEventListener("pointermove", onMove);
      controls.dispose();
      scene.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        if (o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m.dispose());
      });
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, [cases]);

  if (failed) {
    return <div className="globe-fallback">3D globe unavailable (WebGL disabled). Use the case cards below.</div>;
  }
  const items = (cases || []).filter((c) => c && c.case_id);
  return (
    <div className="globe-wrap">
      <div ref={mountRef} className="globe-canvas" role="img" aria-label="3D globe with the nine case locations marked" />
      <div className="globe-legend">
        {items.map((cas) => {
          const verdict = (CASE_META[cas.case_id] || {}).verdict || "detected";
          return (
            <button
              key={cas.case_id}
              type="button"
              className="globe-chip"
              onClick={() => onOpen(cas.case_id)}
              title={`Open ${cas.label || cas.case_id}`}
            >
              <span className="globe-dot" style={{ background: VERDICT_COLOR[verdict] || "#e4572e" }} />
              {cas.label || cas.case_id}
            </button>
          );
        })}
      </div>
    </div>
  );
}
