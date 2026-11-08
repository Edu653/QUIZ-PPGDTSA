#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gloop - Mascote Alienígena Gelatinoso (Widget Nativo para Linux Desktop)
========================================================================
Arquivo único (100% autocontido, sem arquivos externos).
- Estado padrão: 'idle' (Idle Vivo com respiração, piscadas e olhares naturais)
- Eventos aleatórios: Executa animações espontâneas ('petting_chick', 'reading',
  'calculating', 'happy', 'curious', 'thinking', 'surprised') em intervalos
  aleatórios e retorna automaticamente ao 'idle'.
- Janela transparente, sem bordas (frameless), arrastável pela tela e com menu
  de contexto no botão direito do mouse.

Como executar no Linux:
  chmod +x gloop_widget.py
  ./gloop_widget.py

Dependências no Linux (usa automaticamente GTK3+WebKit2 ou PyQt6/PyQt5):
  Ubuntu/Debian/Mint/Pop!_OS:
    sudo apt install python3-gi gir1.2-webkit2-4.1
  Fedora:
    sudo dnf install python3-gobject webkit2gtk4.1
  Arch Linux:
    sudo pacman -S python-gobject webkit2gtk-4.1
"""

import sys

EMBEDDED_HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>Gloop Linux Widget</title>
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
      width: 250px;
      height: 250px;
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
      gap: 4px;
      padding: 3px 8px;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.78);
      border: 1px solid rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(6px);
      opacity: 0;
      transition: opacity 0.2s ease;
      pointer-events: none;
      white-space: nowrap;
      color: #e2e8f0;
      font-size: 11px;
    }
    #stage:hover #hud {
      opacity: 1;
      pointer-events: auto;
    }
    .hud-btn {
      background: none;
      border: none;
      color: #e2e8f0;
      cursor: pointer;
      font-size: 12px;
      padding: 1px 4px;
      border-radius: 4px;
    }
    .hud-btn:hover {
      background: rgba(255, 255, 255, 0.15);
    }
  </style>
</head>
<body>
  <div id="stage">
    <canvas id="mascotCanvas" width="250" height="240"></canvas>
    <div id="hud">
      <button class="hud-btn" title="Trocar Cor" id="themeBtn">🎨</button>
      <button class="hud-btn" title="Sortear Animação Agora" id="randomNowBtn">🎲</button>
      <button class="hud-btn" title="Pintinho" data-trig="petting_chick">🐥</button>
      <button class="hud-btn" title="Caderneta" data-trig="reading">🧐</button>
      <button class="hud-btn" title="Calculadora" data-trig="calculating">🧮</button>
    </div>
  </div>

  <script>
    const THEMES = {
      emerald: {
        core: 'rgba(167, 243, 208, 0.85)',
        mid: 'rgba(16, 185, 129, 0.68)',
        edge: 'rgba(4, 120, 87, 0.82)',
        rim: '#6ee7b7',
        glow: 'rgba(16, 185, 129, 0.32)',
        irisOuter: '#065f46',
        irisInner: '#34d399',
        tint: 'rgba(16, 185, 129, 0.22)'
      },
      cyan: {
        core: 'rgba(165, 243, 252, 0.85)',
        mid: 'rgba(6, 182, 212, 0.68)',
        edge: 'rgba(14, 116, 144, 0.82)',
        rim: '#67e8f9',
        glow: 'rgba(6, 182, 212, 0.32)',
        irisOuter: '#164e63',
        irisInner: '#38bdf8',
        tint: 'rgba(6, 182, 212, 0.22)'
      },
      nebula: {
        core: 'rgba(233, 213, 255, 0.85)',
        mid: 'rgba(147, 51, 234, 0.68)',
        edge: 'rgba(88, 28, 135, 0.84)',
        rim: '#d8b4fe',
        glow: 'rgba(147, 51, 234, 0.32)',
        irisOuter: '#3b0764',
        irisInner: '#f472b6',
        tint: 'rgba(147, 51, 234, 0.22)'
      },
      amber: {
        core: 'rgba(254, 240, 138, 0.86)',
        mid: 'rgba(245, 158, 11, 0.68)',
        edge: 'rgba(180, 83, 9, 0.82)',
        rim: '#fde047',
        glow: 'rgba(245, 158, 11, 0.32)',
        irisOuter: '#7c2d12',
        irisInner: '#fb923c',
        tint: 'rgba(245, 158, 11, 0.20)'
      },
      coral: {
        core: 'rgba(254, 205, 211, 0.85)',
        mid: 'rgba(244, 63, 94, 0.68)',
        edge: 'rgba(159, 18, 57, 0.82)',
        rim: '#fda4af',
        glow: 'rgba(244, 63, 94, 0.32)',
        irisOuter: '#881337',
        irisInner: '#38bdf8',
        tint: 'rgba(244, 63, 94, 0.22)'
      }
    };

    const THEME_KEYS = Object.keys(THEMES);
    const LCD_EXPRESSIONS = ['42', '3.14', '1+1=2', '99%', '∑x', '7×8', '808', '√2', '=100'];
    const MATH_SYMBOLS = ['+', '−', '×', '÷', '=', '%', 'π', '∑'];
    const NOTE_SYMBOLS = ['!', '?', '§', '✓', '⋯', '💡'];
    const CHICK_SYMBOLS = ['♥', '♪', '♥', '✨'];

    const RANDOM_EVENTS = [
      { state: 'petting_chick', duration: 7.0, weight: 3 },
      { state: 'reading',       duration: 7.5, weight: 3 },
      { state: 'calculating',   duration: 6.5, weight: 3 },
      { state: 'happy',         duration: 3.6, weight: 2 },
      { state: 'curious',       duration: 4.0, weight: 2 },
      { state: 'thinking',      duration: 4.2, weight: 2 },
      { state: 'surprised',     duration: 2.2, weight: 1 }
    ];

    class JellyAlienMascot {
      constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.w = canvas.width;
        this.h = canvas.height;
        this.cx = this.w / 2 - 6;
        this.cy = this.h / 2 + 10;
        this.baseRadius = 62;

        this.themeIndex = 0;
        this.theme = THEMES.emerald;
        this.state = 'idle';
        this.squishFactor = 1.0;
        this.followCursor = true;
        this.time = 0;

        this.autoRandom = true;
        this.minIdleSeconds = 16;
        this.maxIdleSeconds = 36;
        this.nextEventTimer = this._randomIdleTime();
        this.activeEventRemaining = 0;
        this.lastRandomState = '';

        this.bodyX = this.cx;
        this.bodyY = this.cy;
        this.bodyVX = 0;
        this.bodyVY = 0;

        this.numNodes = 24;
        this.nodes = [];
        for (let i = 0; i < this.numNodes; i++) {
          const angle = (i / this.numNodes) * Math.PI * 2;
          this.nodes.push({
            angle,
            r: this.baseRadius,
            vr: 0,
            x: this.cx + Math.cos(angle) * this.baseRadius,
            y: this.cy + Math.sin(angle) * this.baseRadius
          });
        }

        this.eye = {
          x: 0, y: -2, vx: 0, vy: 0, targetX: 0, targetY: -2,
          lookX: 0, lookY: 0, targetLookX: 0, targetLookY: 0,
          radius: 21, depth: 0, targetDepth: 0,
          pupilScale: 1.0, targetPupilScale: 1.0,
          blink: 0, isBlinking: false, blinkTimer: 2.2, saccadeTimer: 1.2
        };

        this.calc = {
          phase: 'none', x: 16, y: -140, vx: 0, vy: 0,
          angle: -0.25, vAngle: 0, activeBtn: -1, btnTimer: 0.4,
          screenText: '0.', pulseWave: 0, glanceUpTimer: 0
        };

        this.reader = {
          monoclePhase: 'none', mx: -14, my: -150, mvx: 0, mvy: 0,
          mAngle: 0.2, chainSwing: 0, chainVSwing: 0,
          padPhase: 'none', px: 18, py: -185, pvx: 0, pvy: 0,
          pAngle: -0.15, pvAngle: 0,
          currentLine: 0, lineProgress: 0, isFlipping: false, flipProgress: 0, pageNumber: 1
        };

        this.chickScene = {
          phase: 'none', timer: 0, chickX: 270, chickY: 0,
          walkCycle: 0, chickSquash: 0, happyEyes: false,
          armExtension: 0, handX: 0, handY: 0, patCycle: 0, heartTimer: 0
        };

        this.bubbles = Array.from({ length: 9 }, (_, i) => ({
          x: (Math.random() - 0.5) * 75,
          y: (Math.random() - 0.5) * 75,
          r: 2 + (i % 4) * 1.4,
          alpha: 0.25 + (i % 3) * 0.18,
          phase: Math.random() * Math.PI * 2
        }));

        this.particles = [];
        this.pointer = { x: this.cx, y: this.cy, active: false };
      }

      _randomIdleTime() {
        return this.minIdleSeconds + Math.random() * (this.maxIdleSeconds - this.minIdleSeconds);
      }

      setRandomIntervalRange(minSec, maxSec) {
        this.minIdleSeconds = minSec;
        this.maxIdleSeconds = maxSec;
        if (this.state === 'idle') {
          this.nextEventTimer = this._randomIdleTime();
        }
      }

      triggerRandomAnimation() {
        const candidates = RANDOM_EVENTS.filter(e => e.state !== this.lastRandomState);
        const totalWeight = candidates.reduce((acc, item) => acc + item.weight, 0);
        let pick = Math.random() * totalWeight;
        let chosen = candidates[0];
        for (const item of candidates) {
          pick -= item.weight;
          if (pick <= 0) {
            chosen = item;
            break;
          }
        }
        this.lastRandomState = chosen.state;
        this.activeEventRemaining = chosen.duration;
        this.setState(chosen.state, chosen.duration);
      }

      setState(newState, durationSeconds = null) {
        const prevState = this.state;
        this.state = newState;

        if (newState === 'idle') {
          this.activeEventRemaining = 0;
          this.nextEventTimer = this._randomIdleTime();
        } else if (durationSeconds !== null) {
          this.activeEventRemaining = durationSeconds;
        } else {
          const found = RANDOM_EVENTS.find(e => e.state === newState);
          this.activeEventRemaining = found ? found.duration : 6.0;
        }

        if (prevState === 'calculating' && newState !== 'calculating' &&
            (this.calc.phase === 'submerged' || this.calc.phase === 'falling')) {
          this.calc.phase = 'ejecting';
          this.calc.vy = -9.5;
          this.calc.vx = 2.2;
          this.calc.vAngle = 0.14;
          this.poke(this.bodyX, this.bodyY - this.baseRadius, -10);
        }

        if (prevState === 'reading' && newState !== 'reading' &&
            (this.reader.monoclePhase === 'submerged' || this.reader.padPhase === 'submerged' ||
             this.reader.monoclePhase === 'falling' || this.reader.padPhase === 'falling')) {
          this.reader.monoclePhase = 'ejecting';
          this.reader.mvy = -9.0;
          this.reader.mvx = -2.4;
          this.reader.padPhase = 'ejecting';
          this.reader.pvy = -9.5;
          this.reader.pvx = 2.5;
          this.reader.pvAngle = 0.15;
          this.poke(this.bodyX, this.bodyY - this.baseRadius, -10);
        }

        if (prevState === 'petting_chick' && newState !== 'petting_chick' && this.chickScene.phase !== 'none') {
          this.chickScene.phase = 'walking_past';
          this.chickScene.happyEyes = false;
        }

        if (newState === 'petting_chick') {
          const cs = this.chickScene;
          cs.phase = 'approaching';
          cs.timer = 0;
          cs.chickX = this.w + 22;
          cs.chickY = this.cy + this.baseRadius + 10;
          cs.walkCycle = 0;
          cs.chickSquash = 0;
          cs.happyEyes = false;
          cs.armExtension = 0;
          cs.patCycle = 0;
          cs.heartTimer = 0.25;
          this.eye.targetPupilScale = 1.28;
          this.eye.targetDepth = 0.7;
          return;
        }

        if (newState === 'reading') {
          const r = this.reader;
          r.monoclePhase = 'falling';
          r.mx = -14;
          r.my = -this.bodyY - 25;
          r.mvx = 0.3;
          r.mvy = 2.4;
          r.mAngle = -0.3;
          r.chainSwing = 0.4;
          r.chainVSwing = 0;

          r.padPhase = 'falling';
          r.px = 18;
          r.py = -this.bodyY - 68;
          r.pvx = -0.3;
          r.pvy = 2.0;
          r.pAngle = 0.32;
          r.pvAngle = -0.03;

          r.currentLine = 0;
          r.lineProgress = 0;
          r.isFlipping = false;
          r.flipProgress = 0;

          this.eye.targetPupilScale = 0.82;
          this.eye.targetDepth = 0.5;
          return;
        }

        if (newState === 'calculating') {
          this.calc.phase = 'falling';
          this.calc.x = 14 + (Math.random() - 0.5) * 8;
          this.calc.y = -this.bodyY - 35;
          this.calc.vx = (Math.random() - 0.5) * 1.2;
          this.calc.vy = 2.2;
          this.calc.angle = -0.35;
          this.calc.vAngle = 0.04;
          this.calc.screenText = '0.';
          this.calc.activeBtn = -1;
          this.calc.btnTimer = 0.35;
          this.calc.pulseWave = 0;

          this.eye.targetPupilScale = 0.78;
          this.eye.targetDepth = 0.4;
          return;
        }

        if (newState === 'surprised') {
          this.poke(this.bodyX, this.bodyY + 40, -18);
          this.eye.targetPupilScale = 0.55;
          this.eye.targetDepth = 0.85;
          this.eye.targetX = 0;
          this.eye.targetY = -4;
        } else if (newState === 'happy') {
          this.bodyVY = -7.5;
          this.eye.targetPupilScale = 1.25;
        } else if (newState === 'curious') {
          this.eye.targetPupilScale = 1.38;
          this.eye.targetDepth = 0.9;
        } else if (newState === 'sleepy') {
          this.eye.targetPupilScale = 0.8;
          this.eye.targetDepth = -0.5;
        } else {
          this.eye.targetPupilScale = 1.0;
          this.eye.targetDepth = 0.0;
        }
      }

      setTheme(name) {
        if (THEMES[name]) this.theme = THEMES[name];
      }

      nextTheme() {
        this.themeIndex = (this.themeIndex + 1) % THEME_KEYS.length;
        this.theme = THEMES[THEME_KEYS[this.themeIndex]];
      }

      poke(px, py, strength = 15) {
        const dx = this.bodyX - px;
        const dy = this.bodyY - py;
        const dist = Math.hypot(dx, dy) || 1;
        this.bodyVX += (dx / dist) * 3.8 * this.squishFactor;
        this.bodyVY += (dy / dist) * 3.8 * this.squishFactor - 2.5;

        const clickAngle = Math.atan2(py - this.bodyY, px - this.bodyX);
        for (const node of this.nodes) {
          let diff = Math.atan2(Math.sin(node.angle - clickAngle), Math.cos(node.angle - clickAngle));
          const influence = Math.exp(-(diff * diff) / 0.55);
          node.vr -= influence * strength * this.squishFactor;
        }

        this.eye.vx += (dx / dist) * 6.5;
        this.eye.vy += (dy / dist) * 6.5;
        this.eye.blink = 0.65;

        if (this.calc.phase === 'submerged') {
          this.calc.vx -= (dx / dist) * 5.0;
          this.calc.vy -= (dy / dist) * 5.0;
          this.calc.vAngle += (Math.random() - 0.5) * 0.25;
        }
        if (this.reader.padPhase === 'submerged') {
          this.reader.pvx -= (dx / dist) * 4.8;
          this.reader.pvy -= (dy / dist) * 4.8;
          this.reader.pvAngle += (Math.random() - 0.5) * 0.22;
          this.reader.chainVSwing += (dx / dist) * 0.18;
        }
      }

      spawnSplash(offsetX) {
        for (let i = 0; i < 6; i++) {
          const ang = -Math.PI * 0.5 + (Math.random() - 0.5) * 1.3;
          const spd = 2 + Math.random() * 3.2;
          this.particles.push({
            type: 'droplet',
            x: this.bodyX + offsetX + (Math.random() - 0.5) * 12,
            y: this.bodyY - this.baseRadius + 6,
            vx: Math.cos(ang) * spd,
            vy: Math.sin(ang) * spd - 1.4,
            gravity: 0.18,
            r: 2.2 + Math.random() * 2.2,
            alpha: 0.85,
            decay: 0.026
          });
        }
      }

      update(dt) {
        this.time += dt;
        const t = this.time;

        if (this.autoRandom) {
          if (this.state === 'idle') {
            this.nextEventTimer -= dt;
            if (this.nextEventTimer <= 0) {
              this.triggerRandomAnimation();
            }
          } else if (this.state !== 'petting_chick') {
            this.activeEventRemaining -= dt;
            if (this.activeEventRemaining <= 0) {
              this.setState('idle');
            }
          }
        }

        let floatTargetX = this.cx;
        let floatTargetY = this.cy + Math.sin(t * 2.4) * 5;

        if (this.state === 'happy') {
          const bounceWave = Math.abs(Math.sin(t * 5.2));
          floatTargetY = this.cy + 8 - bounceWave * 22;
        } else if (this.state === 'petting_chick' &&
                   (this.chickScene.phase === 'extending' || this.chickScene.phase === 'petting')) {
          floatTargetX = this.cx + 5;
          floatTargetY = this.cy + 4 + Math.sin(t * 3.0) * 2.5;
        } else if (this.state === 'thinking' || this.state === 'calculating' || this.state === 'reading') {
          floatTargetX = this.cx + Math.cos(t * 1.8) * 3.0;
          floatTargetY = this.cy + Math.sin(t * 2.8) * 3.5;
        } else if (this.state === 'sleepy') {
          floatTargetY = this.cy + 16;
        }

        const ax = (floatTargetX - this.bodyX) * 0.12;
        const ay = (floatTargetY - this.bodyY) * 0.12;
        this.bodyVX = (this.bodyVX + ax) * 0.84;
        this.bodyVY = (this.bodyVY + ay) * 0.84;
        this.bodyX += this.bodyVX;
        this.bodyY += this.bodyVY;

        this.updateCalculator(dt, t);
        this.updateReader(dt, t);
        this.updateChickScene(dt, t);
        this.updateEyeBehavior(dt, t);

        const maxEyeDist = 26;
        const eyeAngle = Math.atan2(this.eye.y, this.eye.x);
        const eyeDistRatio = Math.min(1, Math.hypot(this.eye.x, this.eye.y) / maxEyeDist);

        let propAngle = 0;
        let propDistRatio = 0;
        if (this.calc.phase === 'submerged') {
          propAngle = Math.atan2(this.calc.y, this.calc.x);
          propDistRatio = Math.min(1, Math.hypot(this.calc.x, this.calc.y) / 28);
        } else if (this.reader.padPhase === 'submerged') {
          propAngle = Math.atan2(this.reader.py, this.reader.px);
          propDistRatio = Math.min(1, Math.hypot(this.reader.px, this.reader.py) / 28);
        }

        const armExt = this.chickScene.armExtension;

        for (let i = 0; i < this.numNodes; i++) {
          const node = this.nodes[i];
          const a = node.angle;

          let targetR = this.baseRadius
            + Math.sin(t * 2.6 + a * 2) * (2.6 * this.squishFactor)
            + Math.cos(t * 4.1 - a * 3) * (1.8 * this.squishFactor);

          const stretchY = Math.sin(a);
          targetR += (this.bodyVY * 0.9 * this.squishFactor) * (stretchY * stretchY - 0.5);

          if (this.state === 'sleepy') {
            targetR += Math.sin(a) > 0.2 ? Math.sin(a) * 10 : -4;
          } else if (this.state === 'surprised') {
            targetR += Math.sin(t * 18 + a * 6) * 2.8;
          }

          const angleDiff = Math.atan2(Math.sin(a - eyeAngle), Math.cos(a - eyeAngle));
          targetR += Math.exp(-(angleDiff * angleDiff) / 0.65) * eyeDistRatio * 9.5 * this.squishFactor;

          if (propDistRatio > 0) {
            const pDiff = Math.atan2(Math.sin(a - propAngle), Math.cos(a - propAngle));
            targetR += Math.exp(-(pDiff * pDiff) / 0.55) * propDistRatio * 8.5 * this.squishFactor;
          }

          if (armExt > 0.01) {
            const armBaseAngle = 0.08;
            const armDiff = Math.atan2(Math.sin(a - armBaseAngle), Math.cos(a - armBaseAngle));
            targetR += Math.exp(-(armDiff * armDiff) / 0.35) * armExt * 14 * this.squishFactor;
          }

          const springK = 0.16 / Math.max(0.5, this.squishFactor * 0.85);
          node.vr = (node.vr + (targetR - node.r) * springK) * 0.82;
        }

        const neighborPull = 0.22;
        const deltas = new Array(this.numNodes).fill(0);
        for (let i = 0; i < this.numNodes; i++) {
          const prev = this.nodes[(i - 1 + this.numNodes) % this.numNodes];
          const next = this.nodes[(i + 1) % this.numNodes];
          deltas[i] = ((prev.r + next.r) * 0.5 - this.nodes[i].r) * neighborPull;
        }
        for (let i = 0; i < this.numNodes; i++) {
          const node = this.nodes[i];
          node.vr += deltas[i];
          node.r += node.vr;
          node.x = this.bodyX + Math.cos(node.angle) * node.r;
          node.y = this.bodyY + Math.sin(node.angle) * node.r;
        }

        for (const b of this.bubbles) {
          b.y -= 0.18;
          b.x += Math.sin(t * 1.8 + b.phase) * 0.15 - this.bodyVX * 0.18 + this.eye.vx * 0.08;
          b.y += -this.bodyVY * 0.18 + this.eye.vy * 0.08;

          const d = Math.hypot(b.x, b.y);
          if (d > this.baseRadius * 0.72) {
            const ang = Math.atan2(b.y, b.x) + Math.PI * 0.85;
            b.x = Math.cos(ang) * (this.baseRadius * 0.55);
            b.y = Math.sin(ang) * (this.baseRadius * 0.55);
          }
        }

        if (this.state === 'sleepy' && Math.random() < 0.04) {
          this.particles.push({
            type: 'text',
            text: 'Z',
            x: this.bodyX + 18 + (Math.random() - 0.5) * 10,
            y: this.bodyY - 35,
            vy: -0.6,
            vx: 0.25,
            alpha: 0.9,
            size: 10 + Math.random() * 4
          });
        }
        for (let i = this.particles.length - 1; i >= 0; i--) {
          const p = this.particles[i];
          p.x += p.vx;
          p.y += p.vy;
          if (p.gravity) p.vy += p.gravity;
          p.alpha -= p.decay || 0.014;
          if (p.alpha <= 0) this.particles.splice(i, 1);
        }
      }

      updateChickScene(dt, _t) {
        const cs = this.chickScene;
        if (cs.phase === 'none') return;

        const groundY = this.cy + this.baseRadius + 10;
        const stopX = this.cx + this.baseRadius + 25;

        if (cs.phase === 'approaching') {
          cs.walkCycle += dt * 15;
          cs.chickX -= 52 * dt;
          cs.chickY = groundY - Math.abs(Math.sin(cs.walkCycle)) * 4.5;
          cs.chickSquash += (0 - cs.chickSquash) * 0.2;
          cs.armExtension += (0 - cs.armExtension) * 0.2;

          if (cs.chickX <= stopX) {
            cs.chickX = stopX;
            cs.chickY = groundY;
            cs.phase = 'extending';
            cs.timer = 0;
          }
        } else if (cs.phase === 'extending') {
          cs.timer += dt;
          cs.armExtension = Math.min(1, cs.timer / 0.65);
          cs.chickY = groundY;
          cs.chickSquash += (0 - cs.chickSquash) * 0.2;

          if (cs.armExtension >= 1) {
            cs.phase = 'petting';
            cs.timer = 0;
            cs.patCycle = 0;
            cs.happyEyes = true;
          }
        } else if (cs.phase === 'petting') {
          cs.timer += dt;
          cs.patCycle += dt * 9.5;
          cs.armExtension = 1.0;

          const patDown = Math.max(0, Math.sin(cs.patCycle));
          cs.chickSquash = patDown * 0.24;
          cs.chickY = groundY;

          cs.heartTimer -= dt;
          if (cs.heartTimer <= 0) {
            cs.heartTimer = 0.48;
            const sym = CHICK_SYMBOLS[Math.floor(Math.random() * CHICK_SYMBOLS.length)];
            this.particles.push({
              type: 'text',
              text: sym,
              color: sym === '♥' ? '#fb7185' : '#fde047',
              x: cs.chickX + (Math.random() - 0.5) * 14,
              y: cs.chickY - 30,
              vx: (Math.random() - 0.5) * 0.45,
              vy: -0.95,
              alpha: 0.98,
              size: 12 + Math.random() * 2,
              decay: 0.015
            });
          }

          if (cs.timer >= 2.3) {
            cs.phase = 'retracting';
            cs.timer = 0;
          }
        } else if (cs.phase === 'retracting') {
          cs.timer += dt;
          cs.armExtension = Math.max(0, 1 - cs.timer / 0.55);
          cs.chickSquash += (0 - cs.chickSquash) * 0.25;

          if (cs.armExtension <= 0) {
            cs.armExtension = 0;
            cs.phase = 'walking_past';
            cs.timer = 0;
            this.nodes[0].vr -= 6 * this.squishFactor;
            this.nodes[1].vr -= 4 * this.squishFactor;
            this.nodes[23].vr -= 4 * this.squishFactor;
          }
        } else if (cs.phase === 'walking_past') {
          cs.walkCycle += dt * 16;
          cs.chickX -= 62 * dt;
          cs.chickY = groundY - Math.abs(Math.sin(cs.walkCycle)) * 5.0;
          cs.chickSquash = 0;
          cs.armExtension += (0 - cs.armExtension) * 0.25;

          if (cs.chickX < -32) {
            cs.phase = 'none';
            if (this.state === 'petting_chick') {
              this.setState('idle');
            }
          }
        }

        const shoulderX = this.bodyX + this.baseRadius * 0.72;
        const shoulderY = this.bodyY + 4;
        const patOffsetX = cs.phase === 'petting' ? Math.cos(cs.patCycle) * 3.5 : 0;
        const patOffsetY = cs.phase === 'petting' ? Math.sin(cs.patCycle) * 5.5 : 0;

        const targetHandX = cs.chickX - 2 + patOffsetX;
        const targetHandY = cs.chickY - 26 + patOffsetY;

        const ease = cs.armExtension * cs.armExtension * (3 - 2 * cs.armExtension);
        cs.handX = shoulderX + (targetHandX - shoulderX) * ease;
        cs.handY = shoulderY + (targetHandY - shoulderY) * ease;
      }

      updateReader(dt, t) {
        const r = this.reader;

        if (r.monoclePhase === 'falling') {
          r.mvy += 0.46;
          r.mx += r.mvx;
          r.my += r.mvy;
          r.mAngle *= 0.96;

          if (r.my >= -this.baseRadius * 0.62) {
            r.monoclePhase = 'submerged';
            this.poke(this.bodyX + r.mx, this.bodyY - this.baseRadius, 18);
            this.bodyVY += 3.2;
            r.mvy *= 0.25;
            this.spawnSplash(r.mx);
          }
        } else if (r.monoclePhase === 'submerged') {
          const targetMX = this.eye.x + this.eye.lookX * 0.35;
          const targetMY = this.eye.y + this.eye.lookY * 0.25;
          r.mvx = (r.mvx + (targetMX - r.mx) * 0.24) * 0.75;
          r.mvy = (r.mvy + (targetMY - r.my) * 0.24) * 0.75;
          r.mx += r.mvx;
          r.my += r.mvy;
          r.mAngle += (0 - r.mAngle) * 0.15;

          const chainTargetAngle = -r.mvx * 0.08 + Math.sin(t * 2.6) * 0.08;
          r.chainVSwing = (r.chainVSwing + (chainTargetAngle - r.chainSwing) * 0.12) * 0.85;
          r.chainSwing += r.chainVSwing;
        } else if (r.monoclePhase === 'ejecting') {
          r.mvy += 0.42;
          r.mx += r.mvx;
          r.my += r.mvy;
          r.mAngle -= 0.08;
          if (r.my > 160) r.monoclePhase = 'none';
        }

        if (r.padPhase === 'falling') {
          r.pvy += 0.46;
          r.px += r.pvx;
          r.py += r.pvy;
          r.pAngle += r.pvAngle;

          if (r.py >= -this.baseRadius * 0.62) {
            r.padPhase = 'submerged';
            this.poke(this.bodyX + r.px, this.bodyY - this.baseRadius, 20);
            this.bodyVY += 3.8;
            r.pvy *= 0.28;
            r.pvx = 1.2;
            this.spawnSplash(r.px);
          }
        } else if (r.padPhase === 'submerged') {
          const targetPX = 19 + Math.cos(t * 2.0) * 2.2;
          const targetPY = 5 + Math.sin(t * 2.8) * 3.5;
          const targetPAngle = -0.16 + Math.sin(t * 2.2) * 0.06;

          r.pvx = (r.pvx + (targetPX - r.px) * 0.09 - this.bodyVX * 0.12) * 0.82;
          r.pvy = (r.pvy + (targetPY - r.py) * 0.09 - this.bodyVY * 0.12) * 0.82;
          r.px += r.pvx;
          r.py += r.pvy;

          r.pvAngle = (r.pvAngle + (targetPAngle - r.pAngle) * 0.12) * 0.80;
          r.pAngle += r.pvAngle;

          if (!r.isFlipping) {
            r.lineProgress += dt * 1.55;
            if (r.lineProgress >= 1.0) {
              r.lineProgress = 0;
              r.currentLine++;
              this.eye.vy += 0.8;

              if (r.currentLine >= 4) {
                r.isFlipping = true;
                r.flipProgress = 0;

                r.pvy -= 2.2;
                r.pvx += 1.4;
                r.pvAngle -= 0.16;
                this.eye.vy -= 2.0;
                this.nodes[0].vr += 2.0 * this.squishFactor;

                const sym = NOTE_SYMBOLS[Math.floor(Math.random() * NOTE_SYMBOLS.length)];
                this.particles.push({
                  type: 'text',
                  text: sym,
                  x: this.bodyX + r.px + (Math.random() - 0.5) * 10,
                  y: this.bodyY + r.py - 18,
                  vx: (Math.random() - 0.5) * 0.4,
                  vy: -0.85,
                  alpha: 0.95,
                  size: 11 + Math.random() * 2,
                  decay: 0.015
                });
              }
            }
          } else {
            r.flipProgress += dt * 2.2;
            if (r.flipProgress >= 1.0) {
              r.flipProgress = 0;
              r.isFlipping = false;
              r.currentLine = 0;
              r.lineProgress = 0;
              r.pageNumber++;
            }
          }
        } else if (r.padPhase === 'ejecting') {
          r.pvy += 0.42;
          r.px += r.pvx;
          r.py += r.pvy;
          r.pAngle += r.pvAngle;
          if (r.py > 160) r.padPhase = 'none';
        }
      }

      updateCalculator(dt, t) {
        const c = this.calc;
        if (c.phase === 'none') return;

        if (c.phase === 'falling') {
          c.vy += 0.48;
          c.x += c.vx;
          c.y += c.vy;
          c.angle += c.vAngle;

          if (c.y >= -this.baseRadius * 0.62) {
            c.phase = 'submerged';
            this.poke(this.bodyX + c.x, this.bodyY - this.baseRadius, 22);
            this.bodyVY += 4.5;

            c.vy *= 0.28;
            c.vx = 1.5;
            c.vAngle = 0.08;
            this.spawnSplash(c.x);
          }
        } else if (c.phase === 'submerged') {
          const targetX = 19 + Math.cos(t * 2.2) * 2.5;
          const targetY = 2 + Math.sin(t * 3.1) * 4.5;
          const targetAngle = -0.18 + Math.sin(t * 2.5) * 0.08;

          c.vx = (c.vx + (targetX - c.x) * 0.09 - this.bodyVX * 0.12) * 0.82;
          c.vy = (c.vy + (targetY - c.y) * 0.09 - this.bodyVY * 0.12) * 0.82;
          c.x += c.vx;
          c.y += c.vy;

          c.vAngle = (c.vAngle + (targetAngle - c.angle) * 0.12) * 0.80;
          c.angle += c.vAngle;

          c.btnTimer -= dt;
          if (c.btnTimer <= 0) {
            c.btnTimer = 0.38 + Math.random() * 0.32;
            c.activeBtn = Math.floor(Math.random() * 9);
            c.screenText = LCD_EXPRESSIONS[Math.floor(Math.random() * LCD_EXPRESSIONS.length)];
            c.pulseWave = 1.0;

            this.eye.vx += 2.6;
            this.eye.vy += (Math.random() - 0.5) * 2.2;

            c.vx += 1.9;
            c.vy += (Math.random() - 0.5) * 1.4;
            c.vAngle += (Math.random() - 0.4) * 0.14;

            this.nodes[0].vr += 2.2 * this.squishFactor;
            this.nodes[1].vr += 1.5 * this.squishFactor;

            const sym = MATH_SYMBOLS[Math.floor(Math.random() * MATH_SYMBOLS.length)];
            this.particles.push({
              type: 'text',
              text: sym,
              x: this.bodyX + c.x + (Math.random() - 0.5) * 14,
              y: this.bodyY + c.y - 16,
              vx: (Math.random() - 0.5) * 0.5,
              vy: -0.9 - Math.random() * 0.4,
              alpha: 0.95,
              size: 11 + Math.random() * 3,
              decay: 0.015
            });
          }

          if (c.pulseWave > 0) {
            c.pulseWave = Math.max(0, c.pulseWave - dt * 3.2);
          }
        } else if (c.phase === 'ejecting') {
          c.vy += 0.42;
          c.x += c.vx;
          c.y += c.vy;
          c.angle += c.vAngle;
          if (c.y > 160) {
            c.phase = 'none';
          }
        }
      }

      updateEyeBehavior(dt, t) {
        const eye = this.eye;

        if (this.state === 'sleepy') {
          eye.blink += (0.95 - eye.blink) * 0.1;
        } else {
          eye.blinkTimer -= dt;
          if (eye.blinkTimer <= 0 && !eye.isBlinking) {
            eye.isBlinking = true;
            eye.blinkTimer = 2.4 + Math.random() * 3.5;
          }
          if (eye.isBlinking) {
            eye.blink += 0.35;
            if (eye.blink >= 1) {
              eye.blink = 1;
              eye.isBlinking = false;
            }
          } else {
            eye.blink += (0 - eye.blink) * 0.25;
          }
        }

        if (this.state === 'petting_chick' && this.chickScene.phase !== 'none') {
          const cs = this.chickScene;
          const dx = cs.chickX - this.bodyX;
          const dy = (cs.chickY - 10) - this.bodyY;
          const ang = Math.atan2(dy, dx);
          const dist = Math.hypot(dx, dy);

          eye.targetX = Math.cos(ang) * Math.min(20, dist * 0.25);
          eye.targetY = Math.sin(ang) * Math.min(14, dist * 0.22);
          eye.targetLookX = Math.cos(ang) * Math.min(7.5, dist * 0.11);
          eye.targetLookY = Math.sin(ang) * Math.min(6.5, dist * 0.11);
          eye.targetDepth = 0.75;
          eye.targetPupilScale = cs.phase === 'petting' ? 1.32 : 1.18;
        } else if (this.state === 'reading') {
          const r = this.reader;
          if (r.monoclePhase === 'falling' || r.padPhase === 'falling') {
            eye.targetX = -6;
            eye.targetY = -14;
            eye.targetLookX = 0;
            eye.targetLookY = -9;
            eye.targetPupilScale = 0.75;
          } else if (r.padPhase === 'submerged') {
            eye.targetX = -16 + Math.sin(t * 2.2) * 1.8;
            eye.targetY = -3 + Math.cos(t * 2.0) * 2.2;
            eye.targetDepth = 0.6;

            if (r.isFlipping) {
              const flipArc = Math.sin(r.flipProgress * Math.PI);
              eye.targetLookX = 5.5;
              eye.targetLookY = 2 - flipArc * 8;
              eye.targetPupilScale = 0.92;
            } else {
              const scanX = (r.lineProgress - 0.5) * 4.2;
              const lineY = (r.currentLine - 1.5) * 2.2;
              eye.targetLookX = 5.8 + scanX;
              eye.targetLookY = 1.8 + lineY;
              eye.targetPupilScale = 0.82;
            }
          }
        } else if (this.state === 'calculating') {
          if (this.calc.phase === 'falling') {
            eye.targetX = this.calc.x * 0.35;
            eye.targetY = -16;
            eye.targetLookX = (this.calc.x - eye.x) * 0.25;
            eye.targetLookY = -9;
            eye.targetPupilScale = 0.72;
          } else if (this.calc.phase === 'submerged') {
            eye.targetX = -17 + Math.sin(t * 3.0) * 2;
            eye.targetY = -2 + Math.cos(t * 2.4) * 3;
            eye.targetDepth = 0.55;

            this.calc.glanceUpTimer -= dt;
            if (this.calc.glanceUpTimer <= -0.35) {
              this.calc.glanceUpTimer = 1.6 + Math.random() * 1.2;
            }

            if (this.calc.glanceUpTimer < 0) {
              eye.targetLookX = 2;
              eye.targetLookY = -7;
              eye.targetPupilScale = 0.95;
            } else {
              const dx = this.calc.x - eye.x;
              const dy = this.calc.y - eye.y;
              const scanOffset = Math.sin(t * 14) * 2.2;
              eye.targetLookX = Math.min(8.5, dx * 0.24) + scanOffset * 0.4;
              eye.targetLookY = dy * 0.22 + (this.calc.activeBtn % 3 - 1) * 2.2;
              eye.targetPupilScale = 0.80;
            }
          }
        } else if (this.followCursor && this.pointer.active && this.state !== 'sleepy') {
          const dx = this.pointer.x - this.bodyX;
          const dy = this.pointer.y - this.bodyY;
          const dist = Math.hypot(dx, dy);
          const maxFloat = this.state === 'curious' ? 25 : 19;
          const factor = Math.min(maxFloat, dist * 0.28);
          const ang = Math.atan2(dy, dx);

          eye.targetX = Math.cos(ang) * factor;
          eye.targetY = Math.sin(ang) * factor;
          eye.targetLookX = Math.cos(ang) * Math.min(8, dist * 0.11);
          eye.targetLookY = Math.sin(ang) * Math.min(8, dist * 0.11);
          eye.targetDepth = this.state === 'curious' ? 0.95 : 0.45;
        } else if (this.state === 'thinking') {
          eye.targetX = Math.cos(t * 2.8) * 18;
          eye.targetY = Math.sin(t * 5.6) * 10 - 3;
          eye.targetLookX = Math.cos(t * 2.8 + 0.5) * 6;
          eye.targetLookY = -5 + Math.sin(t * 2.8) * 3;
          eye.targetDepth = Math.sin(t * 2.8) * 0.5;
        } else if (this.state === 'curious') {
          eye.saccadeTimer -= dt;
          if (eye.saccadeTimer <= 0) {
            eye.saccadeTimer = 0.7 + Math.random() * 1.1;
            const ang = (Math.random() - 0.5) * Math.PI * 1.4;
            const rad = 12 + Math.random() * 12;
            eye.targetX = Math.cos(ang) * rad;
            eye.targetY = Math.sin(ang) * rad * 0.8;
            eye.targetLookX = Math.cos(ang) * 7;
            eye.targetLookY = Math.sin(ang) * 6;
          }
        } else if (this.state === 'happy') {
          eye.targetX = Math.sin(t * 4.5) * 8;
          eye.targetY = -6 + Math.cos(t * 9.0) * 5;
          eye.targetLookX = Math.sin(t * 4.5) * 3;
          eye.targetLookY = -2;
        } else if (this.state === 'sleepy') {
          eye.targetX = 0;
          eye.targetY = 8;
          eye.targetLookX = 0;
          eye.targetLookY = 4;
        } else {
          eye.saccadeTimer -= dt;
          if (eye.saccadeTimer <= 0) {
            eye.saccadeTimer = 1.1 + Math.random() * 2.4;
            if (Math.random() < 0.32) {
              eye.targetX = (Math.random() - 0.5) * 6;
              eye.targetY = (Math.random() - 0.5) * 6;
              eye.targetLookX = 0;
              eye.targetLookY = 0;
              eye.targetDepth = 0;
            } else {
              const ang = Math.random() * Math.PI * 2;
              const dist = 7 + Math.random() * 14;
              eye.targetX = Math.cos(ang) * dist;
              eye.targetY = Math.sin(ang) * dist * 0.85;
              eye.targetLookX = Math.cos(ang) * (4 + Math.random() * 4);
              eye.targetLookY = Math.sin(ang) * (4 + Math.random() * 4);
              eye.targetDepth = (Math.random() - 0.35) * 0.8;
            }
          }
        }

        eye.vx += (eye.targetX - eye.x) * 0.085 - this.bodyVX * 0.14;
        eye.vy += (eye.targetY - eye.y) * 0.085 - this.bodyVY * 0.14;
        eye.vx *= 0.80;
        eye.vy *= 0.80;
        eye.x += eye.vx;
        eye.y += eye.vy;

        const maxCavity = this.baseRadius * 0.44;
        const d = Math.hypot(eye.x, eye.y);
        if (d > maxCavity) {
          eye.x = (eye.x / d) * maxCavity;
          eye.y = (eye.y / d) * maxCavity;
        }

        eye.lookX += (eye.targetLookX - eye.lookX) * 0.22;
        eye.lookY += (eye.targetLookY - eye.lookY) * 0.22;
        eye.depth += (eye.targetDepth - eye.depth) * 0.1;
        eye.pupilScale += (eye.targetPupilScale - eye.pupilScale) * 0.15;
      }

      traceJellyPath(ctx, scale = 1.0, offsetX = 0, offsetY = 0) {
        const pts = this.nodes.map(n => ({
          x: this.bodyX + offsetX + (n.x - this.bodyX) * scale,
          y: this.bodyY + offsetY + (n.y - this.bodyY) * scale
        }));
        const len = pts.length;
        ctx.beginPath();
        const startMidX = (pts[len - 1].x + pts[0].x) * 0.5;
        const startMidY = (pts[len - 1].y + pts[0].y) * 0.5;
        ctx.moveTo(startMidX, startMidY);
        for (let i = 0; i < len; i++) {
          const p1 = pts[i];
          const p2 = pts[(i + 1) % len];
          const midX = (p1.x + p2.x) * 0.5;
          const midY = (p1.y + p2.y) * 0.5;
          ctx.quadraticCurveTo(p1.x, p1.y, midX, midY);
        }
        ctx.closePath();
      }

      render(ctx = this.ctx) {
        ctx.clearRect(0, 0, this.w, this.h);

        const heightOffset = Math.max(-25, Math.min(25, this.cy - this.bodyY));
        const shadowScale = 1 - heightOffset * 0.012;
        ctx.save();
        ctx.beginPath();
        ctx.ellipse(
          this.bodyX,
          this.cy + this.baseRadius + 18,
          44 * shadowScale,
          9 * shadowScale,
          0, 0, Math.PI * 2
        );
        ctx.fillStyle = 'rgba(0, 0, 0, 0.22)';
        ctx.fill();
        ctx.restore();

        ctx.save();
        this.traceJellyPath(ctx, 1.06);
        ctx.fillStyle = this.theme.glow;
        ctx.filter = 'blur(8px)';
        ctx.fill();
        ctx.restore();

        ctx.save();
        this.traceJellyPath(ctx, 1.0);
        const grad = ctx.createRadialGradient(
          this.bodyX + this.eye.x * 0.45 - 12,
          this.bodyY + this.eye.y * 0.45 - 16,
          8,
          this.bodyX,
          this.bodyY,
          this.baseRadius * 1.15
        );
        grad.addColorStop(0, this.theme.core);
        grad.addColorStop(0.55, this.theme.mid);
        grad.addColorStop(1, this.theme.edge);
        ctx.fillStyle = grad;
        ctx.fill();

        ctx.clip();

        const eyeWorldX = this.bodyX + this.eye.x;
        const eyeWorldY = this.bodyY + this.eye.y;
        const coreHalo = ctx.createRadialGradient(
          eyeWorldX, eyeWorldY, 4,
          eyeWorldX, eyeWorldY, 40
        );
        coreHalo.addColorStop(0, 'rgba(255,255,255,0.35)');
        coreHalo.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = coreHalo;
        ctx.beginPath();
        ctx.arc(eyeWorldX, eyeWorldY, 40, 0, Math.PI * 2);
        ctx.fill();

        for (let i = 0; i < this.bubbles.length; i += 2) {
          this.drawBubble(ctx, this.bubbles[i]);
        }

        if (this.calc.phase === 'submerged') {
          this.drawInteractionPulse(ctx, eyeWorldX, eyeWorldY, this.bodyX + this.calc.x, this.bodyY + this.calc.y);
          this.drawCalculator(ctx, this.bodyX + this.calc.x, this.bodyY + this.calc.y, this.calc.angle);
        }

        if (this.reader.padPhase === 'submerged') {
          this.drawNotepad(ctx, this.bodyX + this.reader.px, this.bodyY + this.reader.py, this.reader.pAngle);
        }

        this.drawInternalEye(ctx, eyeWorldX, eyeWorldY);

        if (this.reader.monoclePhase === 'submerged') {
          this.drawMonocle(ctx, this.bodyX + this.reader.mx, this.bodyY + this.reader.my, this.reader.mAngle);
        }

        for (let i = 1; i < this.bubbles.length; i += 2) {
          this.drawBubble(ctx, this.bubbles[i]);
        }

        const depthTintAlpha = 0.18 - this.eye.depth * 0.08;
        ctx.fillStyle = this.theme.tint;
        ctx.globalAlpha = Math.max(0.06, Math.min(0.32, depthTintAlpha));
        ctx.fillRect(0, 0, this.w, this.h);
        ctx.globalAlpha = 1;

        this.traceJellyPath(ctx, 0.90, -3, -4);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
        ctx.lineWidth = 3;
        ctx.stroke();

        ctx.restore();

        ctx.save();
        this.traceJellyPath(ctx, 1.0);
        ctx.strokeStyle = this.theme.rim;
        ctx.lineWidth = 2.2;
        ctx.stroke();

        const topNode = this.nodes[19];
        ctx.beginPath();
        ctx.ellipse(topNode.x + 14, topNode.y + 13, 17, 7.5, -0.52, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.62)';
        ctx.fill();

        ctx.beginPath();
        ctx.arc(topNode.x + 31, topNode.y + 7, 3.8, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.55)';
        ctx.fill();
        ctx.restore();

        if (this.chickScene.phase !== 'none' && this.chickScene.chickX > -30 && this.chickScene.chickX < this.w + 30) {
          this.drawChick(ctx);
        }

        if (this.chickScene.armExtension > 0.02) {
          this.drawChubbyGelArm(ctx);
        }

        if (this.calc.phase === 'falling' || this.calc.phase === 'ejecting') {
          this.drawCalculator(ctx, this.bodyX + this.calc.x, this.bodyY + this.calc.y, this.calc.angle);
        }
        if (this.reader.padPhase === 'falling' || this.reader.padPhase === 'ejecting') {
          this.drawNotepad(ctx, this.bodyX + this.reader.px, this.bodyY + this.reader.py, this.reader.pAngle);
        }
        if (this.reader.monoclePhase === 'falling' || this.reader.monoclePhase === 'ejecting') {
          this.drawMonocle(ctx, this.bodyX + this.reader.mx, this.bodyY + this.reader.my, this.reader.mAngle);
        }

        for (const p of this.particles) {
          ctx.save();
          ctx.globalAlpha = Math.max(0, p.alpha);
          if (p.type === 'droplet') {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = this.theme.rim;
            ctx.fill();
          } else {
            ctx.font = `bold ${Math.round(p.size)}px monospace`;
            ctx.fillStyle = p.color || '#ffffff';
            ctx.shadowColor = p.color || this.theme.rim;
            ctx.shadowBlur = 6;
            ctx.fillText(p.text, p.x, p.y);
          }
          ctx.restore();
        }
      }

      drawChick(ctx) {
        const cs = this.chickScene;
        const x = cs.chickX;
        const y = cs.chickY;
        const isWalking = cs.phase === 'approaching' || cs.phase === 'walking_past';
        const legSwing = isWalking ? Math.sin(cs.walkCycle) * 5 : 0;

        ctx.save();
        ctx.beginPath();
        ctx.ellipse(x, this.cy + this.baseRadius + 16, 13, 3.5, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 0, 0, 0.20)';
        ctx.fill();

        ctx.translate(x, y);

        ctx.strokeStyle = '#ea580c';
        ctx.lineWidth = 2.2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        ctx.beginPath();
        ctx.moveTo(-3, -4);
        ctx.lineTo(-3 - legSwing, 5);
        ctx.lineTo(-7 - legSwing, 5);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(3, -4);
        ctx.lineTo(3 + legSwing, 5);
        ctx.lineTo(-1 + legSwing, 5);
        ctx.stroke();

        const scaleX = 1 + cs.chickSquash * 0.65;
        const scaleY = 1 - cs.chickSquash;
        ctx.translate(0, 4);
        ctx.scale(scaleX, scaleY);
        ctx.translate(0, -4);

        const bodyGrad = ctx.createRadialGradient(-4, -14, 2, 0, -10, 16);
        bodyGrad.addColorStop(0, '#fef08a');
        bodyGrad.addColorStop(0.6, '#facc15');
        bodyGrad.addColorStop(1, '#eab308');

        ctx.fillStyle = bodyGrad;
        ctx.strokeStyle = '#ca8a04';
        ctx.lineWidth = 1.5;

        ctx.beginPath();
        ctx.ellipse(1, -9, 12.5, 10.5, 0.08, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(-6, -18, 9.2, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(-2, -13, 8.2, 0, Math.PI * 2);
        ctx.fill();

        const tuftBend = cs.chickSquash * 2.5;
        ctx.beginPath();
        ctx.moveTo(-6, -27);
        ctx.quadraticCurveTo(-8 - tuftBend, -32 + tuftBend * 2, -4 - tuftBend, -31 + tuftBend * 2);
        ctx.quadraticCurveTo(-3, -29, -5, -27);
        ctx.fillStyle = '#facc15';
        ctx.fill();
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(-14.5, -19.5);
        ctx.lineTo(-19.5, -17.5);
        ctx.lineTo(-14.5, -15.5);
        ctx.closePath();
        ctx.fillStyle = '#f97316';
        ctx.fill();
        ctx.strokeStyle = '#c2410c';
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.beginPath();
        ctx.ellipse(-10.5, -15, 2.4, 1.4, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(251, 113, 133, 0.55)';
        ctx.fill();

        if (cs.happyEyes && cs.phase === 'petting') {
          ctx.beginPath();
          ctx.arc(-10, -18.5, 2.3, Math.PI * 1.1, Math.PI * 1.9);
          ctx.strokeStyle = '#1e293b';
          ctx.lineWidth = 1.7;
          ctx.stroke();
        } else {
          ctx.beginPath();
          ctx.arc(-10, -19, 2.0, 0, Math.PI * 2);
          ctx.fillStyle = '#0f172a';
          ctx.fill();

          ctx.beginPath();
          ctx.arc(-10.6, -19.6, 0.75, 0, Math.PI * 2);
          ctx.fillStyle = '#ffffff';
          ctx.fill();
        }

        const wingFlutter = cs.phase === 'petting' ? Math.sin(cs.patCycle * 2) * 0.28 : (isWalking ? Math.sin(cs.walkCycle) * 0.1 : 0);
        ctx.save();
        ctx.translate(2, -10);
        ctx.rotate(-0.15 + wingFlutter);
        ctx.beginPath();
        ctx.ellipse(2, 1, 6.2, 4.0, 0.2, 0, Math.PI * 2);
        ctx.fillStyle = '#fde047';
        ctx.strokeStyle = '#ca8a04';
        ctx.lineWidth = 1.3;
        ctx.fill();
        ctx.stroke();
        ctx.restore();

        ctx.restore();
      }

      drawChubbyGelArm(ctx) {
        const cs = this.chickScene;
        const ext = cs.armExtension;

        const sx = this.bodyX + this.baseRadius * 0.62;
        const sy = this.bodyY + 2;
        const hx = cs.handX;
        const hy = cs.handY;

        const ctrlX = (sx + hx) * 0.5 + 4;
        const ctrlY = Math.min(sy, hy) - 18 * ext;

        ctx.save();

        const armGrad = ctx.createLinearGradient(sx, sy, hx, hy);
        armGrad.addColorStop(0, this.theme.mid);
        armGrad.addColorStop(0.6, this.theme.core);
        armGrad.addColorStop(1, this.theme.mid);

        ctx.beginPath();
        ctx.moveTo(sx, sy - 11);
        ctx.quadraticCurveTo(ctrlX, ctrlY - 9, hx - 4, hy - 6);
        ctx.lineTo(hx - 4, hy + 7);
        ctx.quadraticCurveTo(ctrlX - 2, ctrlY + 9, sx, sy + 12);
        ctx.closePath();

        ctx.fillStyle = armGrad;
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(sx + 6, sy - 10);
        ctx.quadraticCurveTo(ctrlX, ctrlY - 9, hx - 4, hy - 6);
        ctx.strokeStyle = this.theme.rim;
        ctx.lineWidth = 2.1;
        ctx.lineCap = 'round';
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(sx + 6, sy + 11);
        ctx.quadraticCurveTo(ctrlX - 2, ctrlY + 9, hx - 4, hy + 7);
        ctx.strokeStyle = this.theme.rim;
        ctx.lineWidth = 2.1;
        ctx.stroke();

        ctx.save();
        ctx.translate(hx, hy);
        const patTilt = cs.phase === 'petting' ? Math.sin(cs.patCycle) * 0.18 + 0.25 : 0.2;
        ctx.rotate(patTilt);

        ctx.beginPath();
        ctx.ellipse(0, 0, 10.5, 8.2, 0.15, 0, Math.PI * 2);
        ctx.fillStyle = this.theme.core;
        ctx.fill();
        ctx.strokeStyle = this.theme.rim;
        ctx.lineWidth = 2.0;
        ctx.stroke();

        const fingerOffsets = [
          { x: 8.5, y: -3.5, r: 3.8 },
          { x: 9.8, y: 0.8,  r: 4.0 },
          { x: 7.5, y: 4.8,  r: 3.6 }
        ];
        for (const f of fingerOffsets) {
          ctx.beginPath();
          ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
          ctx.fillStyle = this.theme.core;
          ctx.fill();
          ctx.strokeStyle = this.theme.rim;
          ctx.lineWidth = 1.6;
          ctx.stroke();
        }

        ctx.beginPath();
        ctx.ellipse(-2, 6.5, 4.2, 3.0, 0.5, 0, Math.PI * 2);
        ctx.fillStyle = this.theme.core;
        ctx.fill();
        ctx.strokeStyle = this.theme.rim;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.beginPath();
        ctx.ellipse(1, 0.5, 8.8, 6.8, 0.15, 0, Math.PI * 2);
        ctx.fillStyle = this.theme.core;
        ctx.fill();

        ctx.beginPath();
        ctx.ellipse(-1, -3.2, 5.2, 2.2, -0.2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.65)';
        ctx.fill();

        ctx.restore();
        ctx.restore();
      }

      drawMonocle(ctx, x, y, angle) {
        const r = 16.5;
        const swing = this.reader.chainSwing;

        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);

        ctx.save();
        const attachX = -r + 1;
        const attachY = 3;
        const endX = attachX - 5 + Math.sin(swing) * 14;
        const endY = attachY + 34;
        const ctrlX = attachX - 10 + Math.sin(swing * 1.3) * 18;
        const ctrlY = attachY + 20;

        ctx.beginPath();
        ctx.moveTo(attachX, attachY);
        ctx.quadraticCurveTo(ctrlX, ctrlY, endX, endY);
        ctx.strokeStyle = '#fbbf24';
        ctx.lineWidth = 1.8;
        ctx.setLineDash([2.2, 2.2]);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.beginPath();
        ctx.arc(attachX - 1.5, attachY, 2.3, 0, Math.PI * 2);
        ctx.strokeStyle = '#fde047';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(endX, endY, 2.4, 0, Math.PI * 2);
        ctx.fillStyle = '#f59e0b';
        ctx.fill();
        ctx.restore();

        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(254, 243, 199, 0.16)';
        ctx.fill();

        ctx.save();
        ctx.clip();
        ctx.fillStyle = 'rgba(255, 255, 255, 0.48)';
        ctx.beginPath();
        ctx.moveTo(-r, -r + 4);
        ctx.lineTo(-r + 9, -r + 4);
        ctx.lineTo(r - 4, r - 4);
        ctx.lineTo(r - 13, r - 4);
        ctx.closePath();
        ctx.fill();
        ctx.restore();

        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.strokeStyle = '#d97706';
        ctx.lineWidth = 3.2;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.strokeStyle = '#fde047';
        ctx.lineWidth = 1.4;
        ctx.stroke();

        ctx.fillStyle = '#fbbf24';
        this.roundRect(ctx, r - 1.5, -4, 3.8, 7, 1.2);
        ctx.fill();

        ctx.restore();
      }

      drawNotepad(ctx, x, y, angle) {
        const w = 30;
        const h = 38;
        const r = 3.5;
        const rd = this.reader;

        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);

        ctx.fillStyle = 'rgba(0, 15, 10, 0.26)';
        this.roundRect(ctx, -w / 2 + 2, -h / 2 + 3, w, h, r);
        ctx.fill();

        ctx.fillStyle = '#78350f';
        this.roundRect(ctx, -w / 2, -h / 2 + 1, w, h + 1.5, r);
        ctx.fill();

        ctx.fillStyle = '#fef3c7';
        ctx.strokeStyle = '#d97706';
        ctx.lineWidth = 1;
        this.roundRect(ctx, -w / 2 + 1, -h / 2 + 2, w - 2, h - 2.5, r - 1);
        ctx.fill();
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(-w / 2 + 6, -h / 2 + 5);
        ctx.lineTo(-w / 2 + 6, h / 2 - 2);
        ctx.strokeStyle = 'rgba(244, 63, 94, 0.35)';
        ctx.lineWidth = 0.8;
        ctx.stroke();

        this.drawPageLines(ctx, w, h, rd.isFlipping ? -1 : rd.currentLine, rd.lineProgress);

        if (rd.isFlipping) {
          const p = rd.flipProgress;
          const pageH = h - 3;
          const cosP = Math.cos(p * Math.PI);

          ctx.save();
          ctx.translate(0, -h / 2 + 2);

          if (cosP > 0) {
            ctx.fillStyle = `rgba(0, 0, 0, ${(1 - cosP) * 0.22})`;
            ctx.fillRect(-w / 2 + 1.5, 2, w - 3, pageH * cosP);
          }

          ctx.scale(1, cosP);

          ctx.beginPath();
          ctx.moveTo(-w / 2 + 1, 0);
          ctx.lineTo(w / 2 - 1, 0);
          const curlX = Math.sin(p * Math.PI) * 3.5;
          ctx.lineTo(w / 2 - 1 + curlX, pageH);
          ctx.quadraticCurveTo(curlX, pageH - Math.sin(p * Math.PI) * 4, -w / 2 + 1 + curlX, pageH);
          ctx.closePath();

          ctx.fillStyle = cosP >= 0 ? '#fffbeb' : '#fde68a';
          ctx.strokeStyle = '#d97706';
          ctx.lineWidth = 0.9;
          ctx.fill();
          ctx.stroke();

          ctx.strokeStyle = 'rgba(71, 85, 105, 0.45)';
          ctx.lineWidth = 1.2;
          for (let line = 0; line < 4; line++) {
            const ly = 8 + line * 6.5;
            ctx.beginPath();
            ctx.moveTo(-w / 2 + 5, ly);
            ctx.lineTo(w / 2 - 6, ly);
            ctx.stroke();
          }

          ctx.restore();
        }

        const numRings = 5;
        const ringSpan = w - 8;
        for (let i = 0; i < numRings; i++) {
          const rx = -ringSpan / 2 + (i / (numRings - 1)) * ringSpan;
          const ry = -h / 2 + 1.5;

          ctx.beginPath();
          ctx.arc(rx, ry + 2.5, 1.3, 0, Math.PI * 2);
          ctx.fillStyle = '#78350f';
          ctx.fill();

          ctx.beginPath();
          ctx.ellipse(rx, ry, 1.4, 3.2, 0.1, 0, Math.PI * 2);
          ctx.strokeStyle = '#e2e8f0';
          ctx.lineWidth = 1.35;
          ctx.stroke();
        }

        ctx.restore();
      }

      drawPageLines(ctx, w, h, activeLine, lineProgress) {
        const lineLengths = [17, 14, 18, 12];
        for (let i = 0; i < 4; i++) {
          const ly = -h / 2 + 10 + i * 6.5;
          const startX = -w / 2 + 7.5;
          const fullLen = lineLengths[i];

          ctx.beginPath();
          ctx.moveTo(-w / 2 + 3, ly + 2);
          ctx.lineTo(w / 2 - 3, ly + 2);
          ctx.strokeStyle = 'rgba(148, 163, 184, 0.35)';
          ctx.lineWidth = 0.7;
          ctx.stroke();

          ctx.beginPath();
          ctx.moveTo(startX, ly);
          ctx.lineTo(startX + fullLen, ly);
          ctx.strokeStyle = i < activeLine ? '#0f172a' : '#64748b';
          ctx.lineWidth = 1.6;
          ctx.lineCap = 'round';
          ctx.stroke();

          if (i === activeLine) {
            const readLen = Math.max(2, fullLen * lineProgress);
            ctx.beginPath();
            ctx.moveTo(startX, ly);
            ctx.lineTo(startX + readLen, ly);
            ctx.strokeStyle = '#059669';
            ctx.lineWidth = 2.0;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(startX + readLen, ly, 1.6, 0, Math.PI * 2);
            ctx.fillStyle = '#10b981';
            ctx.fill();
          }
        }
      }

      drawInteractionPulse(ctx, ex, ey, cx, cy) {
        if (this.calc.pulseWave <= 0) return;
        const prog = 1 - this.calc.pulseWave;
        const px = ex + (cx - ex) * (0.35 + prog * 0.55);
        const py = ey + (cy - ey) * (0.35 + prog * 0.55);

        ctx.save();
        ctx.beginPath();
        ctx.arc(px, py, 4 + prog * 8, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255, 255, 255, ${this.calc.pulseWave * 0.75})`;
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.restore();
      }

      drawCalculator(ctx, x, y, angle) {
        const w = 30;
        const h = 38;
        const r = 5;

        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);

        ctx.fillStyle = 'rgba(0, 15, 10, 0.28)';
        this.roundRect(ctx, -w / 2 + 2, -h / 2 + 3, w, h, r);
        ctx.fill();

        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#94a3b8';
        ctx.lineWidth = 1.5;
        this.roundRect(ctx, -w / 2, -h / 2, w, h, r);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#a7f3d0';
        this.roundRect(ctx, -w / 2 + 4, -h / 2 + 4, w - 8, 10, 2);
        ctx.fill();

        ctx.fillStyle = '#064e3b';
        ctx.font = 'bold 7.5px monospace';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.fillText(this.calc.screenText, w / 2 - 5.5, -h / 2 + 9.5);

        const startX = -w / 2 + 4.5;
        const startY = -h / 2 + 17;
        const bw = 6;
        const bh = 4.8;
        const gapX = 1.5;
        const gapY = 1.8;

        for (let row = 0; row < 3; row++) {
          for (let col = 0; col < 3; col++) {
            const idx = row * 3 + col;
            const bx = startX + col * (bw + gapX);
            const by = startY + row * (bh + gapY);
            const isPressed = this.calc.activeBtn === idx && this.calc.pulseWave > 0.25;

            if (isPressed) {
              ctx.fillStyle = '#fde047';
            } else if (idx === 8) {
              ctx.fillStyle = '#f59e0b';
            } else if (col === 2) {
              ctx.fillStyle = '#64748b';
            } else {
              ctx.fillStyle = '#cbd5e1';
            }

            this.roundRect(ctx, bx, by + (isPressed ? 0.8 : 0), bw, bh, 1.2);
            ctx.fill();
          }
        }

        ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
        ctx.beginPath();
        ctx.moveTo(-w / 2 + 5, -h / 2 + 4.5);
        ctx.lineTo(-w / 2 + 14, -h / 2 + 4.5);
        ctx.lineTo(-w / 2 + 10, -h / 2 + 13.5);
        ctx.lineTo(-w / 2 + 5, -h / 2 + 13.5);
        ctx.closePath();
        ctx.fill();

        ctx.restore();
      }

      roundRect(ctx, x, y, w, h, r) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.arcTo(x + w, y, x + w, y + h, r);
        ctx.arcTo(x + w, y + h, x, y + h, r);
        ctx.arcTo(x, y + h, x, y, r);
        ctx.arcTo(x, y, x + w, y, r);
        ctx.closePath();
      }

      drawBubble(ctx, b) {
        const bx = this.bodyX + b.x;
        const by = this.bodyY + b.y;
        ctx.save();
        ctx.beginPath();
        ctx.arc(bx, by, b.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${b.alpha})`;
        ctx.fill();
        ctx.beginPath();
        ctx.arc(bx - b.r * 0.3, by - b.r * 0.3, b.r * 0.3, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${Math.min(0.9, b.alpha + 0.3)})`;
        ctx.fill();
        ctx.restore();
      }

      drawInternalEye(ctx, ex, ey) {
        const eye = this.eye;
        const r = eye.radius * (1 + eye.depth * 0.12);

        ctx.save();
        ctx.translate(ex, ey);

        ctx.beginPath();
        ctx.arc(0, 3, r * 1.08, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 20, 15, 0.22)';
        ctx.fill();

        const openRatio = Math.max(0.06, 1 - eye.blink);
        ctx.scale(1 + (1 - openRatio) * 0.12, openRatio);

        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        const scleraGrad = ctx.createRadialGradient(-r * 0.25, -r * 0.25, r * 0.1, 0, 0, r);
        scleraGrad.addColorStop(0, '#ffffff');
        scleraGrad.addColorStop(0.72, '#ecfdf5');
        scleraGrad.addColorStop(1, '#a7f3d0');
        ctx.fillStyle = scleraGrad;
        ctx.fill();
        ctx.clip();

        const ix = eye.lookX;
        const iy = eye.lookY;
        const lookDist = Math.hypot(ix, iy);
        const lookAngle = Math.atan2(iy, ix);
        const foreshorten = Math.max(0.72, 1 - (lookDist / r) * 0.32);

        ctx.save();
        ctx.translate(ix, iy);
        ctx.rotate(lookAngle);
        ctx.scale(foreshorten, 1);
        ctx.rotate(-lookAngle);

        const irisR = r * 0.56;
        const irisGrad = ctx.createRadialGradient(0, 0, irisR * 0.2, 0, 0, irisR);
        irisGrad.addColorStop(0, this.theme.irisInner);
        irisGrad.addColorStop(0.7, this.theme.irisOuter);
        irisGrad.addColorStop(1, '#022c22');
        ctx.beginPath();
        ctx.arc(0, 0, irisR, 0, Math.PI * 2);
        ctx.fillStyle = irisGrad;
        ctx.fill();

        const pupilR = irisR * 0.54 * eye.pupilScale;
        ctx.beginPath();
        ctx.arc(0, 0, pupilR, 0, Math.PI * 2);
        ctx.fillStyle = '#050b14';
        ctx.fill();

        if (this.state === 'happy' || (this.state === 'petting_chick' && this.chickScene.phase === 'petting')) {
          ctx.beginPath();
          ctx.arc(0, 2, pupilR * 0.65, Math.PI * 1.15, Math.PI * 1.85);
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 2.5;
          ctx.lineCap = 'round';
          ctx.stroke();
        }

        ctx.beginPath();
        ctx.arc(-irisR * 0.35, -irisR * 0.35, irisR * 0.24, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.92)';
        ctx.fill();

        ctx.beginPath();
        ctx.arc(irisR * 0.28, irisR * 0.28, irisR * 0.11, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
        ctx.fill();

        ctx.restore();
        ctx.restore();
      }
    }

    const canvas = document.getElementById('mascotCanvas');
    const mascot = new JellyAlienMascot(canvas);
    window.gloopMascot = mascot;

    let downX = 0;
    let downY = 0;
    let isPointerDown = false;

    canvas.addEventListener('pointermove', (e) => {
      const rect = canvas.getBoundingClientRect();
      mascot.pointer.x = (e.clientX - rect.left) * (canvas.width / rect.width);
      mascot.pointer.y = (e.clientY - rect.top) * (canvas.height / rect.height);
      mascot.pointer.active = true;

      if (isPointerDown && Math.hypot(e.clientX - downX, e.clientY - downY) > 6) {
        isPointerDown = false;
        document.title = 'GLOOP_DRAG:' + Date.now();
      }
    });

    canvas.addEventListener('pointerleave', () => {
      mascot.pointer.active = false;
      isPointerDown = false;
    });

    canvas.addEventListener('pointerdown', (e) => {
      if (e.button === 0) {
        downX = e.clientX;
        downY = e.clientY;
        isPointerDown = true;
        const rect = canvas.getBoundingClientRect();
        const px = (e.clientX - rect.left) * (canvas.width / rect.width);
        const py = (e.clientY - rect.top) * (canvas.height / rect.height);
        mascot.poke(px, py, 16);
      }
    });

    window.addEventListener('pointerup', () => {
      isPointerDown = false;
    });

    document.getElementById('themeBtn').addEventListener('click', () => mascot.nextTheme());
    document.getElementById('randomNowBtn').addEventListener('click', () => mascot.triggerRandomAnimation());
    document.querySelectorAll('[data-trig]').forEach((btn) => {
      btn.addEventListener('click', () => mascot.setState(btn.getAttribute('data-trig')));
    });

    let lastTime = performance.now();
    function animate(now) {
      const dt = Math.min(0.05, (now - lastTime) / 1000);
      lastTime = now;
      mascot.update(dt);
      mascot.render();
      requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
  </script>
</body>
</html>
"""


def run_gtk_webkit():
    import gi
    gi.require_version('Gtk', '3.0')
    try:
        gi.require_version('WebKit2', '4.1')
    except ValueError:
        gi.require_version('WebKit2', '4.0')
    from gi.repository import Gtk, Gdk, WebKit2

    class GloopLinuxWidget(Gtk.Window):
        def __init__(self):
            super().__init__(type=Gtk.WindowType.TOPLEVEL)
            self.set_title("Gloop Mascot Widget")
            self.set_default_size(250, 250)
            self.set_resizable(False)
            self.set_decorated(False)
            self.set_keep_above(True)
            self.set_skip_taskbar_hint(True)
            self.set_skip_pager_hint(True)

            # Enable RGBA transparency on X11 / Wayland
            screen = self.get_screen()
            visual = screen.get_rgba_visual()
            if visual and screen.is_composited():
                self.set_visual(visual)
            self.set_app_paintable(True)

            self.webview = WebKit2.WebView()
            self.webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))
            settings = self.webview.get_settings()
            settings.set_enable_developer_extras(False)

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
            if title.startswith("GLOOP_DRAG:"):
                display = Gdk.Display.get_default()
                seat = display.get_default_seat()
                pointer = seat.get_pointer()
                _, x, y = pointer.get_position()
                self.begin_move_drag(1, int(x), int(y), Gtk.get_current_event_time())

        def on_button_press(self, _widget, event):
            if event.button == 3:  # Right-click context menu
                self.show_context_menu(event)
                return True
            return False

        def show_context_menu(self, event):
            menu = Gtk.Menu()

            item_rand = Gtk.MenuItem(label="🎲 Sortear Animação Agora")
            item_rand.connect("activate", lambda _: self.js("window.gloopMascot.triggerRandomAnimation()"))
            menu.append(item_rand)

            # Animations Submenu
            sub_anim = Gtk.Menu()
            item_anim = Gtk.MenuItem(label="🎬 Executar Animação")
            item_anim.set_submenu(sub_anim)
            anims = [
                ("🐥 Carinho no Pintinho", "petting_chick"),
                ("🧐 Lendo Caderneta", "reading"),
                ("🧮 Calculando", "calculating"),
                ("✨ Feliz / Pulo", "happy"),
                ("🔍 Curioso", "curious"),
                ("🌀 Pensando", "thinking"),
                ("⚡ Surpreso", "surprised"),
                ("💤 Dormindo", "sleepy"),
                ("🟢 Voltar ao Idle Vivo", "idle"),
            ]
            for label, st in anims:
                mi = Gtk.MenuItem(label=label)
                mi.connect("activate", lambda _, s=st: self.js(f"window.gloopMascot.setState('{s}')"))
                sub_anim.append(mi)
            menu.append(item_anim)

            # Themes Submenu
            sub_theme = Gtk.Menu()
            item_theme = Gtk.MenuItem(label="🎨 Bioluminescência (Cor)")
            item_theme.set_submenu(sub_theme)
            for label, th in [
                ("🟢 Verde Bio", "emerald"),
                ("🔵 Ciano Abissal", "cyan"),
                ("🟣 Roxo Nebulosa", "nebula"),
                ("🟡 Âmbar Solar", "amber"),
                ("🔴 Rosa Coral", "coral"),
            ]:
                mi = Gtk.MenuItem(label=label)
                mi.connect("activate", lambda _, t=th: self.js(f"window.gloopMascot.setTheme('{t}')"))
                sub_theme.append(mi)
            menu.append(item_theme)

            # Frequency Submenu
            sub_freq = Gtk.Menu()
            item_freq = Gtk.MenuItem(label="⏱ Frequência Aleatória")
            item_freq.set_submenu(sub_freq)
            for label, mn, mx in [
                ("⚡ Rápida (8s a 16s)", 8, 16),
                ("🌿 Normal (16s a 36s)", 16, 36),
                ("🧘 Calma (45s a 90s)", 45, 90),
            ]:
                mi = Gtk.MenuItem(label=label)
                mi.connect("activate", lambda _, a=mn, b=mx: self.js(f"window.gloopMascot.setRandomIntervalRange({a}, {b})"))
                sub_freq.append(mi)
            menu.append(item_freq)

            menu.append(Gtk.SeparatorMenuItem())

            item_quit = Gtk.MenuItem(label="❌ Fechar Mascote")
            item_quit.connect("activate", Gtk.main_quit)
            menu.append(item_quit)

            menu.show_all()
            menu.popup_at_pointer(event)

    GloopLinuxWidget()
    Gtk.main()


def run_pyqt():
    try:
        from PyQt6.QtCore import Qt, QPoint
        from PyQt6.QtGui import QColor, QAction
        from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        IS_QT6 = True
    except ImportError:
        from PyQt5.QtCore import Qt, QPoint
        from PyQt5.QtGui import QColor
        from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        IS_QT6 = False

    app = QApplication(sys.argv)

    class QtGloopWidget(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setFixedSize(250, 250)
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
            if title.startswith("GLOOP_DRAG:") and hasattr(self, "windowHandle") and self.windowHandle():
                self.windowHandle().startSystemMove()

        def show_context_menu(self, pos):
            menu = QMenu(self)
            act_rand = QAction("🎲 Sortear Animação Agora", self)
            act_rand.triggered.connect(lambda: self.js("window.gloopMascot.triggerRandomAnimation()"))
            menu.addAction(act_rand)

            sub_anim = menu.addMenu("🎬 Executar Animação")
            for label, st in [
                ("🐥 Carinho no Pintinho", "petting_chick"),
                ("🧐 Lendo Caderneta", "reading"),
                ("🧮 Calculando", "calculating"),
                ("✨ Feliz / Pulo", "happy"),
                ("🔍 Curioso", "curious"),
                ("🌀 Pensando", "thinking"),
                ("⚡ Surpreso", "surprised"),
                ("💤 Dormindo", "sleepy"),
                ("🟢 Voltar ao Idle Vivo", "idle"),
            ]:
                a = QAction(label, self)
                a.triggered.connect(lambda _checked=False, s=st: self.js(f"window.gloopMascot.setState('{s}')"))
                sub_anim.addAction(a)

            sub_theme = menu.addMenu("🎨 Bioluminescência (Cor)")
            for label, th in [
                ("🟢 Verde Bio", "emerald"),
                ("🔵 Ciano Abissal", "cyan"),
                ("🟣 Roxo Nebulosa", "nebula"),
                ("🟡 Âmbar Solar", "amber"),
                ("🔴 Rosa Coral", "coral"),
            ]:
                a = QAction(label, self)
                a.triggered.connect(lambda _checked=False, t=th: self.js(f"window.gloopMascot.setTheme('{t}')"))
                sub_theme.addAction(a)

            menu.addSeparator()
            act_quit = QAction("❌ Fechar Mascote", self)
            act_quit.triggered.connect(app.quit)
            menu.addAction(act_quit)

            global_pos = self.view.mapToGlobal(pos)
            menu.exec(global_pos) if IS_QT6 else menu.exec_(global_pos)

    win = QtGloopWidget()
    win.show()
    sys.exit(app.exec() if IS_QT6 else app.exec_())


if __name__ == "__main__":
    try:
        run_gtk_webkit()
    except Exception:
        try:
            run_pyqt()
        except Exception as err:
            print("Para rodar o widget nativo no Linux, instale GTK3+WebKit2 ou PyQt6-WebEngine:")
            print("  Ubuntu/Debian/Mint: sudo apt install python3-gi gir1.2-webkit2-4.1")
            print("  Fedora:             sudo dnf install python3-gobject webkit2gtk4.1")
            print("  Arch Linux:         sudo pacman -S python-gobject webkit2gtk-4.1")
            print(f"Detalhe do erro: {err}")
            sys.exit(1)
