/**
 * JellyCompanionMascot ("Lumi") - Floating Tentacled Jellyfish Alien Companion
 * Zero dependencies. Uses 2D Canvas with soft-body medusa dome physics,
 * 6 independent multi-segment IK/wave tentacles with bioluminescent pulse nodes,
 * an internal floating eye suspended in translucent gel, and 9 animations:
 *   - 'idle': Living levitation with jellyfish propulsion & undulating tentacles
 *   - 'cosmic_boba': Holds a zero-G Boba Tea cup with tentacles & sips pearls into her translucent bell!
 *   - 'juggling_orbs': Juggles 3 glowing cosmic orbs in a figure-8 cascade using feeler tentacles
 *   - 'dj_headphones': Wears glowing cyber-headphones & scratches a holographic vinyl record
 *   - 'abducting_duck': Projects a tractor beam from underneath her bell to levitate & tickle a space rubber duck
 *   - 'hypnotic', 'happy_spin', 'electro_shock', 'sleepy_drift'
 *
 * Usage 1 (Web Component):
 *   <script type="module" src="jelly-companion.js"></script>
 *   <jelly-companion state="idle" theme="astral" size="260" auto-random></jelly-companion>
 *
 * Usage 2 (JavaScript Class):
 *   const lumi = new JellyCompanionMascot(canvas, { theme: 'astral', autoRandom: true });
 *   lumi.setState('cosmic_boba');
 */

export const LUMI_THEMES = {
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

export class JellyCompanionMascot {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.w = canvas.width || 260;
    this.h = canvas.height || 250;

    this.themeName = options.theme || 'astral';
    this.theme = LUMI_THEMES[this.themeName] || LUMI_THEMES.astral;
    this.state = options.state || 'idle';
    this.stateTimer = 0;
    this.tentacleFlow = options.tentacleFlow ?? 1.0;
    this.autoRandom = options.autoRandom ?? true;
    this.minIdle = options.minIdle ?? 12;
    this.maxIdle = options.maxIdle ?? 28;
    this.nextRandomTimer = this._randomInterval();
    this.lastRandomState = '';
    this.onStateChange = options.onStateChange || null;

    this.time = 0;
    this._rafId = null;

    this.baseCx = this.w * 0.5;
    this.baseCy = this.h * 0.40;
    this.bellX = this.baseCx;
    this.bellY = this.baseCy;
    this.bellVx = 0;
    this.bellVy = 0;
    this.bellRadius = 48 * (Math.min(this.w, this.h) / 250);
    this.bellScaleX = 1;
    this.bellScaleY = 1;
    this.bellRotation = 0;
    this.pulsePhase = 0;

    this.numNodes = 26;
    this.nodes = Array.from({ length: this.numNodes }, (_, i) => ({
      angle: (i / this.numNodes) * Math.PI * 2,
      r: this.bellRadius,
      vr: 0,
      x: 0,
      y: 0
    }));

    this.numTentacles = 6;
    this.segments = 9;
    this.tentacles = Array.from({ length: this.numTentacles }, (_, t) => {
      const norm = (t / (this.numTentacles - 1)) * 2 - 1;
      const isFeeler = (t === 0 || t === this.numTentacles - 1);
      const segLen = isFeeler ? 8.2 : 6.8 + (t % 2) * 1.1;
      const pts = Array.from({ length: this.segments }, (_, s) => ({
        x: this.baseCx + norm * 28,
        y: this.baseCy + 20 + s * segLen,
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

    this.eye = {
      x: this.baseCx,
      y: this.baseCy - 4,
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

    this.bubbles = Array.from({ length: 11 }, (_, i) => ({
      angle: (i / 11) * Math.PI * 2,
      dist: 10 + Math.random() * 26,
      r: 1.6 + Math.random() * 2.8,
      speed: 0.4 + Math.random() * 0.6
    }));

    this.particles = [];
    this.bobaProp = { active: false, cupX: this.w + 40, cupY: this.baseCy + 12, liquidLevel: 1.0, slurpPhase: 0, strawPearlProg: -1, insidePearls: [] };
    this.juggleProp = {
      active: false,
      phase: 0,
      orbs: [
        { color: '#fde047', glow: '#f59e0b', x: 0, y: 0 },
        { color: '#38bdf8', glow: '#0284c7', x: 0, y: 0 },
        { color: '#f472b6', glow: '#db2777', x: 0, y: 0 }
      ]
    };
    this.djProp = { active: false, headphoneY: -60, beatPhase: 0, vinylAngle: 0, deckAlpha: 0 };
    this.duckProp = { active: false, x: this.w + 30, y: this.h - 24, beamPower: 0, duckSpin: 0 };
    this.pointer = { x: this.w / 2, y: this.h / 2, active: false };

    this._bindEvents();
    this.setState(this.state);
    this.start();
  }

  _randomInterval() {
    return this.minIdle + Math.random() * Math.max(1, this.maxIdle - this.minIdle);
  }

  _bindEvents() {
    this.canvas.addEventListener('pointermove', e => {
      const rect = this.canvas.getBoundingClientRect();
      this.pointer.x = (e.clientX - rect.left) * (this.w / rect.width);
      this.pointer.y = (e.clientY - rect.top) * (this.h / rect.height);
      this.pointer.active = true;
    });
    this.canvas.addEventListener('pointerleave', () => {
      this.pointer.active = false;
    });
    this.canvas.addEventListener('pointerdown', () => {
      this.boostHover();
    });
  }

  setTheme(themeName) {
    if (LUMI_THEMES[themeName]) {
      this.themeName = themeName;
      this.theme = LUMI_THEMES[themeName];
    }
  }

  setState(newState) {
    this.state = newState;
    this.stateTimer = 0;

    this.bobaProp.active = (newState === 'cosmic_boba');
    if (this.bobaProp.active) {
      this.bobaProp.cupX = this.w + 45;
      this.bobaProp.cupY = this.baseCy + 12;
      this.bobaProp.liquidLevel = 1.0;
      this.bobaProp.slurpPhase = 0;
      this.bobaProp.strawPearlProg = -1;
      this.bobaProp.insidePearls = [];
    }

    this.juggleProp.active = (newState === 'juggling_orbs');
    if (this.juggleProp.active) this.juggleProp.phase = 0;

    this.djProp.active = (newState === 'dj_headphones');
    if (this.djProp.active) {
      this.djProp.headphoneY = -60;
      this.djProp.beatPhase = 0;
      this.djProp.deckAlpha = 0;
    }

    this.duckProp.active = (newState === 'abducting_duck');
    if (this.duckProp.active) {
      this.duckProp.x = this.w + 30;
      this.duckProp.y = this.h - 24;
      this.duckProp.beamPower = 0;
      this.duckProp.duckSpin = 0;
    }

    this.bellVy -= 2.2;
    for (const n of this.nodes) {
      n.vr += (Math.random() - 0.5) * 3.5;
    }

    if (this.onStateChange) this.onStateChange(newState);
  }

  triggerRandomAnimation() {
    const pool = [
      'cosmic_boba', 'cosmic_boba',
      'juggling_orbs', 'juggling_orbs',
      'dj_headphones', 'dj_headphones',
      'abducting_duck', 'abducting_duck',
      'hypnotic', 'happy_spin', 'electro_shock'
    ].filter(s => s !== this.lastRandomState);
    const pick = pool[Math.floor(Math.random() * pool.length)];
    this.lastRandomState = pick;
    this.setState(pick);
    this.nextRandomTimer = this._randomInterval();
  }

  boostHover() {
    this.bellVy -= 4.5;
    this.bellScaleX = 0.88;
    this.bellScaleY = 1.14;
    for (const n of this.nodes) {
      n.vr += Math.sin(n.angle * 3) * 4.5;
    }
    this.spawnParticle(this.bellX + (Math.random() - 0.5) * 30, this.bellY + 25, '✦', this.theme.tentacleTip, 1.2);
  }

  spawnParticle(x, y, text, color = '#ffffff', vy = -1.1) {
    this.particles.push({
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

  _getDomeRestRadius(angle, pulse) {
    const sinA = Math.sin(angle);
    let r = this.bellRadius;
    if (sinA < 0) {
      r *= 1.0 + Math.abs(sinA) * 0.06;
    } else {
      const skirtFlare = Math.pow(sinA, 0.7) * 5.5;
      const scallop = Math.cos(angle * 6) * 2.2 * sinA;
      r += skirtFlare + scallop - sinA * 6.5;
    }
    r += Math.cos(angle * 2) * pulse * 3.8 * this.tentacleFlow;
    return r;
  }

  update(dt) {
    this.time += dt;
    this.stateTimer += dt;

    if (this.state === 'idle') {
      if (this.autoRandom) {
        this.nextRandomTimer -= dt;
        if (this.nextRandomTimer <= 0) this.triggerRandomAnimation();
      }
    } else {
      const maxDur = STATE_DURATIONS[this.state] || 6.0;
      if (this.stateTimer >= maxDur) {
        this.setState('idle');
        this.nextRandomTimer = this._randomInterval();
      }
    }

    for (const t of this.tentacles) t.targetWeight *= 0.85;

    const pulseSpeed = this.state === 'sleepy_drift' ? 1.6 : (this.state === 'dj_headphones' ? 6.6 : 2.8);
    this.pulsePhase += dt * pulseSpeed;
    const swimPulse = Math.sin(this.pulsePhase);

    let targetX = this.baseCx + Math.sin(this.time * 1.1) * 7;
    let targetY = this.baseCy + Math.cos(this.time * 2.2) * 9 - swimPulse * 4;
    this.bellRotation *= 0.88;

    if (this.state === 'happy_spin') {
      this.bellRotation = Math.sin(this.stateTimer * Math.PI * 1.6) * 0.35;
      targetY = this.baseCy - Math.abs(Math.sin(this.stateTimer * 5.5)) * 18;
      if (Math.random() < 0.28) {
        this.spawnParticle(this.bellX + (Math.random() - 0.5) * 65, this.bellY + (Math.random() - 0.5) * 50, '✦', this.theme.tentacleTip, -1.0);
      }
    } else if (this.state === 'electro_shock') {
      targetX += (Math.random() - 0.5) * 10;
      targetY += (Math.random() - 0.5) * 8;
      if (Math.random() < 0.35) {
        this.spawnParticle(this.bellX + (Math.random() - 0.5) * 70, this.bellY + (Math.random() - 0.5) * 60, '⚡', '#67e8f9', -1.4);
      }
    } else if (this.state === 'sleepy_drift') {
      targetY = this.baseCy + 10 + Math.sin(this.time * 1.1) * 6;
      if (Math.random() < 0.04) {
        this.spawnParticle(this.bellX + 18, this.bellY - 26, 'z', this.theme.rim, -0.65);
      }
    } else if (this.state === 'hypnotic') {
      targetX = this.baseCx + Math.sin(this.time * 2.4) * 12;
      targetY = this.baseCy + Math.cos(this.time * 2.4) * 7;
    }

    if (this.state === 'cosmic_boba') {
      const t = this.stateTimer;
      const holdX = this.bellX + 46;
      const holdY = this.bellY + 14;
      if (t < 1.1) {
        const p = t / 1.1;
        const ease = 1 - Math.pow(1 - p, 3);
        this.bobaProp.cupX = this.w + 40 + (holdX - (this.w + 40)) * ease;
        this.bobaProp.cupY = holdY + Math.sin(this.time * 4) * 3;
      } else if (t < 7.2) {
        this.bobaProp.cupX = holdX + Math.sin(this.time * 3) * 2;
        this.bobaProp.cupY = holdY + Math.cos(this.time * 2.5) * 2.5;
        this.tentacles[5].targetX = this.bobaProp.cupX + 4;
        this.tentacles[5].targetY = this.bobaProp.cupY + 6;
        this.tentacles[5].targetWeight = 0.95;
        this.tentacles[0].targetX = this.bellX + 24;
        this.tentacles[0].targetY = this.bellY + 4;
        this.tentacles[0].targetWeight = 0.85;

        const prevSlurp = Math.floor(this.bobaProp.slurpPhase);
        this.bobaProp.slurpPhase += dt * 1.35;
        if (Math.floor(this.bobaProp.slurpPhase) > prevSlurp && this.bobaProp.liquidLevel > 0.12) {
          this.bobaProp.strawPearlProg = 0.0;
          this.bobaProp.liquidLevel = Math.max(0.08, this.bobaProp.liquidLevel - 0.14);
          this.bellScaleX = 0.92;
          this.bellScaleY = 1.08;
          this.spawnParticle(this.bobaProp.cupX, this.bobaProp.cupY - 26, '♥', '#f472b6', -1.1);
        }

        if (this.bobaProp.strawPearlProg >= 0) {
          this.bobaProp.strawPearlProg += dt * 2.8;
          if (this.bobaProp.strawPearlProg >= 1.0) {
            this.bobaProp.strawPearlProg = -1;
            this.bobaProp.insidePearls.push({
              x: this.bellX + 18,
              y: this.bellY + 2,
              vx: -2.2 - Math.random() * 1.5,
              vy: -1.8 + (Math.random() - 0.5) * 2.2,
              color: Math.random() < 0.5 ? '#c084fc' : '#38bdf8',
              alpha: 1.0
            });
          }
        }
      } else {
        this.bobaProp.cupX += 3.6;
        this.bobaProp.cupY -= 1.2;
        for (const ip of this.bobaProp.insidePearls) ip.alpha = Math.max(0, ip.alpha - dt * 1.2);
      }

      for (const ip of this.bobaProp.insidePearls) {
        ip.x += ip.vx;
        ip.y += ip.vy;
        ip.vx *= 0.96;
        ip.vy *= 0.96;
        const dx = ip.x - this.bellX;
        const dy = ip.y - (this.bellY - 2);
        const dist = Math.hypot(dx, dy);
        if (dist > this.bellRadius * 0.58) {
          const nx = dx / (dist || 1);
          const ny = dy / (dist || 1);
          ip.x = this.bellX + nx * this.bellRadius * 0.56;
          ip.y = (this.bellY - 2) + ny * this.bellRadius * 0.56;
          ip.vx = -ip.vx * 0.7 - nx * 0.6;
          ip.vy = -ip.vy * 0.7 - ny * 0.6;
        }
      }
    }

    if (this.state === 'juggling_orbs') {
      this.juggleProp.phase += dt * 4.2;
      const leftHandX = this.bellX - 48;
      const rightHandX = this.bellX + 48;
      const handY = this.bellY + 10;

      for (let i = 0; i < 3; i++) {
        const p = (this.juggleProp.phase + (i * Math.PI * 2) / 3) % (Math.PI * 2);
        this.juggleProp.orbs[i].x = this.bellX + Math.sin(p) * 48;
        this.juggleProp.orbs[i].y = handY - Math.abs(Math.sin(p * 2)) * 56 - 8;
      }

      this.tentacles[0].targetX = leftHandX + Math.cos(this.juggleProp.phase * 2) * 10;
      this.tentacles[0].targetY = handY - Math.max(0, Math.sin(this.juggleProp.phase * 2)) * 16;
      this.tentacles[0].targetWeight = 0.95;

      this.tentacles[5].targetX = rightHandX - Math.cos(this.juggleProp.phase * 2) * 10;
      this.tentacles[5].targetY = handY - Math.max(0, -Math.sin(this.juggleProp.phase * 2)) * 16;
      this.tentacles[5].targetWeight = 0.95;
    }

    if (this.state === 'dj_headphones') {
      const t = this.stateTimer;
      this.djProp.beatPhase += dt * 8.5;
      this.djProp.vinylAngle += dt * 4.5;
      if (t < 0.9) {
        const p = t / 0.9;
        this.djProp.headphoneY = -60 + (this.bellY - 6 - (-60)) * (1 - Math.pow(1 - p, 3));
        this.djProp.deckAlpha = p;
      } else if (t < 7.4) {
        this.djProp.headphoneY = this.bellY - 6;
        this.djProp.deckAlpha = 1.0;
        targetY = this.baseCy + Math.sin(this.djProp.beatPhase) * 6;
        this.bellScaleX = 1.0 + Math.sin(this.djProp.beatPhase) * 0.06;
        this.bellScaleY = 1.0 - Math.sin(this.djProp.beatPhase) * 0.06;

        this.tentacles[0].targetX = this.bellX - 44;
        this.tentacles[0].targetY = this.bellY - 4;
        this.tentacles[0].targetWeight = 0.92;

        this.tentacles[5].targetX = this.bellX + 44 + Math.sin(this.time * 14) * 9;
        this.tentacles[5].targetY = this.bellY + 23;
        this.tentacles[5].targetWeight = 0.95;

        if (Math.random() < 0.16) {
          const notes = ['♪', '♫', '♬'];
          this.spawnParticle(
            this.bellX + (Math.random() - 0.5) * 75,
            this.bellY - 25,
            notes[Math.floor(Math.random() * notes.length)],
            Math.random() < 0.5 ? '#38bdf8' : '#f472b6',
            -1.25
          );
        }
      } else {
        this.djProp.headphoneY -= 5.5;
        this.djProp.deckAlpha = Math.max(0, this.djProp.deckAlpha - dt * 2.5);
      }
    }

    if (this.state === 'abducting_duck') {
      const t = this.stateTimer;
      if (t < 1.6) {
        const p = t / 1.6;
        this.duckProp.x = this.w + 30 + (this.bellX - (this.w + 30)) * (1 - Math.pow(1 - p, 2));
        this.duckProp.y = this.h - 22 + Math.sin(this.time * 6) * 2;
        this.duckProp.beamPower = 0;
      } else if (t < 5.6) {
        this.duckProp.beamPower = Math.min(1, this.duckProp.beamPower + dt * 3.5);
        this.duckProp.x = this.bellX + Math.sin(this.time * 3.5) * 5;
        const levitateTargetY = this.bellY + 48 + Math.sin(this.time * 4) * 5;
        this.duckProp.y += (levitateTargetY - this.duckProp.y) * 0.08;
        this.duckProp.duckSpin = Math.sin(this.time * 3.2) * 0.25;

        this.tentacles[0].targetX = this.duckProp.x - 18;
        this.tentacles[0].targetY = this.duckProp.y - 4 + Math.sin(this.time * 12) * 4;
        this.tentacles[0].targetWeight = 0.9;

        this.tentacles[5].targetX = this.duckProp.x + 18;
        this.tentacles[5].targetY = this.duckProp.y - 4 + Math.cos(this.time * 12) * 4;
        this.tentacles[5].targetWeight = 0.9;

        if (Math.random() < 0.14) {
          this.spawnParticle(this.duckProp.x + (Math.random() - 0.5) * 26, this.duckProp.y - 12, Math.random() < 0.5 ? '♥' : '★', '#fde047', -1.0);
        }
      } else {
        this.duckProp.beamPower = Math.max(0, this.duckProp.beamPower - dt * 3.5);
        this.duckProp.y += (this.h - 22 - this.duckProp.y) * 0.12;
        this.duckProp.x -= 3.4;
        this.duckProp.duckSpin *= 0.85;
      }
    }

    this.bellVx += (targetX - this.bellX) * 0.08;
    this.bellVy += (targetY - this.bellY) * 0.08;
    this.bellVx *= 0.84;
    this.bellVy *= 0.84;
    this.bellX += this.bellVx;
    this.bellY += this.bellVy;

    const targetScaleX = 1.0 - swimPulse * 0.045 * this.tentacleFlow;
    const targetScaleY = 1.0 + swimPulse * 0.045 * this.tentacleFlow;
    this.bellScaleX += (targetScaleX - this.bellScaleX) * 0.15;
    this.bellScaleY += (targetScaleY - this.bellScaleY) * 0.15;

    for (let i = 0; i < this.numNodes; i++) {
      const n = this.nodes[i];
      const restR = this._getDomeRestRadius(n.angle, swimPulse);
      n.vr += (restR - n.r) * 0.18;
      const prev = this.nodes[(i - 1 + this.numNodes) % this.numNodes];
      const next = this.nodes[(i + 1) % this.numNodes];
      n.vr += ((prev.r + next.r) * 0.5 - n.r) * 0.22;
      n.vr *= 0.82;
      n.r += n.vr;

      const cosA = Math.cos(n.angle + this.bellRotation);
      const sinA = Math.sin(n.angle + this.bellRotation);
      const yMod = sinA > 0 ? 0.72 : 1.02;
      n.x = this.bellX + cosA * n.r * this.bellScaleX;
      n.y = this.bellY + sinA * n.r * yMod * this.bellScaleY;
    }

    for (let t = 0; t < this.numTentacles; t++) {
      const tent = this.tentacles[t];
      tent.pts[0].x = this.bellX + tent.norm * (this.bellRadius * 0.66) * this.bellScaleX;
      tent.pts[0].y = this.bellY + (this.bellRadius * 0.48 - Math.abs(tent.norm) * 4) * this.bellScaleY;

      for (let s = 1; s < this.segments; s++) {
        const prev = tent.pts[s - 1];
        const cur = tent.pts[s];
        const ratio = s / (this.segments - 1);
        const waveSpeed = this.state === 'dj_headphones' ? 9.0 : (this.state === 'electro_shock' ? 22.0 : 3.4);
        const waveAmp = (tent.isFeeler ? 5.2 : 3.8) * ratio * this.tentacleFlow * (this.state === 'electro_shock' ? 2.1 : 1.0);
        const waveX = Math.sin(this.time * waveSpeed - s * 0.55 + t * 1.1) * waveAmp + tent.norm * ratio * 6 * (1 - swimPulse * 0.4);
        const gravityY = tent.segLen * (this.state === 'happy_spin' ? 0.75 : 1.0);

        let desiredX = prev.x + waveX * 0.38;
        let desiredY = prev.y + gravityY;

        if (tent.targetWeight > 0.05 && tent.targetX !== null) {
          const ikCurve = Math.pow(ratio, 1.35) * tent.targetWeight;
          const arcOffset = Math.sin(ratio * Math.PI) * tent.norm * 14 * tent.targetWeight;
          desiredX = desiredX * (1 - ikCurve) + (tent.targetX + arcOffset) * ikCurve;
          desiredY = desiredY * (1 - ikCurve) + tent.targetY * ikCurve;
        }

        cur.vx = (cur.vx + (desiredX - cur.x) * 0.28) * 0.72;
        cur.vy = (cur.vy + (desiredY - cur.y) * 0.28) * 0.72;
        cur.x += cur.vx;
        cur.y += cur.vy;

        const dx = cur.x - prev.x;
        const dy = cur.y - prev.y;
        const dist = Math.hypot(dx, dy) || 1;
        const maxLen = tent.segLen * (1 + tent.targetWeight * 0.55);
        if (dist > maxLen) {
          cur.x = prev.x + (dx / dist) * maxLen;
          cur.y = prev.y + (dy / dist) * maxLen;
        }
      }
    }

    let lookTargetX = 0;
    let lookTargetY = 0;
    this.eye.pupilScale = 1.0;

    if (this.state === 'cosmic_boba') {
      if (this.bobaProp.insidePearls.length > 0 && this.stateTimer < 7.0) {
        const p = this.bobaProp.insidePearls[this.bobaProp.insidePearls.length - 1];
        lookTargetX = (p.x - this.bellX) * 0.35;
        lookTargetY = (p.y - this.bellY) * 0.35;
        this.eye.pupilScale = 1.18;
      } else {
        lookTargetX = (this.bobaProp.cupX - this.bellX) * 0.22;
        lookTargetY = (this.bobaProp.cupY - this.bellY) * 0.22;
      }
    } else if (this.state === 'juggling_orbs') {
      let topOrb = this.juggleProp.orbs[0];
      for (const o of this.juggleProp.orbs) if (o.y < topOrb.y) topOrb = o;
      lookTargetX = (topOrb.x - this.bellX) * 0.24;
      lookTargetY = (topOrb.y - this.bellY) * 0.22;
      this.eye.pupilScale = 1.12;
    } else if (this.state === 'dj_headphones') {
      lookTargetX = Math.sin(this.djProp.beatPhase * 0.5) * 6;
      lookTargetY = 3 + Math.abs(Math.sin(this.djProp.beatPhase)) * 3;
    } else if (this.state === 'abducting_duck') {
      lookTargetX = (this.duckProp.x - this.bellX) * 0.2;
      lookTargetY = Math.min(11, (this.duckProp.y - this.bellY) * 0.18);
      this.eye.pupilScale = 1.18;
    } else if (this.state === 'electro_shock') {
      lookTargetX = (Math.random() - 0.5) * 8;
      lookTargetY = (Math.random() - 0.5) * 8;
      this.eye.pupilScale = 0.58;
    } else if (this.pointer.active) {
      lookTargetX = Math.max(-10, Math.min(10, (this.pointer.x - this.bellX) * 0.12));
      lookTargetY = Math.max(-8, Math.min(8, (this.pointer.y - this.bellY) * 0.12));
    } else {
      this.eye.idleLookTimer -= dt;
      if (this.eye.idleLookTimer <= 0) {
        this.eye.idleLookTimer = 1.6 + Math.random() * 2.4;
        this.eye.idleTargetX = (Math.random() - 0.5) * 14;
        this.eye.idleTargetY = (Math.random() - 0.5) * 9;
      }
      lookTargetX = this.eye.idleTargetX;
      lookTargetY = this.eye.idleTargetY;
    }

    this.eye.lookX += (lookTargetX - this.eye.lookX) * 0.16;
    this.eye.lookY += (lookTargetY - this.eye.lookY) * 0.16;

    const desiredEyeX = this.bellX + this.eye.lookX * 0.55;
    const desiredEyeY = this.bellY - 5 + this.eye.lookY * 0.55;
    this.eye.vx = (this.eye.vx + (desiredEyeX - this.eye.x) * 0.18) * 0.78;
    this.eye.vy = (this.eye.vy + (desiredEyeY - this.eye.y) * 0.18) * 0.78;
    this.eye.x += this.eye.vx;
    this.eye.y += this.eye.vy;

    this.eye.blinkTimer -= dt;
    if (this.eye.blinkTimer <= 0) {
      this.eye.blink = 1.0;
      this.eye.blinkTimer = 2.6 + Math.random() * 3.2;
    }
    if (this.eye.blink > 0) this.eye.blink = Math.max(0, this.eye.blink - dt * 7.5);

    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.life++;
      p.alpha = 1 - p.life / p.maxLife;
      if (p.life >= p.maxLife) this.particles.splice(i, 1);
    }
  }

  _traceBellPath() {
    const ctx = this.ctx;
    ctx.beginPath();
    const firstMidX = (this.nodes[this.numNodes - 1].x + this.nodes[0].x) * 0.5;
    const firstMidY = (this.nodes[this.numNodes - 1].y + this.nodes[0].y) * 0.5;
    ctx.moveTo(firstMidX, firstMidY);
    for (let i = 0; i < this.numNodes; i++) {
      const next = this.nodes[(i + 1) % this.numNodes];
      const midX = (this.nodes[i].x + next.x) * 0.5;
      const midY = (this.nodes[i].y + next.y) * 0.5;
      ctx.quadraticCurveTo(this.nodes[i].x, this.nodes[i].y, midX, midY);
    }
    ctx.closePath();
  }

  _drawTentacles(layerFilter) {
    const ctx = this.ctx;
    for (let t = 0; t < this.numTentacles; t++) {
      const tent = this.tentacles[t];
      if (tent.layer !== layerFilter) continue;

      ctx.save();
      ctx.beginPath();
      ctx.moveTo(tent.pts[0].x, tent.pts[0].y);
      for (let s = 1; s < this.segments - 1; s++) {
        const xc = (tent.pts[s].x + tent.pts[s + 1].x) * 0.5;
        const yc = (tent.pts[s].y + tent.pts[s + 1].y) * 0.5;
        ctx.quadraticCurveTo(tent.pts[s].x, tent.pts[s].y, xc, yc);
      }
      const tip = tent.pts[this.segments - 1];
      ctx.lineTo(tip.x, tip.y);

      const grad = ctx.createLinearGradient(tent.pts[0].x, tent.pts[0].y, tip.x, tip.y);
      grad.addColorStop(0, this.theme.tentacleBase);
      grad.addColorStop(1, this.theme.tentacleTip);

      ctx.strokeStyle = grad;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.lineWidth = tent.isFeeler ? 6.5 : 4.6;
      ctx.stroke();

      for (let s = 2; s < this.segments; s += 2) {
        const pt = tent.pts[s];
        const pulseGlow = 0.45 + 0.55 * Math.sin(this.time * 5 - s * 0.9 + t);
        ctx.fillStyle = this.theme.bioNode;
        ctx.globalAlpha = pulseGlow * (layerFilter === 'back' ? 0.55 : 0.9);
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, tent.isFeeler ? 2.1 : 1.5, 0, Math.PI * 2);
        ctx.fill();
      }

      if (tent.isFeeler) {
        ctx.globalAlpha = 0.95;
        ctx.fillStyle = this.theme.tentacleTip;
        ctx.shadowColor = this.theme.tentacleTip;
        ctx.shadowBlur = 8;
        ctx.beginPath();
        ctx.arc(tip.x, tip.y, 4.6, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
      }
      ctx.restore();
    }
  }

  _drawInternalEye() {
    const ctx = this.ctx;
    ctx.save();
    const ex = this.eye.x;
    const ey = this.eye.y;
    const r = this.eye.radius;

    ctx.fillStyle = this.theme.tint;
    ctx.beginPath();
    ctx.arc(ex, ey + 2, r + 3, 0, Math.PI * 2);
    ctx.fill();

    const scleraGrad = ctx.createRadialGradient(ex - 3, ey - 3, 2, ex, ey, r);
    scleraGrad.addColorStop(0, '#ffffff');
    scleraGrad.addColorStop(0.82, '#f8fafc');
    scleraGrad.addColorStop(1, '#cbd5e1');
    ctx.fillStyle = scleraGrad;
    ctx.beginPath();
    ctx.arc(ex, ey, r, 0, Math.PI * 2);
    ctx.fill();

    ctx.save();
    ctx.beginPath();
    ctx.arc(ex, ey, r, 0, Math.PI * 2);
    ctx.clip();

    const ix = ex + this.eye.lookX * 0.45;
    const iy = ey + this.eye.lookY * 0.45;
    const irisR = r * 0.64 * this.eye.pupilScale;

    const happyArc = (
      this.state === 'happy_spin' ||
      (this.state === 'dj_headphones' && this.stateTimer > 1.0 && this.stateTimer < 7.3) ||
      (this.state === 'cosmic_boba' && this.bobaProp.insidePearls.length >= 2 && this.stateTimer < 6.8)
    );

    if (happyArc) {
      ctx.strokeStyle = this.theme.irisOuter;
      ctx.lineWidth = 3.4;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.arc(ix, iy + 3, r * 0.46, Math.PI * 1.15, Math.PI * 1.85);
      ctx.stroke();
    } else {
      const irisGrad = ctx.createRadialGradient(ix, iy, irisR * 0.15, ix, iy, irisR);
      irisGrad.addColorStop(0, this.theme.irisInner);
      irisGrad.addColorStop(0.65, this.theme.rim);
      irisGrad.addColorStop(1, this.theme.irisOuter);
      ctx.fillStyle = irisGrad;
      ctx.beginPath();
      ctx.arc(ix, iy, irisR, 0, Math.PI * 2);
      ctx.fill();

      if (this.state === 'hypnotic') {
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        for (let a = 0; a < Math.PI * 5; a += 0.25) {
          const sr = (a / (Math.PI * 5)) * irisR * 0.9;
          const sx = ix + Math.cos(a - this.time * 8) * sr;
          const sy = iy + Math.sin(a - this.time * 8) * sr;
          if (a === 0) ctx.moveTo(sx, sy);
          else ctx.lineTo(sx, sy);
        }
        ctx.stroke();
      } else {
        ctx.fillStyle = '#0f172a';
        ctx.beginPath();
        ctx.arc(ix, iy, irisR * 0.48, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(ix - 3.8, iy - 3.8, 3.1, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(ix + 3.2, iy + 2.8, 1.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    const lidClose = this.state === 'sleepy_drift' ? Math.max(0.58, this.eye.blink) : this.eye.blink;
    if (lidClose > 0.02) {
      ctx.fillStyle = this.theme.edge;
      ctx.fillRect(ex - r - 2, ey - r - 2, (r + 2) * 2, (r * 2 + 4) * lidClose);
    }

    ctx.restore();
    ctx.restore();
  }

  render() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.w, this.h);

    const shadowScale = 1 - Math.max(-0.25, Math.min(0.25, (this.baseCy - this.bellY) / 90));
    ctx.save();
    const shGrad = ctx.createRadialGradient(this.bellX, this.h - 14, 2, this.bellX, this.h - 14, 44 * shadowScale);
    shGrad.addColorStop(0, this.theme.glow);
    shGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = shGrad;
    ctx.beginPath();
    ctx.ellipse(this.bellX, this.h - 14, 42 * shadowScale, 8 * shadowScale, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    if (this.duckProp.active) {
      ctx.save();
      if (this.duckProp.beamPower > 0.02) {
        const topY = this.bellY + 18;
        const botY = this.h - 10;
        const beamGrad = ctx.createLinearGradient(this.bellX, topY, this.bellX, botY);
        beamGrad.addColorStop(0, `rgba(103, 232, 249, ${0.42 * this.duckProp.beamPower})`);
        beamGrad.addColorStop(1, `rgba(217, 70, 239, ${0.06 * this.duckProp.beamPower})`);
        ctx.fillStyle = beamGrad;
        ctx.beginPath();
        ctx.moveTo(this.bellX - 18, topY);
        ctx.lineTo(this.bellX + 18, topY);
        ctx.lineTo(this.bellX + 44, botY);
        ctx.lineTo(this.bellX - 44, botY);
        ctx.closePath();
        ctx.fill();
      }
      ctx.translate(this.duckProp.x, this.duckProp.y);
      ctx.rotate(this.duckProp.duckSpin);
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

    this._drawTentacles('back');

    ctx.save();
    this._traceBellPath();
    const bellGrad = ctx.createRadialGradient(this.bellX - 14, this.bellY - 18, 6, this.bellX, this.bellY, this.bellRadius * 1.18);
    bellGrad.addColorStop(0, this.theme.core);
    bellGrad.addColorStop(0.58, this.theme.mid);
    bellGrad.addColorStop(1, this.theme.edge);
    ctx.shadowColor = this.theme.glow;
    ctx.shadowBlur = 18;
    ctx.fillStyle = bellGrad;
    ctx.fill();
    ctx.shadowBlur = 0;

    ctx.save();
    this._traceBellPath();
    ctx.clip();

    for (const b of this.bubbles) {
      const bx = this.bellX + Math.cos(b.angle + this.time * b.speed) * b.dist * this.bellScaleX;
      const by = this.bellY - 4 + Math.sin(b.angle * 1.3 + this.time * b.speed) * (b.dist * 0.65) * this.bellScaleY;
      ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
      ctx.beginPath();
      ctx.arc(bx, by, b.r, 0, Math.PI * 2);
      ctx.fill();
    }

    if (this.bobaProp.active) {
      for (const ip of this.bobaProp.insidePearls) {
        ctx.save();
        ctx.globalAlpha = ip.alpha;
        ctx.fillStyle = ip.color;
        ctx.beginPath();
        ctx.arc(ip.x, ip.y, 4.4, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    this._drawInternalEye();
    ctx.restore();

    this._traceBellPath();
    ctx.strokeStyle = this.theme.rim;
    ctx.lineWidth = 2.0;
    ctx.stroke();

    ctx.fillStyle = 'rgba(255, 255, 255, 0.48)';
    ctx.beginPath();
    ctx.ellipse(this.bellX - 17 * this.bellScaleX, this.bellY - 22 * this.bellScaleY, 13, 5.5, -0.42, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    this._drawTentacles('front');

    if (this.bobaProp.active) {
      ctx.save();
      const cx = this.bobaProp.cupX;
      const cy = this.bobaProp.cupY;
      ctx.strokeStyle = '#f472b6';
      ctx.lineWidth = 4.2;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(cx - 2, cy + 6);
      ctx.lineTo(cx - 8, cy - 22);
      ctx.lineTo(this.bellX + 20, this.bellY + 2);
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

      const liqH = 24 * this.bobaProp.liquidLevel;
      ctx.fillStyle = 'rgba(217, 70, 239, 0.65)';
      ctx.fillRect(cx - 9, cy + 15 - liqH, 18, liqH);
      ctx.restore();
    }

    if (this.juggleProp.active) {
      ctx.save();
      for (const orb of this.juggleProp.orbs) {
        ctx.shadowColor = orb.glow;
        ctx.shadowBlur = 12;
        ctx.fillStyle = orb.color;
        ctx.beginPath();
        ctx.arc(orb.x, orb.y, 7.5, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }

    if (this.djProp.active) {
      ctx.save();
      const hy = this.djProp.headphoneY;
      const hx = this.bellX;
      const rx = this.bellRadius * 0.98 * this.bellScaleX;
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 6.5;
      ctx.beginPath();
      ctx.arc(hx, hy + 4, rx + 2, Math.PI * 1.05, Math.PI * 1.95);
      ctx.stroke();
      for (const dir of [-1, 1]) {
        const ex = hx + dir * (rx + 1);
        ctx.fillStyle = '#0f172a';
        ctx.strokeStyle = this.theme.tentacleTip;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(ex - 6, hy - 7, 12, 26, 6);
        ctx.fill();
        ctx.stroke();
      }
      ctx.restore();
    }

    for (const p of this.particles) {
      ctx.save();
      ctx.globalAlpha = Math.max(0, p.alpha);
      ctx.fillStyle = p.color;
      ctx.font = `bold ${Math.round(13 * p.scale)}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText(p.text, p.x, p.y);
      ctx.restore();
    }
  }

  start() {
    if (this._rafId) return;
    let last = performance.now();
    const tick = now => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      this.update(dt);
      this.render();
      this._rafId = requestAnimationFrame(tick);
    };
    this._rafId = requestAnimationFrame(tick);
  }

  stop() {
    if (this._rafId) {
      cancelAnimationFrame(this._rafId);
      this._rafId = null;
    }
  }
}

export class JellyCompanionElement extends HTMLElement {
  static get observedAttributes() {
    return ['state', 'theme', 'size', 'auto-random'];
  }

  connectedCallback() {
    const size = parseInt(this.getAttribute('size') || '260', 10);
    const shadow = this.attachShadow({ mode: 'open' });
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    canvas.style.cursor = 'pointer';
    shadow.appendChild(canvas);

    this.mascot = new JellyCompanionMascot(canvas, {
      theme: this.getAttribute('theme') || 'astral',
      state: this.getAttribute('state') || 'idle',
      autoRandom: this.hasAttribute('auto-random')
    });
  }

  attributeChangedCallback(name, _, newVal) {
    if (!this.mascot) return;
    if (name === 'state' && newVal) this.mascot.setState(newVal);
    if (name === 'theme' && newVal) this.mascot.setTheme(newVal);
  }

  disconnectedCallback() {
    if (this.mascot) this.mascot.stop();
  }
}

if (typeof window !== 'undefined' && !customElements.get('jelly-companion')) {
  customElements.define('jelly-companion', JellyCompanionElement);
}
