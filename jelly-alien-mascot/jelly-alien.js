/**
 * JellyAlienMascot ("Gloop") - Drop-in Living Mascot Engine & Web Component
 * Zero dependencies. Uses 2D Canvas with soft-body spring-ring physics,
 * an internal floating eye suspended in viscous bioluminescent gel, and
 * interactive animations:
 *   - 'petting_chick': A cute yellow chick walks up to Gloop; Gloop stretches his jelly body
 *                      into a chubby arm + hand, pets the chick, retracts his arm, and the chick walks past & disappears!
 *   - 'reading': Falling golden monocle with chain (worn by the eye!) + vertical-flip spiral notepad
 *   - 'calculating': Falling calculator + eye pressing keys & reading LCD
 *
 * Usage 1 (Web Component in HTML / Vue / Angular / Electron):
 *   <script type="module" src="jelly-alien.js"></script>
 *   <jelly-alien state="petting_chick" theme="emerald" size="240" follow-cursor></jelly-alien>
 *
 * Usage 2 (JavaScript API):
 *   const mascot = new JellyAlienMascot(canvasElement, { theme: 'emerald', state: 'petting_chick' });
 *   mascot.setState('petting_chick');
 *   mascot.poke();
 */

const JELLY_THEMES = {
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

const LCD_EXPRESSIONS = ['42', '3.14', '1+1=2', '99%', '∑x', '7×8', '808', '√2', '=100'];
const MATH_SYMBOLS = ['+', '−', '×', '÷', '=', '%', 'π', '∑'];
const NOTE_SYMBOLS = ['!', '?', '§', '✓', '⋯', '💡'];
const CHICK_SYMBOLS = ['♥', '♪', '♥', '✨'];

class JellyAlienMascot {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.w = canvas.width || 245;
    this.h = canvas.height || 235;
    this.scaleRatio = Math.min(this.w, this.h) / 235;

    this.cx = this.w / 2 - 6 * this.scaleRatio;
    this.cy = this.h / 2 + 10 * this.scaleRatio;
    this.baseRadius = 62 * this.scaleRatio;

    this.theme = JELLY_THEMES[options.theme] || JELLY_THEMES.emerald;
    this.state = 'idle';
    this.squishFactor = options.squishFactor ?? 1.0;
    this.followCursor = options.followCursor ?? true;
    this.interactive = options.interactive ?? true;
    this.time = 0;
    this._rafId = null;

    // Body center coordinates & velocity
    this.bodyX = this.cx;
    this.bodyY = this.cy;
    this.bodyVX = 0;
    this.bodyVY = 0;

    // Soft-body perimeter nodes (spring-mass ring)
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

    // Internal floating eye (suspended inside the gel cavity)
    this.eye = {
      x: 0,
      y: -2 * this.scaleRatio,
      vx: 0,
      vy: 0,
      targetX: 0,
      targetY: -2 * this.scaleRatio,
      lookX: 0,
      lookY: 0,
      targetLookX: 0,
      targetLookY: 0,
      radius: 21 * this.scaleRatio,
      depth: 0,
      targetDepth: 0,
      pupilScale: 1.0,
      targetPupilScale: 1.0,
      blink: 0,
      isBlinking: false,
      blinkTimer: 2.0,
      saccadeTimer: 1.2
    };

    // Calculator object (for 'calculating' state)
    this.calc = {
      phase: 'none',
      x: 16 * this.scaleRatio,
      y: -140 * this.scaleRatio,
      vx: 0,
      vy: 0,
      angle: -0.25,
      vAngle: 0,
      activeBtn: -1,
      btnTimer: 0.4,
      screenText: '0.',
      pulseWave: 0,
      glanceUpTimer: 0
    };

    // Monocle + Vertical Flip Notepad objects (for 'reading' state)
    this.reader = {
      monoclePhase: 'none',
      mx: -14 * this.scaleRatio,
      my: -150 * this.scaleRatio,
      mvx: 0,
      mvy: 0,
      mAngle: 0.2,
      chainSwing: 0,
      chainVSwing: 0,

      padPhase: 'none',
      px: 18 * this.scaleRatio,
      py: -185 * this.scaleRatio,
      pvx: 0,
      pvy: 0,
      pAngle: -0.15,
      pvAngle: 0,

      currentLine: 0,
      lineProgress: 0,
      isFlipping: false,
      flipProgress: 0,
      pageNumber: 1
    };

    // Little Chick + Chubby Gel Arm (for 'petting_chick' state)
    this.chickScene = {
      phase: 'none', // 'none' | 'approaching' | 'extending' | 'petting' | 'retracting' | 'walking_past'
      timer: 0,
      chickX: 270 * this.scaleRatio,
      chickY: 0,
      walkCycle: 0,
      chickSquash: 0,
      happyEyes: false,
      armExtension: 0,
      handX: 0,
      handY: 0,
      patCycle: 0,
      heartTimer: 0
    };

    // Internal suspended micro-bubbles
    this.bubbles = Array.from({ length: 9 }, (_, i) => ({
      x: (Math.random() - 0.5) * 75 * this.scaleRatio,
      y: (Math.random() - 0.5) * 75 * this.scaleRatio,
      r: (2 + (i % 4) * 1.4) * this.scaleRatio,
      alpha: 0.25 + (i % 3) * 0.18,
      phase: Math.random() * Math.PI * 2
    }));

    this.particles = [];
    this.pointer = { x: this.cx, y: this.cy, active: false };

    if (options.state) {
      this.setState(options.state);
    }

    if (this.interactive) {
      this._bindEvents();
    }
    if (options.autoStart !== false) {
      this.start();
    }
  }

  _bindEvents() {
    this._onPointerMove = (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.pointer.x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
      this.pointer.y = (e.clientY - rect.top) * (this.canvas.height / rect.height);
      this.pointer.active = true;
    };
    this._onPointerLeave = () => {
      this.pointer.active = false;
    };
    this._onPointerDown = (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const px = (e.clientX - rect.left) * (this.canvas.width / rect.width);
      const py = (e.clientY - rect.top) * (this.canvas.height / rect.height);
      this.poke(px, py, 16);
    };

    window.addEventListener('pointermove', this._onPointerMove);
    this.canvas.addEventListener('pointerleave', this._onPointerLeave);
    this.canvas.addEventListener('pointerdown', this._onPointerDown);
  }

  destroy() {
    this.stop();
    if (this.interactive) {
      window.removeEventListener('pointermove', this._onPointerMove);
      this.canvas.removeEventListener('pointerleave', this._onPointerLeave);
      this.canvas.removeEventListener('pointerdown', this._onPointerDown);
    }
  }

  setState(newState) {
    const prevState = this.state;
    this.state = newState;
    const s = this.scaleRatio;

    if (prevState === 'calculating' && newState !== 'calculating' &&
        (this.calc.phase === 'submerged' || this.calc.phase === 'falling')) {
      this.calc.phase = 'ejecting';
      this.calc.vy = -9.5 * s;
      this.calc.vx = 2.2 * s;
      this.calc.vAngle = 0.14;
      this.poke(this.bodyX, this.bodyY - this.baseRadius, -10);
    }

    if (prevState === 'reading' && newState !== 'reading' &&
        (this.reader.monoclePhase === 'submerged' || this.reader.padPhase === 'submerged' ||
         this.reader.monoclePhase === 'falling' || this.reader.padPhase === 'falling')) {
      this.reader.monoclePhase = 'ejecting';
      this.reader.mvy = -9.0 * s;
      this.reader.mvx = -2.4 * s;
      this.reader.padPhase = 'ejecting';
      this.reader.pvy = -9.5 * s;
      this.reader.pvx = 2.5 * s;
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
      cs.chickX = this.w + 22 * s;
      cs.chickY = this.cy + this.baseRadius + 10 * s;
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
      r.mx = -14 * s;
      r.my = -this.bodyY - 25 * s;
      r.mvx = 0.3 * s;
      r.mvy = 2.4 * s;
      r.mAngle = -0.3;
      r.chainSwing = 0.4;
      r.chainVSwing = 0;

      r.padPhase = 'falling';
      r.px = 18 * s;
      r.py = -this.bodyY - 68 * s;
      r.pvx = -0.3 * s;
      r.pvy = 2.0 * s;
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
      this.calc.x = (14 + (Math.random() - 0.5) * 8) * s;
      this.calc.y = -this.bodyY - 35 * s;
      this.calc.vx = (Math.random() - 0.5) * 1.2 * s;
      this.calc.vy = 2.2 * s;
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
      this.poke(this.bodyX, this.bodyY + 40 * s, -18);
      this.eye.targetPupilScale = 0.55;
      this.eye.targetDepth = 0.85;
      this.eye.targetX = 0;
      this.eye.targetY = -4 * s;
    } else if (newState === 'happy') {
      this.bodyVY = -7.5 * s;
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

  setTheme(themeNameOrObject) {
    if (typeof themeNameOrObject === 'string' && JELLY_THEMES[themeNameOrObject]) {
      this.theme = JELLY_THEMES[themeNameOrObject];
    } else if (typeof themeNameOrObject === 'object') {
      this.theme = { ...this.theme, ...themeNameOrObject };
    }
  }

  lookAt(x, y) {
    this.pointer.x = x;
    this.pointer.y = y;
    this.pointer.active = true;
  }

  poke(px, py, strength = 15) {
    const s = this.scaleRatio;
    if (px === undefined || py === undefined) {
      const ang = Math.random() * Math.PI * 2;
      px = this.bodyX + Math.cos(ang) * 45 * s;
      py = this.bodyY + Math.sin(ang) * 45 * s;
    }
    const dx = this.bodyX - px;
    const dy = this.bodyY - py;
    const dist = Math.hypot(dx, dy) || 1;
    this.bodyVX += (dx / dist) * 3.8 * this.squishFactor * s;
    this.bodyVY += (dy / dist) * 3.8 * this.squishFactor * s - 2.5 * s;

    const clickAngle = Math.atan2(py - this.bodyY, px - this.bodyX);
    for (const node of this.nodes) {
      const diff = Math.atan2(Math.sin(node.angle - clickAngle), Math.cos(node.angle - clickAngle));
      const influence = Math.exp(-(diff * diff) / 0.55);
      node.vr -= influence * strength * this.squishFactor * s;
    }

    this.eye.vx += (dx / dist) * 6.5 * s;
    this.eye.vy += (dy / dist) * 6.5 * s;
    this.eye.blink = 0.65;

    if (this.calc.phase === 'submerged') {
      this.calc.vx -= (dx / dist) * 5.0 * s;
      this.calc.vy -= (dy / dist) * 5.0 * s;
      this.calc.vAngle += (Math.random() - 0.5) * 0.25;
    }
    if (this.reader.padPhase === 'submerged') {
      this.reader.pvx -= (dx / dist) * 4.8 * s;
      this.reader.pvy -= (dy / dist) * 4.8 * s;
      this.reader.pvAngle += (Math.random() - 0.5) * 0.22;
      this.reader.chainVSwing += (dx / dist) * 0.18;
    }
  }

  _spawnSplash(offsetX) {
    const s = this.scaleRatio;
    for (let i = 0; i < 6; i++) {
      const ang = -Math.PI * 0.5 + (Math.random() - 0.5) * 1.3;
      const spd = (2 + Math.random() * 3.2) * s;
      this.particles.push({
        type: 'droplet',
        x: this.bodyX + offsetX + (Math.random() - 0.5) * 12 * s,
        y: this.bodyY - this.baseRadius + 6 * s,
        vx: Math.cos(ang) * spd,
        vy: Math.sin(ang) * spd - 1.4 * s,
        gravity: 0.18 * s,
        r: (2.2 + Math.random() * 2.2) * s,
        alpha: 0.85,
        decay: 0.026
      });
    }
  }

  update(dt) {
    this.time += dt;
    const t = this.time;
    const s = this.scaleRatio;

    let floatTargetX = this.cx;
    let floatTargetY = this.cy + Math.sin(t * 2.4) * 5 * s;

    if (this.state === 'happy') {
      const bounceWave = Math.abs(Math.sin(t * 5.2));
      floatTargetY = this.cy + 8 * s - bounceWave * 22 * s;
    } else if (this.state === 'petting_chick' &&
               (this.chickScene.phase === 'extending' || this.chickScene.phase === 'petting')) {
      floatTargetX = this.cx + 5 * s;
      floatTargetY = this.cy + 4 * s + Math.sin(t * 3.0) * 2.5 * s;
    } else if (this.state === 'thinking' || this.state === 'calculating' || this.state === 'reading') {
      floatTargetX = this.cx + Math.cos(t * 1.8) * 3.0 * s;
      floatTargetY = this.cy + Math.sin(t * 2.8) * 3.5 * s;
    } else if (this.state === 'sleepy') {
      floatTargetY = this.cy + 16 * s;
    }

    const ax = (floatTargetX - this.bodyX) * 0.12;
    const ay = (floatTargetY - this.bodyY) * 0.12;
    this.bodyVX = (this.bodyVX + ax) * 0.84;
    this.bodyVY = (this.bodyVY + ay) * 0.84;
    this.bodyX += this.bodyVX;
    this.bodyY += this.bodyVY;

    this._updateCalculator(dt, t);
    this._updateReader(dt, t);
    this._updateChickScene(dt, t);
    this._updateEye(dt, t);

    const maxEyeDist = 26 * s;
    const eyeAngle = Math.atan2(this.eye.y, this.eye.x);
    const eyeDistRatio = Math.min(1, Math.hypot(this.eye.x, this.eye.y) / maxEyeDist);

    let propAngle = 0;
    let propDistRatio = 0;
    if (this.calc.phase === 'submerged') {
      propAngle = Math.atan2(this.calc.y, this.calc.x);
      propDistRatio = Math.min(1, Math.hypot(this.calc.x, this.calc.y) / (28 * s));
    } else if (this.reader.padPhase === 'submerged') {
      propAngle = Math.atan2(this.reader.py, this.reader.px);
      propDistRatio = Math.min(1, Math.hypot(this.reader.px, this.reader.py) / (28 * s));
    }

    const armExt = this.chickScene.armExtension;

    for (let i = 0; i < this.numNodes; i++) {
      const node = this.nodes[i];
      const a = node.angle;

      let targetR = this.baseRadius
        + Math.sin(t * 2.6 + a * 2) * (2.6 * this.squishFactor * s)
        + Math.cos(t * 4.1 - a * 3) * (1.8 * this.squishFactor * s);

      const stretchY = Math.sin(a);
      targetR += (this.bodyVY * 0.9 * this.squishFactor) * (stretchY * stretchY - 0.5);

      if (this.state === 'sleepy') {
        targetR += Math.sin(a) > 0.2 ? Math.sin(a) * 10 * s : -4 * s;
      } else if (this.state === 'surprised') {
        targetR += Math.sin(t * 18 + a * 6) * 2.8 * s;
      }

      const angleDiff = Math.atan2(Math.sin(a - eyeAngle), Math.cos(a - eyeAngle));
      targetR += Math.exp(-(angleDiff * angleDiff) / 0.65) * eyeDistRatio * 9.5 * this.squishFactor * s;

      if (propDistRatio > 0) {
        const pDiff = Math.atan2(Math.sin(a - propAngle), Math.cos(a - propAngle));
        targetR += Math.exp(-(pDiff * pDiff) / 0.55) * propDistRatio * 8.5 * this.squishFactor * s;
      }

      if (armExt > 0.01) {
        const armBaseAngle = 0.08;
        const armDiff = Math.atan2(Math.sin(a - armBaseAngle), Math.cos(a - armBaseAngle));
        targetR += Math.exp(-(armDiff * armDiff) / 0.35) * armExt * 14 * this.squishFactor * s;
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
      b.y -= 0.18 * s;
      b.x += Math.sin(t * 1.8 + b.phase) * 0.15 * s - this.bodyVX * 0.18 + this.eye.vx * 0.08;
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
        x: this.bodyX + (18 + (Math.random() - 0.5) * 10) * s,
        y: this.bodyY - 35 * s,
        vy: -0.6 * s,
        vx: 0.25 * s,
        alpha: 0.9,
        size: (10 + Math.random() * 4) * s
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

  _updateChickScene(dt, _t) {
    const cs = this.chickScene;
    const s = this.scaleRatio;
    if (cs.phase === 'none') return;

    const groundY = this.cy + this.baseRadius + 10 * s;
    const stopX = this.cx + this.baseRadius + 25 * s;

    if (cs.phase === 'approaching') {
      cs.walkCycle += dt * 15;
      cs.chickX -= 52 * s * dt;
      cs.chickY = groundY - Math.abs(Math.sin(cs.walkCycle)) * 4.5 * s;
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
          x: cs.chickX + (Math.random() - 0.5) * 14 * s,
          y: cs.chickY - 30 * s,
          vx: (Math.random() - 0.5) * 0.45 * s,
          vy: -0.95 * s,
          alpha: 0.98,
          size: (12 + Math.random() * 2) * s,
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
        this.nodes[0].vr -= 6 * this.squishFactor * s;
        this.nodes[1].vr -= 4 * this.squishFactor * s;
        this.nodes[23].vr -= 4 * this.squishFactor * s;
      }
    } else if (cs.phase === 'walking_past') {
      cs.walkCycle += dt * 16;
      cs.chickX -= 62 * s * dt;
      cs.chickY = groundY - Math.abs(Math.sin(cs.walkCycle)) * 5.0 * s;
      cs.chickSquash = 0;
      cs.armExtension += (0 - cs.armExtension) * 0.25;

      if (cs.chickX < -32 * s) {
        if (this.state === 'petting_chick') {
          cs.timer += dt;
          if (cs.timer > 0.7) {
            this.setState('petting_chick');
          }
        } else {
          cs.phase = 'none';
        }
      }
    }

    const shoulderX = this.bodyX + this.baseRadius * 0.72;
    const shoulderY = this.bodyY + 4 * s;
    const patOffsetX = cs.phase === 'petting' ? Math.cos(cs.patCycle) * 3.5 * s : 0;
    const patOffsetY = cs.phase === 'petting' ? Math.sin(cs.patCycle) * 5.5 * s : 0;

    const targetHandX = cs.chickX - 2 * s + patOffsetX;
    const targetHandY = cs.chickY - 26 * s + patOffsetY;

    const ease = cs.armExtension * cs.armExtension * (3 - 2 * cs.armExtension);
    cs.handX = shoulderX + (targetHandX - shoulderX) * ease;
    cs.handY = shoulderY + (targetHandY - shoulderY) * ease;
  }

  _updateReader(dt, t) {
    const r = this.reader;
    const s = this.scaleRatio;

    if (r.monoclePhase === 'falling') {
      r.mvy += 0.46 * s;
      r.mx += r.mvx;
      r.my += r.mvy;
      r.mAngle *= 0.96;

      if (r.my >= -this.baseRadius * 0.62) {
        r.monoclePhase = 'submerged';
        this.poke(this.bodyX + r.mx, this.bodyY - this.baseRadius, 18);
        this.bodyVY += 3.2 * s;
        r.mvy *= 0.25;
        this._spawnSplash(r.mx);
      }
    } else if (r.monoclePhase === 'submerged') {
      const targetMX = this.eye.x + this.eye.lookX * 0.35;
      const targetMY = this.eye.y + this.eye.lookY * 0.25;
      r.mvx = (r.mvx + (targetMX - r.mx) * 0.24) * 0.75;
      r.mvy = (r.mvy + (targetMY - r.my) * 0.24) * 0.75;
      r.mx += r.mvx;
      r.my += r.mvy;
      r.mAngle += (0 - r.mAngle) * 0.15;

      const chainTargetAngle = -(r.mvx / s) * 0.08 + Math.sin(t * 2.6) * 0.08;
      r.chainVSwing = (r.chainVSwing + (chainTargetAngle - r.chainSwing) * 0.12) * 0.85;
      r.chainSwing += r.chainVSwing;
    } else if (r.monoclePhase === 'ejecting') {
      r.mvy += 0.42 * s;
      r.mx += r.mvx;
      r.my += r.mvy;
      r.mAngle -= 0.08;
      if (r.my > 160 * s) r.monoclePhase = 'none';
    }

    if (r.padPhase === 'falling') {
      r.pvy += 0.46 * s;
      r.px += r.pvx;
      r.py += r.pvy;
      r.pAngle += r.pvAngle;

      if (r.py >= -this.baseRadius * 0.62) {
        r.padPhase = 'submerged';
        this.poke(this.bodyX + r.px, this.bodyY - this.baseRadius, 20);
        this.bodyVY += 3.8 * s;
        r.pvy *= 0.28;
        r.pvx = 1.2 * s;
        this._spawnSplash(r.px);
      }
    } else if (r.padPhase === 'submerged') {
      const targetPX = (19 + Math.cos(t * 2.0) * 2.2) * s;
      const targetPY = (5 + Math.sin(t * 2.8) * 3.5) * s;
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
          this.eye.vy += 0.8 * s;

          if (r.currentLine >= 4) {
            r.isFlipping = true;
            r.flipProgress = 0;

            r.pvy -= 2.2 * s;
            r.pvx += 1.4 * s;
            r.pvAngle -= 0.16;
            this.eye.vy -= 2.0 * s;
            this.nodes[0].vr += 2.0 * this.squishFactor * s;

            const sym = NOTE_SYMBOLS[Math.floor(Math.random() * NOTE_SYMBOLS.length)];
            this.particles.push({
              type: 'text',
              text: sym,
              x: this.bodyX + r.px + (Math.random() - 0.5) * 10 * s,
              y: this.bodyY + r.py - 18 * s,
              vx: (Math.random() - 0.5) * 0.4 * s,
              vy: -0.85 * s,
              alpha: 0.95,
              size: (11 + Math.random() * 2) * s,
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
      r.pvy += 0.42 * s;
      r.px += r.pvx;
      r.py += r.pvy;
      r.pAngle += r.pvAngle;
      if (r.py > 160 * s) r.padPhase = 'none';
    }
  }

  _updateCalculator(dt, t) {
    const c = this.calc;
    const s = this.scaleRatio;
    if (c.phase === 'none') return;

    if (c.phase === 'falling') {
      c.vy += 0.48 * s;
      c.x += c.vx;
      c.y += c.vy;
      c.angle += c.vAngle;

      if (c.y >= -this.baseRadius * 0.62) {
        c.phase = 'submerged';
        this.poke(this.bodyX + c.x, this.bodyY - this.baseRadius, 22);
        this.bodyVY += 4.5 * s;

        c.vy *= 0.28;
        c.vx = 1.5 * s;
        c.vAngle = 0.08;
        this._spawnSplash(c.x);
      }
    } else if (c.phase === 'submerged') {
      const targetX = (19 + Math.cos(t * 2.2) * 2.5) * s;
      const targetY = (2 + Math.sin(t * 3.1) * 4.5) * s;
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

        this.eye.vx += 2.6 * s;
        this.eye.vy += (Math.random() - 0.5) * 2.2 * s;

        c.vx += 1.9 * s;
        c.vy += (Math.random() - 0.5) * 1.4 * s;
        c.vAngle += (Math.random() - 0.4) * 0.14;

        this.nodes[0].vr += 2.2 * this.squishFactor * s;
        this.nodes[1].vr += 1.5 * this.squishFactor * s;

        const sym = MATH_SYMBOLS[Math.floor(Math.random() * MATH_SYMBOLS.length)];
        this.particles.push({
          type: 'text',
          text: sym,
          x: this.bodyX + c.x + (Math.random() - 0.5) * 14 * s,
          y: this.bodyY + c.y - 16 * s,
          vx: (Math.random() - 0.5) * 0.5 * s,
          vy: (-0.9 - Math.random() * 0.4) * s,
          alpha: 0.95,
          size: (11 + Math.random() * 3) * s,
          decay: 0.015
        });
      }

      if (c.pulseWave > 0) {
        c.pulseWave = Math.max(0, c.pulseWave - dt * 3.2);
      }
    } else if (c.phase === 'ejecting') {
      c.vy += 0.42 * s;
      c.x += c.vx;
      c.y += c.vy;
      c.angle += c.vAngle;
      if (c.y > 160 * s) {
        c.phase = 'none';
      }
    }
  }

  _updateEye(dt, t) {
    const eye = this.eye;
    const s = this.scaleRatio;

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
      const dy = (cs.chickY - 10 * s) - this.bodyY;
      const ang = Math.atan2(dy, dx);
      const dist = Math.hypot(dx, dy);

      eye.targetX = Math.cos(ang) * Math.min(20 * s, dist * 0.25);
      eye.targetY = Math.sin(ang) * Math.min(14 * s, dist * 0.22);
      eye.targetLookX = Math.cos(ang) * Math.min(7.5 * s, dist * 0.11);
      eye.targetLookY = Math.sin(ang) * Math.min(6.5 * s, dist * 0.11);
      eye.targetDepth = 0.75;
      eye.targetPupilScale = cs.phase === 'petting' ? 1.32 : 1.18;
    } else if (this.state === 'reading') {
      const r = this.reader;
      if (r.monoclePhase === 'falling' || r.padPhase === 'falling') {
        eye.targetX = -6 * s;
        eye.targetY = -14 * s;
        eye.targetLookX = 0;
        eye.targetLookY = -9 * s;
        eye.targetPupilScale = 0.75;
      } else if (r.padPhase === 'submerged') {
        eye.targetX = (-16 + Math.sin(t * 2.2) * 1.8) * s;
        eye.targetY = (-3 + Math.cos(t * 2.0) * 2.2) * s;
        eye.targetDepth = 0.6;

        if (r.isFlipping) {
          const flipArc = Math.sin(r.flipProgress * Math.PI);
          eye.targetLookX = 5.5 * s;
          eye.targetLookY = (2 - flipArc * 8) * s;
          eye.targetPupilScale = 0.92;
        } else {
          const scanX = (r.lineProgress - 0.5) * 4.2 * s;
          const lineY = (r.currentLine - 1.5) * 2.2 * s;
          eye.targetLookX = 5.8 * s + scanX;
          eye.targetLookY = 1.8 * s + lineY;
          eye.targetPupilScale = 0.82;
        }
      }
    } else if (this.state === 'calculating') {
      if (this.calc.phase === 'falling') {
        eye.targetX = this.calc.x * 0.35;
        eye.targetY = -16 * s;
        eye.targetLookX = (this.calc.x - eye.x) * 0.25;
        eye.targetLookY = -9 * s;
        eye.targetPupilScale = 0.72;
      } else if (this.calc.phase === 'submerged') {
        eye.targetX = (-17 + Math.sin(t * 3.0) * 2) * s;
        eye.targetY = (-2 + Math.cos(t * 2.4) * 3) * s;
        eye.targetDepth = 0.55;

        this.calc.glanceUpTimer -= dt;
        if (this.calc.glanceUpTimer <= -0.35) {
          this.calc.glanceUpTimer = 1.6 + Math.random() * 1.2;
        }

        if (this.calc.glanceUpTimer < 0) {
          eye.targetLookX = 2 * s;
          eye.targetLookY = -7 * s;
          eye.targetPupilScale = 0.95;
        } else {
          const dx = this.calc.x - eye.x;
          const dy = this.calc.y - eye.y;
          const scanOffset = Math.sin(t * 14) * 2.2 * s;
          eye.targetLookX = Math.min(8.5 * s, dx * 0.24) + scanOffset * 0.4;
          eye.targetLookY = dy * 0.22 + (this.calc.activeBtn % 3 - 1) * 2.2 * s;
          eye.targetPupilScale = 0.80;
        }
      }
    } else if (this.followCursor && this.pointer.active && this.state !== 'sleepy') {
      const dx = this.pointer.x - this.bodyX;
      const dy = this.pointer.y - this.bodyY;
      const dist = Math.hypot(dx, dy);
      const maxFloat = (this.state === 'curious' ? 25 : 19) * s;
      const factor = Math.min(maxFloat, dist * 0.28);
      const ang = Math.atan2(dy, dx);

      eye.targetX = Math.cos(ang) * factor;
      eye.targetY = Math.sin(ang) * factor;
      eye.targetLookX = Math.cos(ang) * Math.min(8 * s, dist * 0.11);
      eye.targetLookY = Math.sin(ang) * Math.min(8 * s, dist * 0.11);
      eye.targetDepth = this.state === 'curious' ? 0.95 : 0.45;
    } else if (this.state === 'thinking') {
      eye.targetX = Math.cos(t * 2.8) * 18 * s;
      eye.targetY = (Math.sin(t * 5.6) * 10 - 3) * s;
      eye.targetLookX = Math.cos(t * 2.8 + 0.5) * 6 * s;
      eye.targetLookY = (-5 + Math.sin(t * 2.8) * 3) * s;
      eye.targetDepth = Math.sin(t * 2.8) * 0.5;
    } else if (this.state === 'curious') {
      eye.saccadeTimer -= dt;
      if (eye.saccadeTimer <= 0) {
        eye.saccadeTimer = 0.7 + Math.random() * 1.1;
        const ang = (Math.random() - 0.5) * Math.PI * 1.4;
        const rad = (12 + Math.random() * 12) * s;
        eye.targetX = Math.cos(ang) * rad;
        eye.targetY = Math.sin(ang) * rad * 0.8;
        eye.targetLookX = Math.cos(ang) * 7 * s;
        eye.targetLookY = Math.sin(ang) * 6 * s;
      }
    } else if (this.state === 'happy') {
      eye.targetX = Math.sin(t * 4.5) * 8 * s;
      eye.targetY = (-6 + Math.cos(t * 9.0) * 5) * s;
      eye.targetLookX = Math.sin(t * 4.5) * 3 * s;
      eye.targetLookY = -2 * s;
    } else if (this.state === 'sleepy') {
      eye.targetX = 0;
      eye.targetY = 8 * s;
      eye.targetLookX = 0;
      eye.targetLookY = 4 * s;
    } else {
      eye.saccadeTimer -= dt;
      if (eye.saccadeTimer <= 0) {
        eye.saccadeTimer = 1.1 + Math.random() * 2.4;
        if (Math.random() < 0.32) {
          eye.targetX = (Math.random() - 0.5) * 6 * s;
          eye.targetY = (Math.random() - 0.5) * 6 * s;
          eye.targetLookX = 0;
          eye.targetLookY = 0;
          eye.targetDepth = 0;
        } else {
          const ang = Math.random() * Math.PI * 2;
          const dist = (7 + Math.random() * 14) * s;
          eye.targetX = Math.cos(ang) * dist;
          eye.targetY = Math.sin(ang) * dist * 0.85;
          eye.targetLookX = Math.cos(ang) * (4 + Math.random() * 4) * s;
          eye.targetLookY = Math.sin(ang) * (4 + Math.random() * 4) * s;
          eye.targetDepth = (Math.random() - 0.35) * 0.8;
        }
      }
    }

    eye.vx = (eye.vx + (eye.targetX - eye.x) * 0.085 - this.bodyVX * 0.14) * 0.80;
    eye.vy = (eye.vy + (eye.targetY - eye.y) * 0.085 - this.bodyVY * 0.14) * 0.80;
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

  _traceJellyPath(ctx, scale = 1.0, offsetX = 0, offsetY = 0) {
    const pts = this.nodes.map((n) => ({
      x: this.bodyX + offsetX + (n.x - this.bodyX) * scale,
      y: this.bodyY + offsetY + (n.y - this.bodyY) * scale
    }));
    const len = pts.length;
    ctx.beginPath();
    ctx.moveTo((pts[len - 1].x + pts[0].x) * 0.5, (pts[len - 1].y + pts[0].y) * 0.5);
    for (let i = 0; i < len; i++) {
      const p1 = pts[i];
      const p2 = pts[(i + 1) % len];
      ctx.quadraticCurveTo(p1.x, p1.y, (p1.x + p2.x) * 0.5, (p1.y + p2.y) * 0.5);
    }
    ctx.closePath();
  }

  render(ctx = this.ctx) {
    const s = this.scaleRatio;
    ctx.clearRect(0, 0, this.w, this.h);

    // Shadow
    const heightOffset = Math.max(-25 * s, Math.min(25 * s, this.cy - this.bodyY));
    const shadowScale = 1 - (heightOffset / s) * 0.012;
    ctx.save();
    ctx.beginPath();
    ctx.ellipse(
      this.bodyX,
      this.cy + this.baseRadius + 18 * s,
      44 * s * shadowScale,
      9 * s * shadowScale,
      0, 0, Math.PI * 2
    );
    ctx.fillStyle = 'rgba(0, 0, 0, 0.22)';
    ctx.fill();
    ctx.restore();

    // Outer Glow
    ctx.save();
    this._traceJellyPath(ctx, 1.06);
    ctx.fillStyle = this.theme.glow;
    ctx.filter = `blur(${Math.round(8 * s)}px)`;
    ctx.fill();
    ctx.restore();

    // Jelly Body Gradient
    ctx.save();
    this._traceJellyPath(ctx, 1.0);
    const grad = ctx.createRadialGradient(
      this.bodyX + this.eye.x * 0.45 - 12 * s,
      this.bodyY + this.eye.y * 0.45 - 16 * s,
      8 * s,
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

    // Eye Core Halo inside Gel
    const eyeWorldX = this.bodyX + this.eye.x;
    const eyeWorldY = this.bodyY + this.eye.y;
    const coreHalo = ctx.createRadialGradient(eyeWorldX, eyeWorldY, 4 * s, eyeWorldX, eyeWorldY, 40 * s);
    coreHalo.addColorStop(0, 'rgba(255,255,255,0.35)');
    coreHalo.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = coreHalo;
    ctx.beginPath();
    ctx.arc(eyeWorldX, eyeWorldY, 40 * s, 0, Math.PI * 2);
    ctx.fill();

    // Back Bubbles
    for (let i = 0; i < this.bubbles.length; i += 2) {
      this._drawBubble(ctx, this.bubbles[i]);
    }

    // Submerged Calculator
    if (this.calc.phase === 'submerged') {
      this._drawInteractionPulse(ctx, eyeWorldX, eyeWorldY, this.bodyX + this.calc.x, this.bodyY + this.calc.y);
      this._drawCalculator(ctx, this.bodyX + this.calc.x, this.bodyY + this.calc.y, this.calc.angle);
    }

    // Submerged Vertical-Flip Notepad
    if (this.reader.padPhase === 'submerged') {
      this._drawNotepad(ctx, this.bodyX + this.reader.px, this.bodyY + this.reader.py, this.reader.pAngle);
    }

    // Floating Internal Eye
    this._drawInternalEye(ctx, eyeWorldX, eyeWorldY);

    // Submerged Golden Monocle with Chain
    if (this.reader.monoclePhase === 'submerged') {
      this._drawMonocle(ctx, this.bodyX + this.reader.mx, this.bodyY + this.reader.my, this.reader.mAngle);
    }

    // Front Bubbles
    for (let i = 1; i < this.bubbles.length; i += 2) {
      this._drawBubble(ctx, this.bubbles[i]);
    }

    // Translucent Gel Layer Over the Eye & Props
    const depthTintAlpha = 0.18 - this.eye.depth * 0.08;
    ctx.fillStyle = this.theme.tint;
    ctx.globalAlpha = Math.max(0.06, Math.min(0.32, depthTintAlpha));
    ctx.fillRect(0, 0, this.w, this.h);
    ctx.globalAlpha = 1;

    // Inner Caustic Rim
    this._traceJellyPath(ctx, 0.90, -3 * s, -4 * s);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
    ctx.lineWidth = 3 * s;
    ctx.stroke();
    ctx.restore();

    // Membrane Rim & Wet Specular Gloss
    ctx.save();
    this._traceJellyPath(ctx, 1.0);
    ctx.strokeStyle = this.theme.rim;
    ctx.lineWidth = 2.2 * s;
    ctx.stroke();

    const topNode = this.nodes[19];
    ctx.beginPath();
    ctx.ellipse(topNode.x + 14 * s, topNode.y + 13 * s, 17 * s, 7.5 * s, -0.52, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.62)';
    ctx.fill();

    ctx.beginPath();
    ctx.arc(topNode.x + 31 * s, topNode.y + 7 * s, 3.8 * s, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.55)';
    ctx.fill();
    ctx.restore();

    // Little Chick
    if (this.chickScene.phase !== 'none' && this.chickScene.chickX > -30 * s && this.chickScene.chickX < this.w + 30 * s) {
      this._drawChick(ctx);
    }

    // Gloop's Chubby Gelatinous Arm & Hand
    if (this.chickScene.armExtension > 0.02) {
      this._drawChubbyGelArm(ctx);
    }

    // Props in the Sky
    if (this.calc.phase === 'falling' || this.calc.phase === 'ejecting') {
      this._drawCalculator(ctx, this.bodyX + this.calc.x, this.bodyY + this.calc.y, this.calc.angle);
    }
    if (this.reader.padPhase === 'falling' || this.reader.padPhase === 'ejecting') {
      this._drawNotepad(ctx, this.bodyX + this.reader.px, this.bodyY + this.reader.py, this.reader.pAngle);
    }
    if (this.reader.monoclePhase === 'falling' || this.reader.monoclePhase === 'ejecting') {
      this._drawMonocle(ctx, this.bodyX + this.reader.mx, this.bodyY + this.reader.my, this.reader.mAngle);
    }

    // Particles
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
        ctx.shadowBlur = 6 * s;
        ctx.fillText(p.text, p.x, p.y);
      }
      ctx.restore();
    }
  }

  _drawChick(ctx) {
    const cs = this.chickScene;
    const s = this.scaleRatio;
    const x = cs.chickX;
    const y = cs.chickY;
    const isWalking = cs.phase === 'approaching' || cs.phase === 'walking_past';
    const legSwing = isWalking ? Math.sin(cs.walkCycle) * 5 * s : 0;

    ctx.save();

    // Chick Ground Shadow
    ctx.beginPath();
    ctx.ellipse(x, this.cy + this.baseRadius + 16 * s, 13 * s, 3.5 * s, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.20)';
    ctx.fill();

    ctx.translate(x, y);

    // Legs & Feet
    ctx.strokeStyle = '#ea580c';
    ctx.lineWidth = 2.2 * s;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    ctx.moveTo(-3 * s, -4 * s);
    ctx.lineTo(-3 * s - legSwing, 5 * s);
    ctx.lineTo(-7 * s - legSwing, 5 * s);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(3 * s, -4 * s);
    ctx.lineTo(3 * s + legSwing, 5 * s);
    ctx.lineTo(-1 * s + legSwing, 5 * s);
    ctx.stroke();

    const scaleX = 1 + cs.chickSquash * 0.65;
    const scaleY = 1 - cs.chickSquash;
    ctx.translate(0, 4 * s);
    ctx.scale(scaleX, scaleY);
    ctx.translate(0, -4 * s);

    const bodyGrad = ctx.createRadialGradient(-4 * s, -14 * s, 2 * s, 0, -10 * s, 16 * s);
    bodyGrad.addColorStop(0, '#fef08a');
    bodyGrad.addColorStop(0.6, '#facc15');
    bodyGrad.addColorStop(1, '#eab308');

    ctx.fillStyle = bodyGrad;
    ctx.strokeStyle = '#ca8a04';
    ctx.lineWidth = 1.5 * s;

    ctx.beginPath();
    ctx.ellipse(1 * s, -9 * s, 12.5 * s, 10.5 * s, 0.08, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(-6 * s, -18 * s, 9.2 * s, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(-2 * s, -13 * s, 8.2 * s, 0, Math.PI * 2);
    ctx.fill();

    const tuftBend = cs.chickSquash * 2.5 * s;
    ctx.beginPath();
    ctx.moveTo(-6 * s, -27 * s);
    ctx.quadraticCurveTo(-8 * s - tuftBend, -32 * s + tuftBend * 2, -4 * s - tuftBend, -31 * s + tuftBend * 2);
    ctx.quadraticCurveTo(-3 * s, -29 * s, -5 * s, -27 * s);
    ctx.fillStyle = '#facc15';
    ctx.fill();
    ctx.stroke();

    // Beak
    ctx.beginPath();
    ctx.moveTo(-14.5 * s, -19.5 * s);
    ctx.lineTo(-19.5 * s, -17.5 * s);
    ctx.lineTo(-14.5 * s, -15.5 * s);
    ctx.closePath();
    ctx.fillStyle = '#f97316';
    ctx.fill();
    ctx.strokeStyle = '#c2410c';
    ctx.lineWidth = 1 * s;
    ctx.stroke();

    // Blush
    ctx.beginPath();
    ctx.ellipse(-10.5 * s, -15 * s, 2.4 * s, 1.4 * s, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(251, 113, 133, 0.55)';
    ctx.fill();

    // Eye
    if (cs.happyEyes && cs.phase === 'petting') {
      ctx.beginPath();
      ctx.arc(-10 * s, -18.5 * s, 2.3 * s, Math.PI * 1.1, Math.PI * 1.9);
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1.7 * s;
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.arc(-10 * s, -19 * s, 2.0 * s, 0, Math.PI * 2);
      ctx.fillStyle = '#0f172a';
      ctx.fill();

      ctx.beginPath();
      ctx.arc(-10.6 * s, -19.6 * s, 0.75 * s, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
    }

    // Wing
    const wingFlutter = cs.phase === 'petting' ? Math.sin(cs.patCycle * 2) * 0.28 : (isWalking ? Math.sin(cs.walkCycle) * 0.1 : 0);
    ctx.save();
    ctx.translate(2 * s, -10 * s);
    ctx.rotate(-0.15 + wingFlutter);
    ctx.beginPath();
    ctx.ellipse(2 * s, 1 * s, 6.2 * s, 4.0 * s, 0.2, 0, Math.PI * 2);
    ctx.fillStyle = '#fde047';
    ctx.strokeStyle = '#ca8a04';
    ctx.lineWidth = 1.3 * s;
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    ctx.restore();
  }

  _drawChubbyGelArm(ctx) {
    const cs = this.chickScene;
    const s = this.scaleRatio;
    const ext = cs.armExtension;

    const sx = this.bodyX + this.baseRadius * 0.62;
    const sy = this.bodyY + 2 * s;
    const hx = cs.handX;
    const hy = cs.handY;

    const ctrlX = (sx + hx) * 0.5 + 4 * s;
    const ctrlY = Math.min(sy, hy) - 18 * s * ext;

    ctx.save();

    const armGrad = ctx.createLinearGradient(sx, sy, hx, hy);
    armGrad.addColorStop(0, this.theme.mid);
    armGrad.addColorStop(0.6, this.theme.core);
    armGrad.addColorStop(1, this.theme.mid);

    ctx.beginPath();
    ctx.moveTo(sx, sy - 11 * s);
    ctx.quadraticCurveTo(ctrlX, ctrlY - 9 * s, hx - 4 * s, hy - 6 * s);
    ctx.lineTo(hx - 4 * s, hy + 7 * s);
    ctx.quadraticCurveTo(ctrlX - 2 * s, ctrlY + 9 * s, sx, sy + 12 * s);
    ctx.closePath();

    ctx.fillStyle = armGrad;
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(sx + 6 * s, sy - 10 * s);
    ctx.quadraticCurveTo(ctrlX, ctrlY - 9 * s, hx - 4 * s, hy - 6 * s);
    ctx.strokeStyle = this.theme.rim;
    ctx.lineWidth = 2.1 * s;
    ctx.lineCap = 'round';
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(sx + 6 * s, sy + 11 * s);
    ctx.quadraticCurveTo(ctrlX - 2 * s, ctrlY + 9 * s, hx - 4 * s, hy + 7 * s);
    ctx.strokeStyle = this.theme.rim;
    ctx.lineWidth = 2.1 * s;
    ctx.stroke();

    // Chubby Hand & 3 Cute Fingers
    ctx.save();
    ctx.translate(hx, hy);
    const patTilt = cs.phase === 'petting' ? Math.sin(cs.patCycle) * 0.18 + 0.25 : 0.2;
    ctx.rotate(patTilt);

    ctx.beginPath();
    ctx.ellipse(0, 0, 10.5 * s, 8.2 * s, 0.15, 0, Math.PI * 2);
    ctx.fillStyle = this.theme.core;
    ctx.fill();
    ctx.strokeStyle = this.theme.rim;
    ctx.lineWidth = 2.0 * s;
    ctx.stroke();

    const fingerOffsets = [
      { x: 8.5 * s, y: -3.5 * s, r: 3.8 * s },
      { x: 9.8 * s, y: 0.8 * s,  r: 4.0 * s },
      { x: 7.5 * s, y: 4.8 * s,  r: 3.6 * s }
    ];
    for (const f of fingerOffsets) {
      ctx.beginPath();
      ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
      ctx.fillStyle = this.theme.core;
      ctx.fill();
      ctx.strokeStyle = this.theme.rim;
      ctx.lineWidth = 1.6 * s;
      ctx.stroke();
    }

    ctx.beginPath();
    ctx.ellipse(-2 * s, 6.5 * s, 4.2 * s, 3.0 * s, 0.5, 0, Math.PI * 2);
    ctx.fillStyle = this.theme.core;
    ctx.fill();
    ctx.strokeStyle = this.theme.rim;
    ctx.lineWidth = 1.5 * s;
    ctx.stroke();

    ctx.beginPath();
    ctx.ellipse(1 * s, 0.5 * s, 8.8 * s, 6.8 * s, 0.15, 0, Math.PI * 2);
    ctx.fillStyle = this.theme.core;
    ctx.fill();

    ctx.beginPath();
    ctx.ellipse(-1 * s, -3.2 * s, 5.2 * s, 2.2 * s, -0.2, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.65)';
    ctx.fill();

    ctx.restore();
    ctx.restore();
  }

  _drawMonocle(ctx, x, y, angle) {
    const s = this.scaleRatio;
    const r = 16.5 * s;
    const swing = this.reader.chainSwing;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    ctx.save();
    const attachX = -r + 1 * s;
    const attachY = 3 * s;
    const endX = attachX - 5 * s + Math.sin(swing) * 14 * s;
    const endY = attachY + 34 * s;
    const ctrlX = attachX - 10 * s + Math.sin(swing * 1.3) * 18 * s;
    const ctrlY = attachY + 20 * s;

    ctx.beginPath();
    ctx.moveTo(attachX, attachY);
    ctx.quadraticCurveTo(ctrlX, ctrlY, endX, endY);
    ctx.strokeStyle = '#fbbf24';
    ctx.lineWidth = 1.8 * s;
    ctx.setLineDash([2.2 * s, 2.2 * s]);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.beginPath();
    ctx.arc(attachX - 1.5 * s, attachY, 2.3 * s, 0, Math.PI * 2);
    ctx.strokeStyle = '#fde047';
    ctx.lineWidth = 1.5 * s;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(endX, endY, 2.4 * s, 0, Math.PI * 2);
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
    ctx.moveTo(-r, -r + 4 * s);
    ctx.lineTo(-r + 9 * s, -r + 4 * s);
    ctx.lineTo(r - 4 * s, r - 4 * s);
    ctx.lineTo(r - 13 * s, r - 4 * s);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    ctx.beginPath();
    ctx.arc(0, 0, r, 0, Math.PI * 2);
    ctx.strokeStyle = '#d97706';
    ctx.lineWidth = 3.2 * s;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(0, 0, r, 0, Math.PI * 2);
    ctx.strokeStyle = '#fde047';
    ctx.lineWidth = 1.4 * s;
    ctx.stroke();

    ctx.fillStyle = '#fbbf24';
    this._roundRect(ctx, r - 1.5 * s, -4 * s, 3.8 * s, 7 * s, 1.2 * s);
    ctx.fill();

    ctx.restore();
  }

  _drawNotepad(ctx, x, y, angle) {
    const s = this.scaleRatio;
    const w = 30 * s;
    const h = 38 * s;
    const r = 3.5 * s;
    const rd = this.reader;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    ctx.fillStyle = 'rgba(0, 15, 10, 0.26)';
    this._roundRect(ctx, -w / 2 + 2 * s, -h / 2 + 3 * s, w, h, r);
    ctx.fill();

    ctx.fillStyle = '#78350f';
    this._roundRect(ctx, -w / 2, -h / 2 + 1 * s, w, h + 1.5 * s, r);
    ctx.fill();

    ctx.fillStyle = '#fef3c7';
    ctx.strokeStyle = '#d97706';
    ctx.lineWidth = 1 * s;
    this._roundRect(ctx, -w / 2 + 1 * s, -h / 2 + 2 * s, w - 2 * s, h - 2.5 * s, r - 1 * s);
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(-w / 2 + 6 * s, -h / 2 + 5 * s);
    ctx.lineTo(-w / 2 + 6 * s, h / 2 - 2 * s);
    ctx.strokeStyle = 'rgba(244, 63, 94, 0.35)';
    ctx.lineWidth = 0.8 * s;
    ctx.stroke();

    this._drawPageLines(ctx, w, h, rd.isFlipping ? -1 : rd.currentLine, rd.lineProgress);

    if (rd.isFlipping) {
      const p = rd.flipProgress;
      const pageH = h - 3 * s;
      const cosP = Math.cos(p * Math.PI);

      ctx.save();
      ctx.translate(0, -h / 2 + 2 * s);

      if (cosP > 0) {
        ctx.fillStyle = `rgba(0, 0, 0, ${(1 - cosP) * 0.22})`;
        ctx.fillRect(-w / 2 + 1.5 * s, 2 * s, w - 3 * s, pageH * cosP);
      }

      ctx.scale(1, cosP);

      ctx.beginPath();
      ctx.moveTo(-w / 2 + 1 * s, 0);
      ctx.lineTo(w / 2 - 1 * s, 0);
      const curlX = Math.sin(p * Math.PI) * 3.5 * s;
      ctx.lineTo(w / 2 - 1 * s + curlX, pageH);
      ctx.quadraticCurveTo(curlX, pageH - Math.sin(p * Math.PI) * 4 * s, -w / 2 + 1 * s + curlX, pageH);
      ctx.closePath();

      ctx.fillStyle = cosP >= 0 ? '#fffbeb' : '#fde68a';
      ctx.strokeStyle = '#d97706';
      ctx.lineWidth = 0.9 * s;
      ctx.fill();
      ctx.stroke();

      ctx.strokeStyle = 'rgba(71, 85, 105, 0.45)';
      ctx.lineWidth = 1.2 * s;
      for (let line = 0; line < 4; line++) {
        const ly = (8 + line * 6.5) * s;
        ctx.beginPath();
        ctx.moveTo(-w / 2 + 5 * s, ly);
        ctx.lineTo(w / 2 - 6 * s, ly);
        ctx.stroke();
      }

      ctx.restore();
    }

    const numRings = 5;
    const ringSpan = w - 8 * s;
    for (let i = 0; i < numRings; i++) {
      const rx = -ringSpan / 2 + (i / (numRings - 1)) * ringSpan;
      const ry = -h / 2 + 1.5 * s;

      ctx.beginPath();
      ctx.arc(rx, ry + 2.5 * s, 1.3 * s, 0, Math.PI * 2);
      ctx.fillStyle = '#78350f';
      ctx.fill();

      ctx.beginPath();
      ctx.ellipse(rx, ry, 1.4 * s, 3.2 * s, 0.1, 0, Math.PI * 2);
      ctx.strokeStyle = '#e2e8f0';
      ctx.lineWidth = 1.35 * s;
      ctx.stroke();
    }

    ctx.restore();
  }

  _drawPageLines(ctx, w, h, activeLine, lineProgress) {
    const s = this.scaleRatio;
    const lineLengths = [17 * s, 14 * s, 18 * s, 12 * s];
    for (let i = 0; i < 4; i++) {
      const ly = -h / 2 + (10 + i * 6.5) * s;
      const startX = -w / 2 + 7.5 * s;
      const fullLen = lineLengths[i];

      ctx.beginPath();
      ctx.moveTo(-w / 2 + 3 * s, ly + 2 * s);
      ctx.lineTo(w / 2 - 3 * s, ly + 2 * s);
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.35)';
      ctx.lineWidth = 0.7 * s;
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(startX, ly);
      ctx.lineTo(startX + fullLen, ly);
      ctx.strokeStyle = i < activeLine ? '#0f172a' : '#64748b';
      ctx.lineWidth = 1.6 * s;
      ctx.lineCap = 'round';
      ctx.stroke();

      if (i === activeLine) {
        const readLen = Math.max(2 * s, fullLen * lineProgress);
        ctx.beginPath();
        ctx.moveTo(startX, ly);
        ctx.lineTo(startX + readLen, ly);
        ctx.strokeStyle = '#059669';
        ctx.lineWidth = 2.0 * s;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(startX + readLen, ly, 1.6 * s, 0, Math.PI * 2);
        ctx.fillStyle = '#10b981';
        ctx.fill();
      }
    }
  }

  _drawInteractionPulse(ctx, ex, ey, cx, cy) {
    if (this.calc.pulseWave <= 0) return;
    const s = this.scaleRatio;
    const prog = 1 - this.calc.pulseWave;
    const px = ex + (cx - ex) * (0.35 + prog * 0.55);
    const py = ey + (cy - ey) * (0.35 + prog * 0.55);

    ctx.save();
    ctx.beginPath();
    ctx.arc(px, py, (4 + prog * 8) * s, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(255, 255, 255, ${this.calc.pulseWave * 0.75})`;
    ctx.lineWidth = 2 * s;
    ctx.stroke();
    ctx.restore();
  }

  _drawCalculator(ctx, x, y, angle) {
    const s = this.scaleRatio;
    const w = 30 * s;
    const h = 38 * s;
    const r = 5 * s;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    ctx.fillStyle = 'rgba(0, 15, 10, 0.28)';
    this._roundRect(ctx, -w / 2 + 2 * s, -h / 2 + 3 * s, w, h, r);
    ctx.fill();

    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 1.5 * s;
    this._roundRect(ctx, -w / 2, -h / 2, w, h, r);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#a7f3d0';
    this._roundRect(ctx, -w / 2 + 4 * s, -h / 2 + 4 * s, w - 8 * s, 10 * s, 2 * s);
    ctx.fill();

    ctx.fillStyle = '#064e3b';
    ctx.font = `bold ${Math.max(6, 7.5 * s)}px monospace`;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(this.calc.screenText, w / 2 - 5.5 * s, -h / 2 + 9.5 * s);

    const startX = -w / 2 + 4.5 * s;
    const startY = -h / 2 + 17 * s;
    const bw = 6 * s;
    const bh = 4.8 * s;
    const gapX = 1.5 * s;
    const gapY = 1.8 * s;

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

        this._roundRect(ctx, bx, by + (isPressed ? 0.8 * s : 0), bw, bh, 1.2 * s);
        ctx.fill();
      }
    }

    ctx.restore();
  }

  _roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  _drawBubble(ctx, b) {
    const bx = this.bodyX + b.x;
    const by = this.bodyY + b.y;
    ctx.save();
    ctx.beginPath();
    ctx.arc(bx, by, b.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255, 255, 255, ${b.alpha})`;
    ctx.fill();
    ctx.restore();
  }

  _drawInternalEye(ctx, ex, ey) {
    const eye = this.eye;
    const s = this.scaleRatio;
    const r = eye.radius * (1 + eye.depth * 0.12);

    ctx.save();
    ctx.translate(ex, ey);

    ctx.beginPath();
    ctx.arc(0, 3 * s, r * 1.08, 0, Math.PI * 2);
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
      ctx.arc(0, 2 * s, pupilR * 0.65, Math.PI * 1.15, Math.PI * 1.85);
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2.5 * s;
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

  start() {
    if (this._rafId) return;
    let last = performance.now();
    const loop = (now) => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      this.update(dt);
      this.render();
      this._rafId = requestAnimationFrame(loop);
    };
    this._rafId = requestAnimationFrame(loop);
  }

  stop() {
    if (this._rafId) {
      cancelAnimationFrame(this._rafId);
      this._rafId = null;
    }
  }
}

/**
 * Custom Web Component: <jelly-alien state="petting_chick" theme="emerald" size="240"></jelly-alien>
 */
if (typeof customElements !== 'undefined' && !customElements.get('jelly-alien')) {
  class JellyAlienElement extends HTMLElement {
    static get observedAttributes() {
      return ['state', 'theme', 'size', 'squish'];
    }

    connectedCallback() {
      const size = parseInt(this.getAttribute('size') || '240', 10);
      const shadow = this.shadowRoot || this.attachShadow({ mode: 'open' });
      shadow.innerHTML = `<canvas width="${size}" height="${size}" style="display:block; cursor:pointer; user-select:none;"></canvas>`;
      const canvas = shadow.querySelector('canvas');

      this.mascot = new JellyAlienMascot(canvas, {
        state: this.getAttribute('state') || 'idle',
        theme: this.getAttribute('theme') || 'emerald',
        squishFactor: parseFloat(this.getAttribute('squish') || '1.0'),
        followCursor: this.hasAttribute('follow-cursor') || true
      });
    }

    attributeChangedCallback(name, _oldVal, newVal) {
      if (!this.mascot) return;
      if (name === 'state') this.mascot.setState(newVal);
      if (name === 'theme') this.mascot.setTheme(newVal);
      if (name === 'squish') this.mascot.squishFactor = parseFloat(newVal) || 1.0;
    }

    disconnectedCallback() {
      if (this.mascot) this.mascot.destroy();
    }
  }
  customElements.define('jelly-alien', JellyAlienElement);
}

if (typeof window !== 'undefined') {
  window.JellyAlienMascot = JellyAlienMascot;
  window.JELLY_THEMES = JELLY_THEMES;
}

export { JellyAlienMascot, JELLY_THEMES };
