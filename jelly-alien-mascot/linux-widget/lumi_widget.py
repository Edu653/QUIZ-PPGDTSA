#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lumi - Companheira Flutuante com Tentáculos (Widget Nativo para Linux Desktop)
==============================================================================
Arquivo único (100% autocontido, sem arquivos externos).
- Estado padrão: 'idle' (Flutuação Viva com propulsão de medusa e 6 tentáculos IK/onda)
- Eventos aleatórios: Executa animações espontâneas ('cosmic_boba', 'juggling_orbs',
  'dj_headphones', 'abducting_duck', 'hypnotic', 'happy_spin', 'electro_shock')
  em intervalos aleatórios e retorna automaticamente à Flutuação Viva ('idle').
- Janela transparente, sem bordas (frameless), arrastável pela tela e com menu
  de contexto no botão direito do mouse.

Como executar no Linux (inclusive junto com o gloop_widget.py!):
  chmod +x lumi_widget.py
  ./lumi_widget.py
"""

import sys

EMBEDDED_HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>Lumi Linux Widget</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      -webkit-user-select: none;
    }
    html, body {
      width: 100%;
      height: 100%;
      background: transparent !important;
      overflow: hidden;
      font-family: system-ui, -apple-system, sans-serif;
    }
    #stage {
      position: relative;
      width: 260px;
      height: 255px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    canvas {
      display: block;
      cursor: grab;
      touch-action: none;
    }
    canvas:active {
      cursor: grabbing;
    }
    #hud {
      position: absolute;
      bottom: 4px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 6px;
      align-items: center;
      padding: 3px 9px;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.80);
      border: 1px solid rgba(244, 114, 182, 0.28);
      backdrop-filter: blur(6px);
      opacity: 0;
      transition: opacity 0.2s ease;
      pointer-events: none;
      white-space: nowrap;
      color: #f8fafc;
      font-size: 11px;
    }
    #stage:hover #hud {
      opacity: 1;
      pointer-events: auto;
    }
    .hud-btn {
      background: none;
      border: none;
      color: #f472b6;
      cursor: pointer;
      font-size: 11px;
      font-weight: 600;
      padding: 0 3px;
    }
    .hud-btn:hover {
      color: #38bdf8;
    }
  </style>
</head>
<body>
  <div id="stage">
    <canvas id="lumiCanvas" width="260" height="250"></canvas>
    <div id="hud">
      <span id="hudState">🪼 Flutuação Viva</span>
      <span>•</span>
      <button class="hud-btn" onclick="window.triggerRandomNow()">🎲 Sortear</button>
    </div>
  </div>

  <script>
    const canvas = document.getElementById('lumiCanvas');
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    const S = 1.0;

    const LUMI_THEMES = {
      astral: {
        core: 'rgba(251, 207, 232, 0.88)',
        mid: 'rgba(217, 70, 239, 0.68)',
        edge: 'rgba(88, 28, 135, 0.85)',
        rim: '#f472b6',
        tentacleBase: 'rgba(192, 38, 211, 0.72)',
        tentacleTip: '#38bdf8',
        bioNode: '#67e8f9',
        glow: 'rgba(217, 70, 239, 0.34)',
        irisOuter: '#4a044e',
        irisInner: '#fbbf24',
        tint: 'rgba(217, 70, 239, 0.22)'
      },
      abyssal: {
        core: 'rgba(186, 230, 253, 0.88)',
        mid: 'rgba(37, 99, 235, 0.68)',
        edge: 'rgba(30, 27, 75, 0.88)',
        rim: '#60a5fa',
        tentacleBase: 'rgba(59, 130, 246, 0.72)',
        tentacleTip: '#a3e635',
        bioNode: '#bef264',
        glow: 'rgba(59, 130, 246, 0.36)',
        irisOuter: '#172554',
        irisInner: '#a3e635',
        tint: 'rgba(37, 99, 235, 0.22)'
      },
      aurora: {
        core: 'rgba(204, 251, 241, 0.88)',
        mid: 'rgba(20, 184, 166, 0.66)',
        edge: 'rgba(112, 26, 117, 0.84)',
        rim: '#5eead4',
        tentacleBase: 'rgba(168, 85, 247, 0.70)',
        tentacleTip: '#f472b6',
        bioNode: '#fde047',
        glow: 'rgba(45, 212, 191, 0.34)',
        irisOuter: '#134e4a',
        irisInner: '#e879f9',
        tint: 'rgba(20, 184, 166, 0.20)'
      },
      solaris: {
        core: 'rgba(254, 249, 195, 0.90)',
        mid: 'rgba(249, 115, 22, 0.68)',
        edge: 'rgba(127, 29, 29, 0.86)',
        rim: '#fde047',
        tentacleBase: 'rgba(234, 88, 12, 0.74)',
        tentacleTip: '#c084fc',
        bioNode: '#fef08a',
        glow: 'rgba(249, 115, 22, 0.35)',
        irisOuter: '#7c2d12',
        irisInner: '#38bdf8',
        tint: 'rgba(249, 115, 22, 0.22)'
      },
      phantom: {
        core: 'rgba(255, 255, 255, 0.92)',
        mid: 'rgba(165, 180, 252, 0.64)',
        edge: 'rgba(49, 46, 129, 0.82)',
        rim: '#e0e7ff',
        tentacleBase: 'rgba(129, 140, 248, 0.68)',
        tentacleTip: '#2dd4bf',
        bioNode: '#f472b6',
        glow: 'rgba(165, 180, 252, 0.36)',
        irisOuter: '#312e81',
        irisInner: '#2dd4bf',
        tint: 'rgba(165, 180, 252, 0.20)'
      }
    };

    const STATE_LABELS = {
      idle: '🪼 Flutuação Viva',
      cosmic_boba: '🧋 Boba Cósmico',
      juggling_orbs: '🔮 Malabarismo',
      dj_headphones: '🎧 DJ & Vinil',
      abducting_duck: '🛸 Abduzir Pato',
      hypnotic: '🌀 Hipnose Bio',
      happy_spin: '✨ Giro Feliz',
      electro_shock: '⚡ Choque Bio',
      sleepy_drift: '🌙 Deriva Zzz'
    };

    const STATE_DURATIONS = {
      cosmic_boba: 8.6,
      juggling_orbs: 8.2,
      dj_headphones: 8.4,
      abducting_duck: 8.4,
      hypnotic: 5.2,
      happy_spin: 4.0,
      electro_shock: 3.4,
      sleepy_drift: 6.5
    };

    let currentTheme = LUMI_THEMES.astral;
    let currentState = 'idle';
    let stateTimer = 0;
    let time = 0;
    let autoRandom = true;
    let minIdleSec = 16;
    let maxIdleSec = 36;
    let nextRandomTimer = 16 + Math.random() * 20;
    let lastRandomState = '';

    let baseCx = W * 0.5;
    let baseCy = H * 0.40;
    let bellX = baseCx;
    let bellY = baseCy;
    let bellVx = 0;
    let bellVy = 0;
    let bellRadius = 48;
    let bellScaleX = 1;
    let bellScaleY = 1;
    let bellRotation = 0;
    let pulsePhase = 0;

    const NUM_NODES = 26;
    const nodes = Array.from({ length: NUM_NODES }, (_, i) => ({
      angle: (i / NUM_NODES) * Math.PI * 2,
      r: bellRadius,
      vr: 0,
      x: 0,
      y: 0
    }));

    const NUM_TENTACLES = 6;
    const SEGMENTS = 9;
    const tentacles = Array.from({ length: NUM_TENTACLES }, (_, t) => {
      const norm = (t / (NUM_TENTACLES - 1)) * 2 - 1;
      const isFeeler = (t === 0 || t === NUM_TENTACLES - 1);
      const segLen = isFeeler ? 8.2 : 6.8 + (t % 2) * 1.1;
      const pts = Array.from({ length: SEGMENTS }, (_, s) => ({
        x: baseCx + norm * 28,
        y: baseCy + 20 + s * segLen,
        vx: 0,
        vy: 0
      }));
      return {
        index: t,
        norm,
        isFeeler,
        layer: (t === 1 || t === 4) ? 'back' : 'front',
        segLen,
        pts,
        targetX: null,
        targetY: null,
        targetWeight: 0
      };
    });

    const eye = {
      x: baseCx,
      y: baseCy - 4,
      vx: 0,
      vy: 0,
      lookX: 0,
      lookY: 0,
      radius: 17.5,
      pupilScale: 1.0,
      blink: 0,
      blinkTimer: 2.8,
      idleLookTimer: 1.5,
      idleTargetX: 0,
      idleTargetY: 0
    };

    const bubbles = Array.from({ length: 11 }, (_, i) => ({
      angle: (i / 11) * Math.PI * 2,
      dist: 10 + Math.random() * 26,
      r: 1.6 + Math.random() * 2.8,
      speed: 0.4 + Math.random() * 0.6
    }));

    const particles = [];
    const bobaProp = { active: false, cupX: W + 40, cupY: baseCy + 12, liquidLevel: 1.0, slurpPhase: 0, strawPearlProg: -1, insidePearls: [] };
    const juggleProp = {
      active: false,
      phase: 0,
      orbs: [
        { color: '#fde047', glow: '#f59e0b', x: 0, y: 0 },
        { color: '#38bdf8', glow: '#0284c7', x: 0, y: 0 },
        { color: '#f472b6', glow: '#db2777', x: 0, y: 0 }
      ]
    };
    const djProp = { active: false, headphoneY: -60, beatPhase: 0, vinylAngle: 0, deckAlpha: 0 };
    const duckProp = { active: false, x: W + 30, y: H - 24, beamPower: 0, duckSpin: 0 };
    const pointer = { x: W / 2, y: H / 2, active: false };

    function spawnParticle(x, y, text, color = '#ffffff', vy = -1.1) {
      particles.push({
        x, y,
        vx: (Math.random() - 0.5) * 1.1,
        vy,
        text,
        color,
        alpha: 1.0,
        scale: 0.7 + Math.random() * 0.4,
        life: 0,
        maxLife: 55 + Math.random() * 25
      });
    }

    window.setMascotState = function(newState) {
      currentState = newState;
      stateTimer = 0;
      document.getElementById('hudState').textContent = STATE_LABELS[newState] || newState;
      bobaProp.active = (newState === 'cosmic_boba');
      if (bobaProp.active) {
        bobaProp.cupX = W + 45;
        bobaProp.cupY = baseCy + 12;
        bobaProp.liquidLevel = 1.0;
        bobaProp.slurpPhase = 0;
        bobaProp.strawPearlProg = -1;
        bobaProp.insidePearls = [];
      }
      juggleProp.active = (newState === 'juggling_orbs');
      if (juggleProp.active) juggleProp.phase = 0;
      djProp.active = (newState === 'dj_headphones');
      if (djProp.active) {
        djProp.headphoneY = -60;
        djProp.beatPhase = 0;
        djProp.deckAlpha = 0;
      }
      duckProp.active = (newState === 'abducting_duck');
      if (duckProp.active) {
        duckProp.x = W + 30;
        duckProp.y = H - 24;
        duckProp.beamPower = 0;
        duckProp.duckSpin = 0;
      }
      bellVy -= 2.2;
    };

    window.setMascotTheme = function(tName) {
      if (LUMI_THEMES[tName]) currentTheme = LUMI_THEMES[tName];
    };

    window.setRandomIntervalRange = function(minS, maxS) {
      minIdleSec = minS;
      maxIdleSec = maxS;
      nextRandomTimer = minIdleSec + Math.random() * (maxIdleSec - minIdleSec);
    };

    window.triggerRandomNow = function() {
      const pool = [
        'cosmic_boba', 'cosmic_boba',
        'juggling_orbs', 'juggling_orbs',
        'dj_headphones', 'dj_headphones',
        'abducting_duck', 'abducting_duck',
        'hypnotic', 'happy_spin', 'electro_shock'
      ].filter(s => s !== lastRandomState);
      const pick = pool[Math.floor(Math.random() * pool.length)];
      lastRandomState = pick;
      window.setMascotState(pick);
      nextRandomTimer = minIdleSec + Math.random() * (maxIdleSec - minIdleSec);
    };

    function getDomeRestRadius(angle, pulse) {
      const sinA = Math.sin(angle);
      let r = bellRadius;
      if (sinA < 0) {
        r *= 1.0 + Math.abs(sinA) * 0.06;
      } else {
        r += Math.pow(sinA, 0.7) * 5.5 + Math.cos(angle * 6) * 2.2 * sinA - sinA * 6.5;
      }
      r += Math.cos(angle * 2) * pulse * 3.8;
      return r;
    }

    function updatePhysics(dt) {
      time += dt;
      stateTimer += dt;

      if (currentState === 'idle') {
        if (autoRandom) {
          nextRandomTimer -= dt;
          if (nextRandomTimer <= 0) window.triggerRandomNow();
        }
      } else {
        const maxDur = STATE_DURATIONS[currentState] || 6.0;
        if (stateTimer >= maxDur) {
          window.setMascotState('idle');
          nextRandomTimer = minIdleSec + Math.random() * (maxIdleSec - minIdleSec);
        }
      }

      for (const t of tentacles) t.targetWeight *= 0.85;

      const pulseSpeed = currentState === 'sleepy_drift' ? 1.6 : (currentState === 'dj_headphones' ? 6.6 : 2.8);
      pulsePhase += dt * pulseSpeed;
      const swimPulse = Math.sin(pulsePhase);

      let targetX = baseCx + Math.sin(time * 1.1) * 7;
      let targetY = baseCy + Math.cos(time * 2.2) * 9 - swimPulse * 4;
      bellRotation *= 0.88;

      if (currentState === 'happy_spin') {
        bellRotation = Math.sin(stateTimer * Math.PI * 1.6) * 0.35;
        targetY = baseCy - Math.abs(Math.sin(stateTimer * 5.5)) * 18;
        if (Math.random() < 0.28) spawnParticle(bellX + (Math.random() - 0.5) * 65, bellY, '✦', currentTheme.tentacleTip, -1.0);
      } else if (currentState === 'electro_shock') {
        targetX += (Math.random() - 0.5) * 10;
        targetY += (Math.random() - 0.5) * 8;
        if (Math.random() < 0.35) spawnParticle(bellX + (Math.random() - 0.5) * 70, bellY, '⚡', '#67e8f9', -1.4);
      } else if (currentState === 'sleepy_drift') {
        targetY = baseCy + 10 + Math.sin(time * 1.1) * 6;
        if (Math.random() < 0.04) spawnParticle(bellX + 18, bellY - 26, 'z', currentTheme.rim, -0.65);
      } else if (currentState === 'hypnotic') {
        targetX = baseCx + Math.sin(time * 2.4) * 12;
        targetY = baseCy + Math.cos(time * 2.4) * 7;
      }

      if (currentState === 'cosmic_boba') {
        const t = stateTimer;
        const holdX = bellX + 46;
        const holdY = bellY + 14;
        if (t < 1.1) {
          const p = t / 1.1;
          bobaProp.cupX = W + 40 + (holdX - (W + 40)) * (1 - Math.pow(1 - p, 3));
          bobaProp.cupY = holdY;
        } else if (t < 7.2) {
          bobaProp.cupX = holdX + Math.sin(time * 3) * 2;
          bobaProp.cupY = holdY + Math.cos(time * 2.5) * 2.5;
          tentacles[5].targetX = bobaProp.cupX + 4;
          tentacles[5].targetY = bobaProp.cupY + 6;
          tentacles[5].targetWeight = 0.95;
          tentacles[0].targetX = bellX + 24;
          tentacles[0].targetY = bellY + 4;
          tentacles[0].targetWeight = 0.85;

          const prevSlurp = Math.floor(bobaProp.slurpPhase);
          bobaProp.slurpPhase += dt * 1.35;
          if (Math.floor(bobaProp.slurpPhase) > prevSlurp && bobaProp.liquidLevel > 0.12) {
            bobaProp.strawPearlProg = 0.0;
            bobaProp.liquidLevel = Math.max(0.08, bobaProp.liquidLevel - 0.14);
            bellScaleX = 0.92;
            bellScaleY = 1.08;
            spawnParticle(bobaProp.cupX, bobaProp.cupY - 26, '♥', '#f472b6', -1.1);
          }
          if (bobaProp.strawPearlProg >= 0) {
            bobaProp.strawPearlProg += dt * 2.8;
            if (bobaProp.strawPearlProg >= 1.0) {
              bobaProp.strawPearlProg = -1;
              bobaProp.insidePearls.push({
                x: bellX + 18,
                y: bellY + 2,
                vx: -2.2 - Math.random() * 1.5,
                vy: -1.8 + (Math.random() - 0.5) * 2.2,
                color: Math.random() < 0.5 ? '#c084fc' : '#38bdf8',
                alpha: 1.0
              });
            }
          }
        } else {
          bobaProp.cupX += 3.6;
          for (const ip of bobaProp.insidePearls) ip.alpha = Math.max(0, ip.alpha - dt * 1.2);
        }
        for (const ip of bobaProp.insidePearls) {
          ip.x += ip.vx;
          ip.y += ip.vy;
          ip.vx *= 0.96;
          ip.vy *= 0.96;
          const dx = ip.x - bellX;
          const dy = ip.y - bellY;
          const dist = Math.hypot(dx, dy);
          if (dist > bellRadius * 0.56) {
            ip.x = bellX + (dx / dist) * bellRadius * 0.55;
            ip.y = bellY + (dy / dist) * bellRadius * 0.55;
            ip.vx *= -0.7;
            ip.vy *= -0.7;
          }
        }
      }

      if (currentState === 'juggling_orbs') {
        juggleProp.phase += dt * 4.2;
        const handY = bellY + 10;
        for (let i = 0; i < 3; i++) {
          const p = (juggleProp.phase + (i * Math.PI * 2) / 3) % (Math.PI * 2);
          juggleProp.orbs[i].x = bellX + Math.sin(p) * 48;
          juggleProp.orbs[i].y = handY - Math.abs(Math.sin(p * 2)) * 56 - 8;
        }
        tentacles[0].targetX = bellX - 48 + Math.cos(juggleProp.phase * 2) * 10;
        tentacles[0].targetY = handY - Math.max(0, Math.sin(juggleProp.phase * 2)) * 16;
        tentacles[0].targetWeight = 0.95;
        tentacles[5].targetX = bellX + 48 - Math.cos(juggleProp.phase * 2) * 10;
        tentacles[5].targetY = handY - Math.max(0, -Math.sin(juggleProp.phase * 2)) * 16;
        tentacles[5].targetWeight = 0.95;
      }

      if (currentState === 'dj_headphones') {
        const t = stateTimer;
        djProp.beatPhase += dt * 8.5;
        djProp.vinylAngle += dt * 4.5;
        if (t < 0.9) {
          djProp.headphoneY = -60 + (bellY - 6 - (-60)) * (t / 0.9);
          djProp.deckAlpha = t / 0.9;
        } else if (t < 7.4) {
          djProp.headphoneY = bellY - 6;
          djProp.deckAlpha = 1.0;
          targetY = baseCy + Math.sin(djProp.beatPhase) * 6;
          tentacles[0].targetX = bellX - 44;
          tentacles[0].targetY = bellY - 4;
          tentacles[0].targetWeight = 0.92;
          tentacles[5].targetX = bellX + 44 + Math.sin(time * 14) * 9;
          tentacles[5].targetY = bellY + 23;
          tentacles[5].targetWeight = 0.95;
          if (Math.random() < 0.16) spawnParticle(bellX + (Math.random() - 0.5) * 70, bellY - 25, '♪', '#38bdf8', -1.2);
        } else {
          djProp.headphoneY -= 5.5;
          djProp.deckAlpha = Math.max(0, djProp.deckAlpha - dt * 2.5);
        }
      }

      if (currentState === 'abducting_duck') {
        const t = stateTimer;
        if (t < 1.6) {
          duckProp.x = W + 30 + (bellX - (W + 30)) * (t / 1.6);
          duckProp.y = H - 22;
          duckProp.beamPower = 0;
        } else if (t < 5.6) {
          duckProp.beamPower = Math.min(1, duckProp.beamPower + dt * 3.5);
          duckProp.x = bellX + Math.sin(time * 3.5) * 5;
          duckProp.y += (bellY + 48 - duckProp.y) * 0.08;
          duckProp.duckSpin = Math.sin(time * 3.2) * 0.25;
          tentacles[0].targetX = duckProp.x - 18;
          tentacles[0].targetY = duckProp.y - 4;
          tentacles[0].targetWeight = 0.9;
          tentacles[5].targetX = duckProp.x + 18;
          tentacles[5].targetY = duckProp.y - 4;
          tentacles[5].targetWeight = 0.9;
          if (Math.random() < 0.14) spawnParticle(duckProp.x + (Math.random() - 0.5) * 26, duckProp.y - 12, '♥', '#fde047', -1.0);
        } else {
          duckProp.beamPower = Math.max(0, duckProp.beamPower - dt * 3.5);
          duckProp.y += (H - 22 - duckProp.y) * 0.12;
          duckProp.x -= 3.4;
        }
      }

      bellVx = (bellVx + (targetX - bellX) * 0.08) * 0.84;
      bellVy = (bellVy + (targetY - bellY) * 0.08) * 0.84;
      bellX += bellVx;
      bellY += bellVy;

      bellScaleX += (1.0 - swimPulse * 0.045 - bellScaleX) * 0.15;
      bellScaleY += (1.0 + swimPulse * 0.045 - bellScaleY) * 0.15;

      for (let i = 0; i < NUM_NODES; i++) {
        const n = nodes[i];
        const restR = getDomeRestRadius(n.angle, swimPulse);
        n.vr += (restR - n.r) * 0.18;
        const prev = nodes[(i - 1 + NUM_NODES) % NUM_NODES];
        const next = nodes[(i + 1) % NUM_NODES];
        n.vr = (n.vr + ((prev.r + next.r) * 0.5 - n.r) * 0.22) * 0.82;
        n.r += n.vr;

        const cosA = Math.cos(n.angle + bellRotation);
        const sinA = Math.sin(n.angle + bellRotation);
        const yMod = sinA > 0 ? 0.72 : 1.02;
        n.x = bellX + cosA * n.r * bellScaleX;
        n.y = bellY + sinA * n.r * yMod * bellScaleY;
      }

      for (let t = 0; t < NUM_TENTACLES; t++) {
        const tent = tentacles[t];
        tent.pts[0].x = bellX + tent.norm * (bellRadius * 0.66) * bellScaleX;
        tent.pts[0].y = bellY + (bellRadius * 0.48 - Math.abs(tent.norm) * 4) * bellScaleY;
        for (let s = 1; s < SEGMENTS; s++) {
          const prev = tent.pts[s - 1];
          const cur = tent.pts[s];
          const ratio = s / (SEGMENTS - 1);
          const waveSpeed = currentState === 'dj_headphones' ? 9.0 : (currentState === 'electro_shock' ? 22.0 : 3.4);
          const waveX = Math.sin(time * waveSpeed - s * 0.55 + t * 1.1) * (tent.isFeeler ? 5.2 : 3.8) * ratio;
          let desiredX = prev.x + waveX * 0.38;
          let desiredY = prev.y + tent.segLen;
          if (tent.targetWeight > 0.05 && tent.targetX !== null) {
            const ik = Math.pow(ratio, 1.35) * tent.targetWeight;
            const arcOffset = Math.sin(ratio * Math.PI) * tent.norm * 14 * tent.targetWeight;
            desiredX = desiredX * (1 - ik) + (tent.targetX + arcOffset) * ik;
            desiredY = desiredY * (1 - ik) + tent.targetY * ik;
          }
          cur.vx = (cur.vx + (desiredX - cur.x) * 0.28) * 0.72;
          cur.vy = (cur.vy + (desiredY - cur.y) * 0.28) * 0.72;
          cur.x += cur.vx;
          cur.y += cur.vy;
        }
      }

      eye.idleLookTimer -= dt;
      if (eye.idleLookTimer <= 0) {
        eye.idleLookTimer = 1.6 + Math.random() * 2.4;
        eye.idleTargetX = (Math.random() - 0.5) * 14;
        eye.idleTargetY = (Math.random() - 0.5) * 9;
      }
      const lx = pointer.active ? (pointer.x - bellX) * 0.12 : eye.idleTargetX;
      const ly = pointer.active ? (pointer.y - bellY) * 0.12 : eye.idleTargetY;
      eye.lookX += (lx - eye.lookX) * 0.16;
      eye.lookY += (ly - eye.lookY) * 0.16;
      eye.x += (bellX + eye.lookX * 0.55 - eye.x) * 0.2;
      eye.y += (bellY - 5 + eye.lookY * 0.55 - eye.y) * 0.2;

      eye.blinkTimer -= dt;
      if (eye.blinkTimer <= 0) {
        eye.blink = 1.0;
        eye.blinkTimer = 2.6 + Math.random() * 3.2;
      }
      if (eye.blink > 0) eye.blink = Math.max(0, eye.blink - dt * 7.5);

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life++;
        p.alpha = 1 - p.life / p.maxLife;
        if (p.life >= p.maxLife) particles.splice(i, 1);
      }
    }

    function traceBellPath() {
      ctx.beginPath();
      const firstMidX = (nodes[NUM_NODES - 1].x + nodes[0].x) * 0.5;
      const firstMidY = (nodes[NUM_NODES - 1].y + nodes[0].y) * 0.5;
      ctx.moveTo(firstMidX, firstMidY);
      for (let i = 0; i < NUM_NODES; i++) {
        const next = nodes[(i + 1) % NUM_NODES];
        ctx.quadraticCurveTo(nodes[i].x, nodes[i].y, (nodes[i].x + next.x) * 0.5, (nodes[i].y + next.y) * 0.5);
      }
      ctx.closePath();
    }

    function drawTentacles(layerFilter) {
      for (let t = 0; t < NUM_TENTACLES; t++) {
        const tent = tentacles[t];
        if (tent.layer !== layerFilter) continue;
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(tent.pts[0].x, tent.pts[0].y);
        for (let s = 1; s < SEGMENTS - 1; s++) {
          ctx.quadraticCurveTo(tent.pts[s].x, tent.pts[s].y, (tent.pts[s].x + tent.pts[s + 1].x) * 0.5, (tent.pts[s].y + tent.pts[s + 1].y) * 0.5);
        }
        const tip = tent.pts[SEGMENTS - 1];
        ctx.lineTo(tip.x, tip.y);
        const grad = ctx.createLinearGradient(tent.pts[0].x, tent.pts[0].y, tip.x, tip.y);
        grad.addColorStop(0, currentTheme.tentacleBase);
        grad.addColorStop(1, currentTheme.tentacleTip);
        ctx.strokeStyle = grad;
        ctx.lineCap = 'round';
        ctx.lineWidth = tent.isFeeler ? 6.5 : 4.6;
        ctx.stroke();

        for (let s = 2; s < SEGMENTS; s += 2) {
          const pt = tent.pts[s];
          ctx.fillStyle = currentTheme.bioNode;
          ctx.globalAlpha = 0.45 + 0.5 * Math.sin(time * 5 - s * 0.9 + t);
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, tent.isFeeler ? 2.1 : 1.5, 0, Math.PI * 2);
          ctx.fill();
        }

        if (tent.isFeeler) {
          ctx.globalAlpha = 0.95;
          ctx.fillStyle = currentTheme.tentacleTip;
          ctx.beginPath();
          ctx.arc(tip.x, tip.y, 4.5, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.restore();
      }
    }

    function render() {
      ctx.clearRect(0, 0, W, H);

      ctx.save();
      const shGrad = ctx.createRadialGradient(bellX, H - 14, 2, bellX, H - 14, 42);
      shGrad.addColorStop(0, currentTheme.glow);
      shGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = shGrad;
      ctx.beginPath();
      ctx.ellipse(bellX, H - 14, 40, 7, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      if (duckProp.active) {
        ctx.save();
        if (duckProp.beamPower > 0.02) {
          const topY = bellY + 18;
          const botY = H - 10;
          const beamGrad = ctx.createLinearGradient(bellX, topY, bellX, botY);
          beamGrad.addColorStop(0, `rgba(103, 232, 249, ${0.42 * duckProp.beamPower})`);
          beamGrad.addColorStop(1, `rgba(217, 70, 239, ${0.06 * duckProp.beamPower})`);
          ctx.fillStyle = beamGrad;
          ctx.beginPath();
          ctx.moveTo(bellX - 18, topY);
          ctx.lineTo(bellX + 18, topY);
          ctx.lineTo(bellX + 44, botY);
          ctx.lineTo(bellX - 44, botY);
          ctx.closePath();
          ctx.fill();
        }
        ctx.translate(duckProp.x, duckProp.y);
        ctx.rotate(duckProp.duckSpin);
        ctx.fillStyle = '#facc15';
        ctx.beginPath();
        ctx.ellipse(0, 4, 11, 7.5, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(-5, -4, 6.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#f97316';
        ctx.beginPath();
        ctx.ellipse(-11.5, -3.5, 3.5, 2, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#0f172a';
        ctx.beginPath();
        ctx.arc(-6.8, -5.2, 1.4, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = 'rgba(186, 230, 253, 0.85)';
        ctx.fillStyle = 'rgba(186, 230, 253, 0.18)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(-5.5, -4, 9.8, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      }

      drawTentacles('back');

      ctx.save();
      traceBellPath();
      const bellGrad = ctx.createRadialGradient(bellX - 14, bellY - 18, 6, bellX, bellY, bellRadius * 1.18);
      bellGrad.addColorStop(0, currentTheme.core);
      bellGrad.addColorStop(0.58, currentTheme.mid);
      bellGrad.addColorStop(1, currentTheme.edge);
      ctx.fillStyle = bellGrad;
      ctx.fill();

      ctx.save();
      traceBellPath();
      ctx.clip();

      for (const b of bubbles) {
        const bx = bellX + Math.cos(b.angle + time * b.speed) * b.dist * bellScaleX;
        const by = bellY - 4 + Math.sin(b.angle * 1.3 + time * b.speed) * (b.dist * 0.65) * bellScaleY;
        ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
        ctx.beginPath();
        ctx.arc(bx, by, b.r, 0, Math.PI * 2);
        ctx.fill();
      }

      if (bobaProp.active) {
        for (const ip of bobaProp.insidePearls) {
          ctx.save();
          ctx.globalAlpha = ip.alpha;
          ctx.fillStyle = ip.color;
          ctx.beginPath();
          ctx.arc(ip.x, ip.y, 4.4, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        }
      }

      const ex = eye.x;
      const ey = eye.y;
      const r = eye.radius;
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(ex, ey, r, 0, Math.PI * 2);
      ctx.fill();

      const ix = ex + eye.lookX * 0.45;
      const iy = ey + eye.lookY * 0.45;
      ctx.fillStyle = currentTheme.irisOuter;
      ctx.beginPath();
      ctx.arc(ix, iy, r * 0.64, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = currentTheme.irisInner;
      ctx.beginPath();
      ctx.arc(ix, iy, r * 0.45, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#0f172a';
      ctx.beginPath();
      ctx.arc(ix, iy, r * 0.28, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(ix - 3.5, iy - 3.5, 2.8, 0, Math.PI * 2);
      ctx.fill();

      const lidClose = currentState === 'sleepy_drift' ? Math.max(0.58, eye.blink) : eye.blink;
      if (lidClose > 0.02) {
        ctx.fillStyle = currentTheme.edge;
        ctx.fillRect(ex - r - 2, ey - r - 2, (r + 2) * 2, (r * 2 + 4) * lidClose);
      }
      ctx.restore();

      traceBellPath();
      ctx.strokeStyle = currentTheme.rim;
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = 'rgba(255, 255, 255, 0.48)';
      ctx.beginPath();
      ctx.ellipse(bellX - 17 * bellScaleX, bellY - 22 * bellScaleY, 13, 5.5, -0.42, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      drawTentacles('front');

      if (bobaProp.active) {
        ctx.save();
        const cx = bobaProp.cupX;
        const cy = bobaProp.cupY;
        ctx.strokeStyle = '#f472b6';
        ctx.lineWidth = 4;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(cx - 2, cy + 6);
        ctx.lineTo(cx - 8, cy - 22);
        ctx.lineTo(bellX + 20, bellY + 2);
        ctx.stroke();

        ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
        ctx.strokeStyle = '#f8fafc';
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.moveTo(cx - 12, cy - 12);
        ctx.lineTo(cx + 12, cy - 12);
        ctx.lineTo(cx + 9, cy + 16);
        ctx.lineTo(cx - 9, cy + 16);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        const liqH = 24 * bobaProp.liquidLevel;
        ctx.fillStyle = 'rgba(217, 70, 239, 0.65)';
        ctx.fillRect(cx - 9, cy + 15 - liqH, 18, liqH);
        ctx.restore();
      }

      if (juggleProp.active) {
        ctx.save();
        for (const orb of juggleProp.orbs) {
          ctx.shadowColor = orb.glow;
          ctx.shadowBlur = 12;
          ctx.fillStyle = orb.color;
          ctx.beginPath();
          ctx.arc(orb.x, orb.y, 7.5, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.restore();
      }

      if (djProp.active) {
        ctx.save();
        const hy = djProp.headphoneY;
        const hx = bellX;
        const rx = bellRadius * 0.98 * bellScaleX;
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.arc(hx, hy + 4, rx + 2, Math.PI * 1.05, Math.PI * 1.95);
        ctx.stroke();
        for (const dir of [-1, 1]) {
          const ex = hx + dir * (rx + 1);
          ctx.fillStyle = '#0f172a';
          ctx.strokeStyle = currentTheme.tentacleTip;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.roundRect(ex - 6, hy - 7, 12, 26, 6);
          ctx.fill();
          ctx.stroke();
        }
        ctx.restore();
      }

      for (const p of particles) {
        ctx.save();
        ctx.globalAlpha = Math.max(0, p.alpha);
        ctx.fillStyle = p.color;
        ctx.font = `bold ${Math.round(13 * p.scale)}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(p.text, p.x, p.y);
        ctx.restore();
      }
    }

    canvas.addEventListener('pointermove', e => {
      const rect = canvas.getBoundingClientRect();
      pointer.x = (e.clientX - rect.left) * (W / rect.width);
      pointer.y = (e.clientY - rect.top) * (H / rect.height);
      pointer.active = true;
    });
    canvas.addEventListener('pointerleave', () => { pointer.active = false; });
    canvas.addEventListener('pointerdown', e => {
      if (e.button !== 0) return;
      const rect = canvas.getBoundingClientRect();
      const px = (e.clientX - rect.left) * (W / rect.width);
      const py = (e.clientY - rect.top) * (H / rect.height);
      const dist = Math.hypot(px - bellX, py - bellY);
      if (e.altKey || dist > bellRadius * 1.05) {
        document.title = 'LUMI_DRAG:' + Date.now();
      } else {
        bellVy -= 4.2;
        spawnParticle(bellX, bellY + 20, '✦', currentTheme.tentacleTip, 1.1);
      }
    });

    let last = performance.now();
    function loop(now) {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      updatePhysics(dt);
      render();
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  </script>
</body>
</html>
"""


def run_gtk_webkit():
    import gi
    gi.require_version("Gtk", "3.0")
    try:
        gi.require_version("WebKit2", "4.1")
    except ValueError:
        gi.require_version("WebKit2", "4.0")
    from gi.repository import Gtk, Gdk, WebKit2

    class LumiLinuxWidget(Gtk.Window):
        def __init__(self):
            super().__init__(title="Lumi Companion Widget")
            self.set_default_size(260, 255)
            self.set_decorated(False)
            self.set_keep_above(True)
            self.set_skip_taskbar_hint(True)
            self.set_skip_pager_hint(True)

            screen = self.get_screen()
            visual = screen.get_rgba_visual()
            if visual and screen.is_composited():
                self.set_visual(visual)
            self.set_app_paintable(True)

            self.webview = WebKit2.WebView()
            self.webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))
            self.webview.load_html(EMBEDDED_HTML, "file:///")
            self.webview.connect("notify::title", self.on_title_changed)
            self.webview.connect("button-press-event", self.on_button_press)

            self.add(self.webview)
            self.connect("destroy", Gtk.main_quit)
            self.show_all()

        def js(self, code):
            self.webview.run_javascript(code, None, None, None)

        def on_title_changed(self, webview, _param):
            title = webview.get_title() or ""
            if title.startswith("LUMI_DRAG:"):
                display = Gdk.Display.get_default()
                seat = display.get_default_seat()
                pointer = seat.get_pointer()
                _, x, y = pointer.get_position()
                self.begin_move_drag(1, int(x), int(y), Gtk.get_current_event_time())

        def on_button_press(self, _widget, event):
            if event.button == 3:
                self.show_context_menu(event)
                return True
            return False

        def show_context_menu(self, event):
            menu = Gtk.Menu()

            item_rand = Gtk.MenuItem(label="🎲 Sortear Animação Agora")
            item_rand.connect("activate", lambda _: self.js("window.triggerRandomNow()"))
            menu.append(item_rand)

            sub_anim = Gtk.Menu()
            item_anim = Gtk.MenuItem(label="🎬 Executar Animação")
            item_anim.set_submenu(sub_anim)
            for label, st in [
                ("🧋 Boba Tea Cósmico", "cosmic_boba"),
                ("🔮 Malabarismo de Orbes", "juggling_orbs"),
                ("🎧 DJ & Vinil Holográfico", "dj_headphones"),
                ("🛸 Abduzir Patinho Espacial", "abducting_duck"),
                ("🌀 Hipnose Bioluminescente", "hypnotic"),
                ("✨ Giro Feliz", "happy_spin"),
                ("⚡ Choque Elétrico", "electro_shock"),
                ("🌙 Deriva Sonolenta", "sleepy_drift"),
                ("🪼 Voltar à Flutuação Viva", "idle"),
            ]:
                mi = Gtk.MenuItem(label=label)
                mi.connect("activate", lambda _, s=st: self.js(f"window.setMascotState('{s}')"))
                sub_anim.append(mi)
            menu.append(item_anim)

            sub_theme = Gtk.Menu()
            item_theme = Gtk.MenuItem(label="🎨 Cores Abissais (Dual-Tone)")
            item_theme.set_submenu(sub_theme)
            for label, th in [
                ("🩷 Magenta Astral & Ciano", "astral"),
                ("💙 Abissal Elétrico & Lime", "abyssal"),
                ("💚 Aurora Boreal & Violeta", "aurora"),
                ("🧡 Supernova Solar & Plasma", "solaris"),
                ("🤍 Fantasma Lunar & Pérola", "phantom"),
            ]:
                mi = Gtk.MenuItem(label=label)
                mi.connect("activate", lambda _, t=th: self.js(f"window.setMascotTheme('{t}')"))
                sub_theme.append(mi)
            menu.append(item_theme)

            sub_freq = Gtk.Menu()
            item_freq = Gtk.MenuItem(label="⏱ Frequência Aleatória")
            item_freq.set_submenu(sub_freq)
            for label, mn, mx in [
                ("⚡ Rápida (8s a 16s)", 8, 16),
                ("🌿 Normal (16s a 36s)", 16, 36),
                ("🧘 Calma (45s a 90s)", 45, 90),
            ]:
                mi = Gtk.MenuItem(label=label)
                mi.connect("activate", lambda _, a=mn, b=mx: self.js(f"window.setRandomIntervalRange({a}, {b})"))
                sub_freq.append(mi)
            menu.append(item_freq)

            menu.append(Gtk.SeparatorMenuItem())
            item_quit = Gtk.MenuItem(label="❌ Fechar Lumi")
            item_quit.connect("activate", Gtk.main_quit)
            menu.append(item_quit)

            menu.show_all()
            menu.popup_at_pointer(event)

    LumiLinuxWidget()
    Gtk.main()


def run_pyqt():
    try:
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QColor, QAction
        from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        IS_QT6 = True
    except ImportError:
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QColor
        from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        IS_QT6 = False

    app = QApplication(sys.argv)

    class QtLumiWidget(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setFixedSize(260, 255)
            flags = (
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
            ) if IS_QT6 else (
                Qt.FramelessWindowHint
                | Qt.WindowStaysOnTopHint
                | Qt.Tool
            )
            self.setWindowFlags(flags)
            self.setAttribute(
                Qt.WidgetAttribute.WA_TranslucentBackground if IS_QT6 else Qt.WA_TranslucentBackground
            )

            self.view = QWebEngineView(self)
            self.view.page().setBackgroundColor(QColor(0, 0, 0, 0))
            self.view.setHtml(EMBEDDED_HTML)
            self.view.titleChanged.connect(self.on_title_changed)
            self.view.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu if IS_QT6 else Qt.CustomContextMenu
            )
            self.view.customContextMenuRequested.connect(self.show_context_menu)
            self.setCentralWidget(self.view)

        def js(self, code):
            self.view.page().runJavaScript(code)

        def on_title_changed(self, title):
            if title.startswith("LUMI_DRAG:") and hasattr(self, "windowHandle") and self.windowHandle():
                self.windowHandle().startSystemMove()

        def show_context_menu(self, pos):
            menu = QMenu(self)
            act_rand = QAction("🎲 Sortear Animação Agora", self)
            act_rand.triggered.connect(lambda: self.js("window.triggerRandomNow()"))
            menu.addAction(act_rand)

            sub_anim = menu.addMenu("🎬 Executar Animação")
            for label, st in [
                ("🧋 Boba Tea Cósmico", "cosmic_boba"),
                ("🔮 Malabarismo de Orbes", "juggling_orbs"),
                ("🎧 DJ & Vinil Holográfico", "dj_headphones"),
                ("🛸 Abduzir Patinho Espacial", "abducting_duck"),
                ("🌀 Hipnose Bioluminescente", "hypnotic"),
                ("✨ Giro Feliz", "happy_spin"),
                ("⚡ Choque Elétrico", "electro_shock"),
                ("🌙 Deriva Sonolenta", "sleepy_drift"),
                ("🪼 Voltar à Flutuação Viva", "idle"),
            ]:
                a = QAction(label, self)
                a.triggered.connect(lambda _c=False, s=st: self.js(f"window.setMascotState('{s}')"))
                sub_anim.addAction(a)

            sub_theme = menu.addMenu("🎨 Cores Abissais (Dual-Tone)")
            for label, th in [
                ("🩷 Magenta Astral & Ciano", "astral"),
                ("💙 Abissal Elétrico & Lime", "abyssal"),
                ("💚 Aurora Boreal & Violeta", "aurora"),
                ("🧡 Supernova Solar & Plasma", "solaris"),
                ("🤍 Fantasma Lunar & Pérola", "phantom"),
            ]:
                a = QAction(label, self)
                a.triggered.connect(lambda _c=False, t=th: self.js(f"window.setMascotTheme('{t}')"))
                sub_theme.addAction(a)

            menu.addSeparator()
            act_quit = QAction("❌ Fechar Lumi", self)
            act_quit.triggered.connect(app.quit)
            menu.addAction(act_quit)

            global_pos = self.view.mapToGlobal(pos)
            menu.exec(global_pos) if IS_QT6 else menu.exec_(global_pos)

    win = QtLumiWidget()
    win.show()
    sys.exit(app.exec() if IS_QT6 else app.exec_())


if __name__ == "__main__":
    try:
        run_gtk_webkit()
    except Exception:
        try:
            run_pyqt()
        except Exception as err:
            print(f"Erro ao iniciar Lumi Widget: {err}")
            sys.exit(1)
