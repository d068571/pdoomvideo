// alps.js: "Clawd goes hiking", a 27 s spin-off on the P(doom) engine. Six shots, one Swiss cliché each:
// the postcard, the punctual train, the sprinting grandma, the cowbells, the pocket knife and the summit coffee.
(() => {
  const RED = '#D8263A', RED_DK = '#961B2C', GRASS = '#7DB356', GRASS_DK = '#4E8A3E', ROCK = '#8C8FA8', ROCK_DK = '#5D6282';
  const WOODC = '#9A5B34', GOLDB = '#E9B53C', FELT = '#5C7A45', SKIN_G = '#F2C4A0';

  // ---------- scenery ----------
  function sky(top = '#8EC3E6', low = '#D8EEF4') {
    paint(rectPts(-600, -600, W + 1200, H + 1200), { wash: top, washOp: 255, ink: null });
    paint(ellPts(960, 900, 1500, 520, 24), { fill: low, fillOp: 150, bleed: .25, tex: .3, border: .2, ink: null });
  }
  function sun(x, y, r, t) {
    paint(ellPts(x, y, r * 2.1, r * 2.1, 26), { fill: PAL.ochre, fillOp: 50, bleed: .3, tex: .2, ink: null });
    for (let i = 0; i < 10; i++) { const a = i / 10 * TAU + t * .3; inkLine([[x + Math.cos(a) * r * 1.25, y + Math.sin(a) * r * 1.25], [x + Math.cos(a) * r * 1.65, y + Math.sin(a) * r * 1.65]], .8, PAL.ochre, 'ink', 0); }
    paint(ellPts(x, y, r, r, 22, 2), { wash: '#F6CB57', fill: PAL.ochre, fillOp: 90, ink: PAL.ink, sw: .8 });
  }
  function cloud(x, y, s, op = 230) {
    const puffs = [[-1.3, .2, 1], [-.4, -.35, 1.25], [.6, -.1, 1.05], [1.4, .25, .8], [0, .35, 1.1]];
    for (const [px, py, r] of puffs) paint(ellPts(x + px * s, y + py * s, r * s * .75, r * s * .6, 16, s * .03), { wash: PAL.cream, washOp: op, ink: null });
    inkLine([[x - 1.9 * s, y + .55 * s], [x + 1.9 * s, y + .55 * s]], .5, '#B9C8D8', 'inkfine', 0);
  }
  // A jagged snow-capped peak. Its shape comes from hash(seed), so it holds still while the ink boils.
  function peak(cx, top, base, hw, col, seed, o = {}) {
    const lean = o.lean || 0, rw = o.rw || 1, sn = o.snow ?? .33, A = [cx + lean, top], L = [cx - hw, base], R = [cx + hw * rw, base];
    const side = (P, Q, k0) => { const r = []; for (let i = 1; i < 4; i++) { const k = i / 4; r.push([lerp(P[0], Q[0], k) + (hash(seed + i + k0) - .5) * hw * .22, lerp(P[1], Q[1], k) + (hash(seed + i * 3 + k0) - .5) * 30]); } return r; };
    const pts = [L, ...side(L, A, 0), A, ...side(A, R, 10), R];
    paint(pts, { wash: col, washOp: 255, fill: mixCol(col, PAL.ink, .35), fillOp: 60, bleed: .08, tex: .6, border: .5, ink: o.ink === undefined ? PAL.ink : o.ink, sw: o.sw ?? .9 });
    paint([A, ...side(A, R, 10), R, [cx + lean * .4 + hw * .1, base]], { fill: PAL.ink, fillOp: 45, bleed: .05, tex: .5, border: .3, ink: null });
    const P1 = [lerp(A[0], L[0], sn), lerp(A[1], L[1], sn)], P2 = [lerp(A[0], R[0], sn), lerp(A[1], R[1], sn)], snow = [A, P2];
    for (let i = 1; i < 6; i++) { const k = i / 6; snow.push([lerp(P2[0], P1[0], k), lerp(P2[1], P1[1], k) + (i % 2 ? 26 : -16) * (hw / 300)]); }
    snow.push(P1);
    paint(snow, { wash: '#F7F4EE', washOp: 255, fill: '#C9D6E8', fillOp: 70, tex: .4, ink: o.ink === undefined ? PAL.ink : o.ink, sw: (o.sw ?? .9) * .7 });
  }
  // Big shapes far off-canvas get dropped under a zoomed camera, so the hill only spans what the camera can see.
  function hill(y0, amp, col, seed, o = {}) {
    const z = CAM ? CAM.zoom : 1, xa = CAM ? CAM.cx - W / 2 / z - 150 : -500, xb = CAM ? CAM.cx + W / 2 / z + 150 : W + 500, yb = CAM ? CAM.cy + H / 2 / z + 150 : 1400;
    const pts = [[xa, yb]], hy = x => { const k = (x + 500) / (W + 1000) * 14; return y0 - Math.sin(k * .7 + seed) * amp - hash(seed + Math.round(k)) * amp * .4; };
    for (let i = 0; i <= 14; i++) { const x = lerp(xa, xb, i / 14); pts.push([x, hy(x)]); }
    pts.push([xb, yb]);
    paint(pts, { wash: col, washOp: 255, fill: mixCol(col, PAL.ink, .3), fillOp: 55, bleed: .1, tex: .7, border: .5, ink: o.ink === undefined ? PAL.ink : o.ink, sw: .9, curv: .5 });
  }
  function flowers(x0, x1, y0, y1, n, seed) {
    for (let i = 0; i < n; i++) {
      const x = lerp(x0, x1, hash(seed + i)), y = lerp(y0, y1, hash(seed + i * 7)), c = [PAL.cream, PAL.ochre, PAL.rose, '#B98AD8'][i % 4];
      paint(ellPts(x, y, 6, 6, 8), { wash: c, ink: null });
    }
  }
  function pine(x, y, s) {
    paint(rectPts(x - .15 * s, y - .4 * s, .3 * s, .45 * s), { wash: WOODC, ink: null });
    for (let i = 0; i < 3; i++) { const yy = y - .3 * s - i * .45 * s, w = (.62 - i * .15) * s; paint([[x - w, yy], [x, yy - .75 * s], [x + w, yy]], { wash: '#2F6B4A', fill: '#1E4A38', fillOp: 70, ink: PAL.ink, sw: .6 }); }
  }
  function flag(x, y, s, t, ph = 0) {
    inkLine([[x, y], [x, y - 3 * s]], 1.1, PAL.ink, 'ink', 0);
    const top = [], bot = [], wv = k => Math.sin(k * 3 - t * 7 + ph) * .12 * s * k;
    for (let i = 0; i <= 6; i++) { const k = i / 6; top.push([x + k * 1.5 * s, y - 3 * s + wv(k)]); bot.push([x + k * 1.5 * s, y - 1.5 * s + wv(k)]); }
    paint([...top, ...bot.reverse()], { wash: RED, washOp: 255, ink: PAL.ink, sw: .7 });
    const cx = x + .75 * s, cy = y - 2.25 * s + wv(.5), a = .18 * s, b = .5 * s;
    paint(rectPts(cx - a, cy - b, 2 * a, 2 * b), { wash: '#FFFDF6', ink: null });
    paint(rectPts(cx - b, cy - a, 2 * b, 2 * a), { wash: '#FFFDF6', ink: null });
  }
  function chalet(x, y, s, t) {
    paint(rectPts(x - 2 * s, y - 2.2 * s, 4 * s, 2.2 * s, 2), { wash: '#B8773F', fill: '#7C4A2C', fillOp: 80, tex: .7, ink: PAL.ink, sw: .9 });
    for (let i = 1; i < 5; i++) inkLine([[x - 2 * s, y - i * .45 * s], [x + 2 * s, y - i * .45 * s]], .4, '#7C4A2C', 'inkfine', 0);
    paint([[x - 2.8 * s, y - 2.1 * s], [x, y - 3.9 * s], [x + 2.8 * s, y - 2.1 * s], [x + 2.6 * s, y - 1.9 * s], [x, y - 3.5 * s], [x - 2.6 * s, y - 1.9 * s]], { wash: '#6B3A26', ink: PAL.ink, sw: .9 });
    for (const wx of [-1.2, .4]) {
      paint(rectPts(x + wx * s, y - 1.6 * s, .8 * s, .7 * s), { wash: '#FBE7B5', ink: PAL.ink, sw: .6 });
      for (let k = 0; k < 3; k++) paint(ellPts(x + (wx + .15 + k * .25) * s, y - .85 * s, .13 * s, .11 * s, 8), { wash: '#E2334D', ink: null });
    }
    flag(x + 2.2 * s, y - 2.4 * s, .55 * s, t);
  }

  // ---------- Clawd the hiker: alpine felt hat with a feather, rucksack with a bedroll ----------
  function alpHat(u, sw) {
    paint(ellPts(0, -8.05 * u, 4.4 * u, .75 * u, 20), { wash: '#4A6636', ink: PAL.ink, sw: sw * .7 });
    paint([[-2.7 * u, -8.2 * u], [-2.1 * u, -10.9 * u], [-.2 * u, -10.4 * u], [2.1 * u, -10.9 * u], [2.7 * u, -8.2 * u]], { wash: FELT, fill: '#3E5A2E', fillOp: 70, tex: .6, ink: PAL.ink, sw: sw * .8, curv: .35 });
    paint(rectPts(-2.65 * u, -9.0 * u, 5.3 * u, .65 * u), { wash: RED, ink: null });
    paint(starPts(-1.3 * u, -8.68 * u, .5 * u, .4, 5), { wash: PAL.cream, ink: PAL.ink, sw: sw * .35 });
    push(); translate(2.3 * u, -9.4 * u); rotate(.5);
    paint(ellPts(0, -1.4 * u, .45 * u, 1.7 * u, 14), { wash: '#E9E2CF', fill: PAL.teal, fillOp: 80, ink: PAL.ink, sw: sw * .5 });
    inkLine([[0, .2 * u], [0, -3 * u]], sw * .5, PAL.ink, 'inkfine', 0);
    pop();
  }
  function pack(x, y, u, dir) {
    const bx = x - dir * 5.5 * u, by = y - 7.4 * u;
    paint(rrPts(bx - 1.7 * u, by, 3.4 * u, 4.8 * u, .9 * u), { wash: RED, fill: RED_DK, fillOp: 80, tex: .6, ink: PAL.ink, sw: clamp(u / 15, .45, 2) });
    paint(rrPts(bx - 2 * u, by - 1.2 * u, 4 * u, 1.3 * u, .6 * u), { wash: '#5F7FA8', ink: PAL.ink, sw: clamp(u / 18, .4, 1.6) });
    paint(rrPts(bx - 1.1 * u, by + 2.4 * u, 2.2 * u, 1.5 * u, .4 * u), { wash: RED_DK, ink: PAL.ink, sw: clamp(u / 22, .4, 1.4) });
  }
  // hiker(x, y, u, o): clawd() in hiking kit. o as clawd(); o.dx (body units) shifts, o.flip faces left.
  function hiker(x, y, u, o = {}) {
    x += (o.dx || 0) * u;
    pack(x, y + (o.dy || 0) * u, u, o.flip ? -1 : 1);
    const extra = o.draw;
    clawd(x, y, u, { ...o, draw: (uu, sw) => { alpHat(uu, sw); if (extra) extra(uu, sw); } });
  }
  // where Clawd's right-arm tip is in world space (for props held in the air)
  const armTip = (x, y, u, dy, a, side = 1) => [x + side * (4.9 * u + Math.cos(a) * 2.2 * u), y + dy * u - 4.5 * u - Math.sin(a) * 2.2 * u];

  // ================= 1. The postcard (0 – 4.3) =================
  function postcard(t, lt) {
    const z = lerp(1, 1.08, ease(lt / 4.3));
    camBegin(960 + lt * 12, 540, z);
    sky();
    sun(1600, 190, 70, t);
    cloud(420, 200, 70); cloud(1250, 140, 50);
    peak(300, 330, 760, 420, ROCK, 1, { snow: .4 });
    peak(1500, 360, 760, 460, ROCK, 5, { snow: .38 });
    peak(930, 110, 780, 330, '#9A8CA8', 9, { lean: 70, rw: 1.5, snow: .3, sw: 1.1 });     // the one on the chocolate box
    cloud(700, 520, 60, 200);
    hill(700, 40, '#9CC869', 2);
    chalet(1450, 730, 70, t);
    for (const [px, py, s] of [[160, 740, 90], [260, 760, 70], [1760, 760, 80], [1860, 740, 100]]) pine(px, py, s);
    hill(860, 30, GRASS, 4);
    flowers(-100, 2000, 890, 1060, 40, 3);
    // Clawd marches in and throws its arms up at the view
    const x = kf(lt, [[0, -150], [2.2, 760]], x => x), arrived = lt > 2.2;
    const m = move(arrived ? 'roof' : 'walk', t);
    hiker(x, 930, 24, { ...m, dx: 0, ...mood(t, [[0, 'normal'], [2.25, 'spark', 'spark']]), mouth: arrived ? 'O' : 'smile' });
    camEnd();
    // title card
    letter('CLAWD GOES HIKING', 960, 260 - 10 * wob(t, .5), 118, PAL.cream, { pop: (lt - .4) * 2.5, rot: -.04, stroke: RED_DK });
    letter('a small adventure in the Swiss Alps', 960, 370, 48, PAL.ink, { pop: (lt - 1) * 2.5, ink: false, rot: -.02 });
  }

  // ================= 2. The train leaves at 08:00:00 sharp (4.3 – 8.6) =================
  // Swiss station clock: the red second hand sweeps round in 58.5 s, waits at 12, then the minute jumps.
  function stationClock(x, y, R, sec, min) {
    inkLine([[x, -40], [x, y - R]], 2, PAL.ink, 'ink', 0);
    paint(ellPts(x, y, R * 1.08, R * 1.08, 36), { wash: '#3B4050', ink: PAL.ink, sw: 1.2 });
    paint(ellPts(x, y, R, R, 36), { wash: '#FFFDF6', ink: null });
    for (let i = 0; i < 60; i++) {
      const a = i / 60 * TAU, big = i % 5 === 0, r0 = big ? R * .72 : R * .86;
      inkLine([[x + Math.sin(a) * r0, y - Math.cos(a) * r0], [x + Math.sin(a) * R * .95, y - Math.cos(a) * R * .95]], big ? 2.4 : .7, PAL.ink, big ? 'marker' : 'inkfine', 0);
    }
    const hand = (a, l0, l1, w) => { const c = Math.cos(a), s = Math.sin(a), px = -c * w, py = -s * w; paint([[x - s * l0 + px, y + c * l0 + py], [x + s * l1 + px, y - c * l1 + py], [x + s * l1 - px, y - c * l1 - py], [x - s * l0 - px, y + c * l0 - py]], { wash: PAL.ink, ink: null }); };
    hand((8 + min / 60) / 12 * TAU, R * .2, R * .6, R * .05);
    hand(min / 60 * TAU, R * .2, R * .88, R * .035);
    const sa = Math.min(1, sec / 58.5) * TAU, sx = Math.sin(sa), sy = -Math.cos(sa);
    inkLine([[x - sx * R * .3, y - sy * R * .3], [x + sx * R * .62, y + sy * R * .62]], 1.1, RED, 'marker', 0);
    paint(ellPts(x + sx * R * .62, y + sy * R * .62, R * .1, R * .1, 14), { wash: RED, ink: null });
    paint(ellPts(x, y, R * .04, R * .04, 8), { wash: RED, ink: null });
  }
  function trainCar(x, y, len, i, t, front) {
    const h = 300;
    paint(rrPts(x, y, len, h, front ? 60 : 24, 2), { wash: RED, fill: RED_DK, fillOp: 70, tex: .6, border: .5, ink: PAL.ink, sw: 1.2 });
    paint(rectPts(x + 10, y + 220, len - 20, 22), { wash: '#FFF5E2', ink: null });
    for (let w = 0; w < 4; w++) {
      const wx = x + 40 + w * (len - 60) / 4;
      paint(rrPts(wx, y + 50, (len - 60) / 4 - 26, 110, 16), { wash: '#BFE0EE', fill: PAL.sky, fillOp: 80, ink: PAL.ink, sw: .8 });
      if ((i * 4 + w) % 3 !== 1) clawd(wx + ((len - 60) / 4 - 26) / 2, y + 160, 8, { noShadow: true, eyes: 'happy', aR: 1.2 + .4 * wob(t, 2, w), seed: w, hat: w % 2 ? 'fedora' : null, noLegs: true });
    }
    paint(rectPts(x + 18, y + h - 20, len - 36, 34), { wash: '#3B4050', ink: null });
    for (const bx of [x + 90, x + len - 90]) for (const d of [-40, 40]) paint(ellPts(bx + d, y + h + 16, 26, 26, 14), { wash: '#2E3140', ink: PAL.ink, sw: .7 });
    if (front) {
      paint(rrPts(x + len - 110, y + 40, 90, 120, 30), { wash: '#BFE0EE', ink: PAL.ink, sw: .9 });
      paint(ellPts(x + len - 40, y + 250, 16, 12, 10), { wash: '#FFF2B0', ink: PAL.ink, sw: .6 });
    }
  }
  function station(t, lt) {
    const sec = 57.6 + lt, min = lt >= 2.4 ? 60 : 59;        // 07:59:57.6 → hand waits at 12 from lt .9 → departs lt 2.4
    const go = Math.max(0, lt - 2.4), tx = 320 + 1500 * go * go;
    const [sx, sy] = shakeXY(t, lt > 2.4 && lt < 2.7 ? 5 : 0);
    camBegin(960 + sx + lt * 10, 540 + sy, 1.02);
    sky('#9CCDE8', '#E4F2F4');
    peak(450, 180, 520, 380, ROCK, 11, { snow: .42 });
    peak(1350, 140, 520, 420, ROCK, 17, { snow: .4 });
    paint(rectPts(-300, 480, W + 600, 300), { wash: '#A9C98A', fill: GRASS_DK, fillOp: 50, tex: .6, ink: null });
    inkLine([[-300, 760], [W + 300, 760]], 1.2, '#5D6282', 'ink', 0);
    for (let c = 0; c < 3; c++) trainCar(tx + c * 640, 420, 620, c, t, c === 2);
    // platform
    paint(rectPts(-300, 790, W + 600, 400), { wash: '#B9B4AE', fill: '#8C8782', fillOp: 70, tex: .7, border: .4, ink: PAL.ink, sw: 1.2 });
    inkLine([[-300, 818], [W + 300, 818]], 2.4, '#F2C94C', 'marker', 0);
    stationClock(250, 250, 130, sec, min);
    // Clawd sprints in, a second too late
    const cx = kf(lt, [[1.6, -250], [3.05, 780]], easeOut), arrived = lt > 3.05;
    const m = move(arrived ? 'idle' : 'run', t);
    hiker(cx, 930, 22, { ...m, dx: 0, rot: arrived ? -.05 * Math.exp(-(lt - 3.05) * 6) : m.rot,
      ...mood(t, [[4.3, 'narrow', 'sweat'], [4.3 + 3.1, 'scared', '!'], [4.3 + 3.7, 'closed', 'sweat']]), mouth: arrived ? 'wobble' : 'o', aL: arrived ? 1.3 : m.aL, aR: arrived ? 1.2 : m.aR });
    camEnd();
    sfx('PSSHT', 1300, 380, 80, PAL.cream, lt - 2.2, { rot: .08 });
    sfx('ZOOOM!', 1500, 520, 130, PAL.ochre, lt - 2.7, { life: 1.3 });
    const hhmmss = lt < 2.4 ? '07:59:' + Math.min(59, Math.floor(sec)) : '08:00:0' + Math.floor(lt - 2.4);
    letter(hhmmss, 250, 440, 46, lt < 2.4 ? PAL.cream : PAL.ochre, { ink: true });
  }

  // ================= 3. The grandma overtakes (8.6 – 13.0) =================
  function granny(x, y, s, t, run) {
    researcher(x, y, s, {
      coat: '#C8324A', pants: '#4E6B3A', shirt: PAL.cream, run, rot: .18, dy: -Math.abs(Math.sin(run * TAU)) * .8,
      aL: .2 + .5 * Math.sin(run * TAU), aR: .2 - .5 * Math.sin(run * TAU), eyes: 'closed', mouth: 'grin', blush: true,
      draw: (s, sw) => {
        // grey perm over the hair, and a bun
        paint(ellPts(0, -12.1 * s, 2.6 * s, 1.35 * s, 20), { wash: '#D9D6DF', fill: '#A9A6B8', fillOp: 70, tex: .6, ink: PAL.ink, sw: sw * .6 });
        paint(ellPts(0, -13.6 * s, 1.1 * s, .9 * s, 14), { wash: '#D9D6DF', ink: PAL.ink, sw: sw * .6 });
      },
      handL: (s, sw) => inkLine([[0, 0], [-.4 * s, 6.5 * s]], sw * 1.1, '#5D6282', 'ink', 0),
      handR: (s, sw) => inkLine([[0, 0], [.4 * s, 6.5 * s]], sw * 1.1, '#5D6282', 'ink', 0)
    });
  }
  function signpost(x, y, t) {
    inkLine([[x, y], [x, y - 330]], 3, '#8B8F99', 'marker', 0);
    const arrow = (yy, txt, time, rot) => {
      push(); translate(x, yy); rotate(rot);
      paint([[-20, -38], [300, -38], [345, 0], [300, 38], [-20, 38]], { wash: '#F4CF2E', fill: '#E0A92A', fillOp: 70, tex: .5, ink: PAL.ink, sw: 1 });
      pop();
      letter(txt, x + 110, yy - 2 + rot * 140, 34, PAL.ink, { ink: false, rot, font: '800 30px "Shantell Sans"' });
      letter(time, x + 250, yy - 2 + rot * 250, 34, PAL.ink, { ink: false, rot, font: '800 30px "Shantell Sans"' });
    };
    arrow(y - 300, 'Gipfel', '1 h 30', -.12);
    arrow(y - 210, 'Hütte', '45 min', -.12);
    paint(rectPts(x - 26, y - 360, 52, 30), { wash: '#FFFDF6', ink: PAL.ink, sw: .6 });
    paint(rectPts(x - 26, y - 360, 17, 30), { wash: '#C8324A', ink: null });
  }
  const slopeY = x => 960 - .26 * x;
  function trail(t, lt) {
    const [sx, sy] = shakeXY(t, Math.abs(lt - 1.95) < .2 ? 6 : 0);
    camBegin(960 + sx, 520 + sy, 1.0);
    sky('#86BEE3', '#DDF0F2');
    cloud(1500, 150, 60); cloud(300, 120, 40);
    peak(1600, -40, 560, 520, ROCK, 21, { snow: .45 });
    peak(500, 160, 620, 400, '#9A9CB6', 23, { snow: .35 });
    // slope
    const pts = [[-300, slopeY(-300)]];
    for (let i = 1; i < 12; i++) { const x = -300 + i * 230; pts.push([x, slopeY(x) - 12 * Math.sin(i * 1.3)]); }
    pts.push([2400, slopeY(2400)], [2400, 1400], [-300, 1400]);
    paint(pts, { wash: GRASS, washOp: 255, fill: GRASS_DK, fillOp: 60, bleed: .1, tex: .8, border: .5, ink: PAL.ink, sw: 1.1 });
    const path = []; for (let i = 0; i <= 8; i++) { const x = -300 + i * 330; path.push([x, slopeY(x) + 40]); }
    inkLine(path, 3, '#C9A876', 'dry', .4);
    for (const [px, s] of [[150, 110], [1700, 130], [1850, 90]]) pine(px, slopeY(px) + 30, s);
    flowers(-200, 2100, 0, 0, 0, 0);
    signpost(1300, slopeY(1300) + 20, t);
    // Clawd, slowly, sweating
    const x = 760 + lt * 30, passK = seg(lt, 1.85, 2.3);
    hiker(x, slopeY(x) + 20, 21, { walk: lt * .7, dy: -Math.abs(Math.sin(lt * 2.2)) * .3, rot: -.2 + passK * .25 * Math.exp(-(lt - 2.3) * 2), aL: -.3, aR: -.2,
      ...mood(t, [[8.6, 'narrow', 'sweat'], [8.6 + 1.95, 'swirl', '!?'], [8.6 + 3.4, 'closed', 'sweat']]), mouth: lt < 1.95 ? 'wobble' : 'O' });
    // Grandma: whooshes up the path past Clawd
    const gx = kf(lt, [[.8, -250], [3.2, 2300]], x => x);
    if (lt > .7 && lt < 3.3) {
      for (let k = 1; k < 5; k++) inkLine([[gx - 60 - k * 70, slopeY(gx) - 60 - k * 40 + k * 18], [gx - 150 - k * 110, slopeY(gx - 150 - k * 110) - 60 + k * 18]], .8, PAL.cream, 'ink', 0);
      paint(ellPts(gx - 90, slopeY(gx - 90) + 10, 70, 30, 14), { fill: '#C9A876', fillOp: 120, bleed: .2, ink: null });
      granny(gx, slopeY(gx) + 20, 13, t, lt * 3.2);
    }
    camEnd();
    sfx('Grüezi!', gx + 40, slopeY(gx) - 270, 70, PAL.cream, lt - 1.6, { rot: -.15, life: 1.2 });
    sfx('ZOOM', 700, 330, 90, PAL.ochre, lt - 2.0, { rot: -.2, life: 1 });
  }

  // ================= 4. The cowbells (13.0 – 17.4) =================
  function cowbell(x, y, s, swing, ring) {
    push(); translate(x, y); rotate(swing);
    inkLine([[-1.2 * s, -1.2 * s], [0, -.2 * s], [1.2 * s, -1.2 * s]], 3 * s / 40, '#6B3A26', 'marker', .4);
    paint([[-.55 * s, 0], [.55 * s, 0], [.95 * s, 1.5 * s], [-.95 * s, 1.5 * s]], { wash: GOLDB, fill: '#B98322', fillOp: 90, tex: .5, ink: PAL.ink, sw: clamp(s / 40, .5, 1.6), curv: .2 });
    paint(ellPts(0, 1.5 * s, .95 * s, .2 * s, 14), { wash: '#8A5E19', ink: PAL.ink, sw: clamp(s / 50, .4, 1.2) });
    paint(ellPts(-.3 * s, .5 * s, .12 * s, .4 * s, 10), { wash: '#FFF2B0', washOp: 170, ink: null });
    pop();
    if (ring > .05) for (let k = 0; k < 3; k++) {
      const r = s * (1.4 + k * .5 + ring * .6), a0 = -.5, a1 = .5, arc = [];
      for (let i = 0; i <= 6; i++) { const a = lerp(a0, a1, i / 6); arc.push([x + Math.cos(a) * r, y + s + Math.sin(a) * r]); }
      inkLine(arc, 1.2 * ring, PAL.ink, 'ink', .5);
      inkLine(arc.map(([px, py]) => [2 * x - px, py]), 1.2 * ring, PAL.ink, 'ink', .5);
    }
  }
  function cow(x, y, s, t, o = {}) {
    const f = o.flip ? -1 : 1, nod = o.nod || 0, sw = clamp(s / 14, .5, 1.6);
    push(); translate(x, y); scale(f, 1);
    for (const lx of [-3, -1.6, 1.6, 3]) paint(rectPts(lx * s - .45 * s, -3 * s, .9 * s, 3 * s), { wash: '#E9DCC8', ink: PAL.ink, sw: sw * .7 });
    inkLine([[3.9 * s, -5.8 * s], [4.6 * s, -3.8 * s + wob(t, 1.3) * .3 * s], [4.4 * s, -2.8 * s]], sw, PAL.ink, 'ink', .5);
    paint(rrPts(-4 * s, -7.4 * s, 8 * s, 4.6 * s, 2 * s), { wash: '#F4EBDD', fill: '#D8C9B3', fillOp: 60, tex: .6, ink: PAL.ink, sw });
    for (const [px, py, r] of [[-1.5, -6.4, 1.2], [1.8, -5.2, 1.4], [.2, -4, .8]]) paint(ellPts(px * s, py * s, r * s, r * .8 * s, 14, s * .08), { wash: '#A04E2A', ink: null });
    // head
    push(); translate(-4.2 * s, -6.8 * s); rotate(-.15 + nod * .3);
    for (const hx of [-1, 1]) inkLine([[hx * .9 * s, -2.1 * s], [hx * 1.6 * s, -2.9 * s], [hx * 1.4 * s, -3.3 * s]], sw * 1.4, '#F0E6CC', 'marker', .6);
    for (const hx of [-1, 1]) paint(ellPts(hx * 1.9 * s, -1.7 * s, .8 * s, .4 * s, 12), { wash: '#A04E2A', ink: PAL.ink, sw: sw * .6 });
    paint(rrPts(-1.4 * s, -2.4 * s, 2.8 * s, 3.4 * s, 1.2 * s), { wash: '#A04E2A', fill: '#7A3A20', fillOp: 60, tex: .5, ink: PAL.ink, sw });
    paint([[-.5 * s, -2.4 * s], [.5 * s, -2.4 * s], [.3 * s, -.2 * s], [-.3 * s, -.2 * s]], { wash: '#F4EBDD', ink: null });
    paint(ellPts(0, .6 * s, 1.35 * s, .8 * s, 16), { wash: '#F2A7A2', ink: PAL.ink, sw: sw * .8 });
    for (const nx of [-.5, .5]) paint(ellPts(nx * s, .6 * s, .16 * s, .22 * s, 8), { wash: '#6A2A35', ink: null });
    const e = o.eyes || 'dot';
    for (const ex of [-.75, .75]) {
      if (e === 'closed') inkLine([[ex * s - .3 * s, -1.2 * s], [ex * s, -1.0 * s], [ex * s + .3 * s, -1.2 * s]], sw, PAL.ink, 'ink', .4);
      else paint(ellPts(ex * s, -1.2 * s, .25 * s, .3 * s, 10), { wash: PAL.ink, ink: null });
    }
    pop();
    pop();
    cowbell(x - f * 4.2 * s, y - 4.6 * s + nod * .5 * s, s * (o.bell || 1), (o.swing || 0) * f, o.ring || 0);
  }
  function cows(t, lt) {
    // each cow nods on its beat and its bell rings; the last one is enormous
    const bp = bpOf(t), bi = Math.floor(bp), bf = bp - bi;
    const hitAt = k => { const age = lt - k; return age > 0 && age < .6 ? Math.exp(-age * 5) : 0; };
    const h1 = hitAt(.35) + hitAt(1.7), h2 = hitAt(1.03) + hitAt(2.4), h3 = hitAt(3.1);
    const push3 = ease(seg(lt, 2.5, 3.05)), zoom = lerp(1, 1.7, push3);
    const [sx, sy] = shakeXY(t, h3 * 22 + (h1 + h2) * 5);
    camBegin(lerp(960, 1420, push3) + sx, lerp(540, 700, push3) + sy, zoom);
    sky('#8EC3E6', '#E4F2EA');
    peak(600, 120, 560, 420, ROCK, 31, { snow: .4 });
    peak(1550, 80, 560, 480, ROCK, 37, { snow: .42 });
    hill(600, 30, '#9CC869', 6);
    hill(780, 20, GRASS, 8);
    flowers(-200, 2100, 800, 1060, 45, 9);
    cow(360, 880, 20, t, { nod: h1, ring: h1, swing: Math.sin(lt * 14) * .35 * h1, eyes: h1 > .3 ? 'closed' : 'dot' });
    cow(1000, 760, 13, t, { flip: true, nod: h2, ring: h2, swing: Math.sin(lt * 14) * .35 * h2 });
    // Clawd between them, rattled by every bong
    const rattled = h1 + h2 + h3;
    hiker(760, 950, 20, { dy: -rattled * 1.2, sq: -rattled * .12, rot: Math.sin(lt * 40) * .06 * rattled, aL: .9 + rattled, aR: .9 + rattled,
      ...mood(t, [[13, 'happy'], [13.35, 'x', 'music'], [13.9, 'narrow'], [15.4, 'swirl', 'swirl']]), mouth: rattled > .3 ? 'O' : 'wobble' });
    cow(1470, 900, 24, t, { flip: true, nod: h3, ring: h3, bell: lerp(1, 2.6, push3), swing: Math.sin(lt * 12) * .3 * h3, eyes: 'closed' });
    camEnd();
    sfx('BONG', 330, 470, 110, PAL.ochre, lt - .35, { life: .7 });
    sfx('BONG', 1000, 400, 90, PAL.ochre, lt - 1.03, { life: .7, rot: .1 });
    sfx('BONG', 250, 520, 110, PAL.ochre, lt - 1.7, { life: .7, rot: .06 });
    sfx('BONG', 1150, 350, 90, PAL.ochre, lt - 2.4, { life: .7 });
    sfx('BOOONNNG!!', 960, 250, 190, RED, lt - 3.1, { life: 1.2 });
  }

  // ================= 5. The pocket knife (17.4 – 21.8) =================
  // Each tool is drawn along +x from the knife's pivot, length L.
  const TOOLS = [
    (L, sw) => paint([[0, -14], [L * .85, -14], [L, 0], [0, 12]], { wash: '#D7DCE3', fill: '#8C96A8', fillOp: 70, ink: PAL.ink, sw }),
    (L, sw) => { const p = [[0, -12]]; for (let i = 1; i < 12; i++) p.push([L * i / 12, i % 2 ? -22 : -12]); p.push([L, -12], [L, 12], [0, 12]); paint(p, { wash: '#C9CED8', ink: PAL.ink, sw }); },
    (L, sw) => { paint(rectPts(0, -7, L * .6, 14), { wash: '#C9CED8', ink: PAL.ink, sw }); paint(ellPts(L * .8, 0, L * .2, 22, 16), { wash: '#C9CED8', ink: PAL.ink, sw }); },
    (L, sw) => { const p = []; for (let i = 0; i <= 30; i++) { const k = i / 30; p.push([L * k, Math.sin(k * 26) * 16]); } inkLine(p, sw * 1.6, '#8C96A8', 'ink', .7); },
    (L, sw) => { paint(rectPts(0, -7, L * .65, 14), { wash: '#C9CED8', ink: PAL.ink, sw }); for (const d of [-18, -6, 6, 18]) paint(rectPts(L * .65, d - 3, L * .35, 6), { wash: '#C9CED8', ink: PAL.ink, sw: sw * .6 }); },
    (L, sw) => { paint(rectPts(0, -7, L * .6, 14), { wash: '#C9CED8', ink: PAL.ink, sw }); paint(ellPts(L * .82, 0, L * .2, 30, 18), { wash: '#BFE0EE', fill: PAL.sky, fillOp: 60, ink: PAL.ink, sw: sw * 1.4 }); },
    (L, sw) => { paint(rectPts(0, -6, L, 12), { wash: '#6E9F58', ink: PAL.ink, sw }); for (let i = 0; i < 6; i++) inkLine([[L * .6 + i * L * .07, -6], [L * .6 + i * L * .07, -26]], sw, PAL.cream, 'inkfine', 0); },
    (L, sw) => { paint(rectPts(0, -7, L * .55, 14), { wash: '#C9CED8', ink: PAL.ink, sw }); paint(heartPts(L * .8, 0, 26), { wash: '#6B3A26', ink: PAL.ink, sw }); },   // a chocolate spatula, obviously
    (L, sw) => { paint(rectPts(0, -6, L * .6, 12), { wash: '#C9CED8', ink: PAL.ink, sw }); paint(ellPts(L * .84, 0, L * .18, L * .12, 16), { wash: '#F4E28A', fill: PAL.ochre, fillOp: 90, ink: PAL.ink, sw }); for (const [hx, hy] of [[.8, -.03], [.9, .04], [.78, .06]]) paint(ellPts(L * hx, L * hy, 6, 6, 8), { wash: '#E0B63A', ink: null }); }   // cheese
  ];
  function knife(x, y, lt, t) {
    const n = TOOLS.length;
    for (let i = n - 1; i >= 0; i--) {
      const k = backOut(seg(lt, .5 + i * .2, .8 + i * .2)), a = lerp(0, -Math.PI * .95 + i / (n - 1) * Math.PI * 1.15, k);
      if (k < .02) continue;
      push(); translate(x + 60, y); rotate(a); TOOLS[i](lerp(60, 190, k), .8); pop();
    }
    // the alphorn is always the last tool
    const ak = easeOut(seg(lt, 2.45, 3.0));
    if (ak > .01) {
      push(); translate(x + 60, y); rotate(lerp(-.2, -.35, ak));
      const L = 1300 * ak, pts = [];
      for (let i = 0; i <= 10; i++) pts.push([L * i / 10, -8 - i * 1.2]);
      for (let i = 10; i >= 0; i--) pts.push([L * i / 10, 8 + i * 1.2]);
      paint(pts, { wash: '#C98A4E', fill: '#8A5A2E', fillOp: 80, tex: .6, ink: PAL.ink, sw: 1 });
      if (L > 400) { paint([[L - 10, -20], [L + 60, -85], [L + 90, 0], [L + 60, 85], [L - 10, 20]], { wash: '#C98A4E', fill: '#8A5A2E', fillOp: 80, ink: PAL.ink, sw: 1.1, curv: .5 }); paint(ellPts(L + 75, 0, 22, 82, 16), { wash: '#4A2A18', ink: null }); }
      pop();
    }
    paint(rrPts(x - 90, y - 30, 190, 60, 28), { wash: RED, fill: RED_DK, fillOp: 70, tex: .6, ink: PAL.ink, sw: 1.1 });
    paint(rectPts(x - 12, y - 16, 24, 32), { wash: '#FFFDF6', ink: null }); paint(rectPts(x - 16, y - 6, 32, 12), { wash: '#FFFDF6', ink: null });
  }
  function pocketKnife(t, lt) {
    const [sx, sy] = shakeXY(t, lt > 2.5 && lt < 2.8 ? 8 : lt > 3.45 && lt < 3.7 ? 10 : 0);
    const z = lerp(1.05, 1.0, ease(lt / 4.4));
    camBegin(960 + sx, 540 + sy, z);
    sky('#8CC0E4', '#F0E6D2');
    peak(1400, 120, 620, 520, ROCK, 41, { snow: .4 });
    cloud(500, 220, 60);
    hill(650, 25, '#9CC869', 12);
    // bench
    paint(rectPts(260, 820, 900, 34), { wash: WOODC, ink: PAL.ink, sw: .9 });
    for (const lx of [320, 1060]) paint(rectPts(lx, 850, 26, 120), { wash: '#6B3A26', ink: PAL.ink, sw: .8 });
    flowers(-200, 2100, 900, 1060, 30, 13);
    const chomp = lt > 3.35, lid = chomp ? Math.sin(seg(lt, 3.35, 3.85) * Math.PI) : 0;
    const bp = bpOf(t), aL = chomp ? 1.0 : .4 + .1 * Math.sin(bp * TAU);
    const cx = 620, cy = 830, u = 34;
    hiker(cx, cy, u, {
      aL, aR: .15, lid, ...mood(t, [[17.4, 'happy', 'heart'], [17.9, 'spark', 'spark'], [17.4 + 2.5, 'scared', '!?'], [17.4 + 3.3, 'narrow']]), mouth: lt > 2.5 && !chomp ? 'O' : 'smile',
      armL: (u, sw) => {   // the chocolate bar, getting shorter after the chomp
        const left = lt > 3.6 ? .45 : 1;
        paint(rectPts(-.2 * u, -.9 * u, 2.4 * u * left, 1.8 * u), { wash: '#6B3A26', fill: '#4A2616', fillOp: 70, ink: PAL.ink, sw: sw * .7 });
        paint(rectPts(1.2 * u * left, -1 * u, 1.3 * u * left, 2 * u), { wash: RED, ink: PAL.ink, sw: sw * .6 });
      }
    });
    const [kx, ky] = armTip(cx, cy, u, 0, .15);
    knife(kx + 40, ky, lt, t);
    camEnd();
    sfx('TÖÖÖT', 1500, 250, 120, PAL.ochre, lt - 2.9, { life: .9, rot: -.15 });
    sfx('CHOMP!', 420, 420, 130, PAL.cream, lt - 3.55, { life: .85 });
  }

  // ================= 6. The summit and the coffee (21.8 – 27.0) =================
  function kiosk(x, y, t, lt) {
    paint(rectPts(x - 150, y - 200, 300, 200, 2), { wash: '#B8773F', fill: '#7C4A2C', fillOp: 80, tex: .7, ink: PAL.ink, sw: 1 });
    paint([[x - 200, y - 190], [x, y - 300], [x + 200, y - 190]], { wash: '#6B3A26', ink: PAL.ink, sw: 1 });
    paint(rectPts(x - 110, y - 170, 220, 90), { wash: '#3B2A22', ink: PAL.ink, sw: .8 });
    letter('KAFI', x, y - 250, 40, PAL.cream, {});
    // the price board swings in
    const k = backOut(seg(lt, 3.15, 3.55)), bx = x + 250, by = y - 210;
    if (k > .02) {
      push(); translate(bx, by); rotate(Math.sin(lt * 8) * .06 * Math.exp(-(lt - 3.3) * 2)); scale(k);
      paint(rectPts(-120, -60, 240, 150, 3), { wash: '#FFF5E2', fill: '#E8D5B0', fillOp: 60, ink: PAL.ink, sw: 1.2 });
      pop();
      letter('1 Kafi', bx, by - 20, 38 * k, PAL.ink, { ink: false });
      letter('CHF 14.50', bx, by + 40, 50 * k, RED, { ink: false, rot: -.05 });
    }
  }
  function summit(t, lt) {
    const pan = ease(seg(lt, 2.3, 3.0)), zOut = lerp(1.35, 1.0, easeOut(seg(lt, 0, 1.2)));
    const faint = seg(lt, 3.75, 4.05);
    const [sx, sy] = shakeXY(t, lt > 4.05 && lt < 4.3 ? 12 : 0);
    camBegin(lerp(900, 1130, pan) + sx, lerp(520, 540, pan) + sy, zOut);
    sky('#6FAEDD', '#D6ECF5');
    sun(1650, 170, 60, t);
    // sea of clouds with far peaks
    peak(200, 380, 760, 300, '#A8AAC2', 51, { snow: .45, sw: .6 });
    peak(1750, 330, 760, 330, '#A8AAC2', 53, { snow: .45, sw: .6 });
    for (let i = 0; i < 8; i++) cloud(-100 + i * 300, 760 + (i % 2) * 30 + wob(t, .1, i) * 8, 90, 245);
    peak(960, 560, 1250, 900, ROCK, 57, { snow: .28, rw: 1.3, sw: 1.3 });
    flag(1030, 604, 60, t, 1);
    paint(rectPts(1250, 845, 400, 26), { wash: '#7C4A2C', ink: PAL.ink, sw: .9 });
    kiosk(1450, 850, t, lt);
    // Clawd on the top: a yodel, then the price
    const hop = lt < .9 ? backOut(seg(lt, .2, .7)) : 1;
    const style = lt > 1.0 && lt < 2.6 ? 'roof' : 'idle', m = move(style, t);
    const x = 925, y = 592 + (1 - hop) * 260;
    hiker(x, y, 22, { ...m, dx: 0, dy: m.dy, rot: -1.5 * easeIn(faint), sq: m.sq,
      ...mood(t, [[21.8, 'happy'], [22.8, 'closed', 'music'], [21.8 + 2.6, 'look'], [21.8 + 3.3, 'x', '!!']]), lookX: 1,
      mouth: lt > 1.0 && lt < 2.5 ? 'O' : lt > 3.3 ? 'wobble' : 'smile' });
    camEnd();
    sfx('HOLDRIO-Ü!', 700, 270, 120, PAL.cream, lt - 1.0, { life: 1.5, rot: -.08 });
    sfx('holdrio...', 1500, 420, 60, PAL.cream, lt - 1.6, { life: 1.1, rot: .05, alpha: .8 });
    sfx('...rio-ü', 250, 470, 44, PAL.cream, lt - 2.1, { life: 1.0, rot: -.05, alpha: .7 });
    sfx('THUD', 560, 330, 110, PAL.ochre, lt - 4.05, { life: .8 });
    // iris out on the fainted hiker
    const ir = lerp(1400, 0, easeIn(seg(lt, 4.45, 5.1)));
    if (lt > 4.45) {
      flushLetters();
      iris(925 - 170, 540, ir, PAL.ink);
      letter('ENDE', 960, 540, 110, PAL.cream, { pop: (lt - 4.9) * 4, screen: true });
    }
  }

  chapter('alps', 0, FILM_DUR, [[0, postcard], [4.3, station], [8.6, trail], [13.0, cows], [17.4, pocketKnife], [21.8, summit]]);
})();
