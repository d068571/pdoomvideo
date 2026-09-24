// show.js: timeline for the Swiss hiking short (swiss.html). Replaces timeline.js: same chapter/shot registry,
// brush wipes between shots and a narrator caption bar in place of the karaoke. No P(doom) meter here.
//
// The short runs 27 s on the same 88 BPM grid as the video, so pulse()/move() still land on the soundtrack's beats.

const FILM_DUR = 27;
const CH = [];
function chapter(name, start, end, shots) { CH.push({ name, start, end, shots }); CH.sort((a, b) => a.start - b.start); }

// Shot breaks that get a brush wipe.
const WIPES = [4.3, 8.6, 13.0, 17.4, 21.8];
const WIPE_TR = .3;
const WIPE_COLS = [[PAL.sap, PAL.teal], ['#C8324A', PAL.rose], [PAL.ochre, PAL.clay], [PAL.teal, PAL.sky], [PAL.violet, PAL.indigo]];

// Narrator captions: [start, end, text].
const CAPS = [
  [.5, 4.0, "Clawd goes hiking in the Swiss Alps."],
  [4.6, 8.3, "Swiss trains leave on time. To the second."],
  [8.9, 12.7, "Sign: 1 h 30. Local grandma: 12 minutes."],
  [13.3, 17.1, "The cows wear bells. Big bells."],
  [17.7, 21.5, "The pocket knife has a tool for everything."],
  [22.1, 24.9, "The summit! Time for a coffee..."],
  [25.0, 27.0, "CHF 14.50?!"]
];

function drawWorld(t) {
  const ch = CH.find(c => t >= c.start && t < c.end);
  if (ch) {
    let i = 0; while (i + 1 < ch.shots.length && t >= ch.shots[i + 1][0]) i++;
    const t0 = ch.shots[i][0], end = i + 1 < ch.shots.length ? ch.shots[i + 1][0] : ch.end;
    ch.shots[i][1](t, t - t0, end - t0);
    CAM = null;
  }
  flushLetters();
  WIPES.forEach((b, j) => { if (Math.abs(t - b) < WIPE_TR) wipe((t - (b - WIPE_TR)) / (2 * WIPE_TR), j); });
  caption(t);
}

// ---------- brush wipe (as in timeline.js, with alpine colours) ----------
function wipe(p, idx) {
  const [c1, c2] = WIPE_COLS[idx % WIPE_COLS.length], n = 5, bh = (H + 420) / n + 40;
  push(); translate(W / 2, H / 2); rotate(-.1); translate(-W / 2, -H / 2);
  for (let i = 0; i < n; i++) {
    const y0 = -230 + i * (H + 420) / n, d = [0, .14, .06, .18, .1][i];
    const q = p < .5 ? easeOut(clamp((p * 2 - d) / (1 - d))) : ease(clamp(((p - .5) * 2 - d) / (1 - d)));
    const x0 = p < .5 ? -300 : lerp(-300, W + 400, q), x1 = p < .5 ? lerp(-300, W + 400, q) : W + 400;
    if (x1 - x0 < 30) continue;
    const pts = [], rag = (k, side) => side * (40 + 50 * hash(i * 31 + k)) + jit(12);
    for (let k = 0; k <= 8; k++) pts.push([lerp(x0, x1, k / 8), y0 + Math.sin(k * .9 + i) * 14 + jit(5)]);
    for (let k = 1; k < 9; k++) pts.push([x1 + rag(k, 1) - 40, y0 + bh * k / 9]);
    for (let k = 8; k >= 0; k--) pts.push([lerp(x0, x1, k / 8), y0 + bh + Math.sin(k * .8 + i * 2) * 14 + jit(5)]);
    if (p >= .5) for (let k = 8; k > 0; k--) pts.push([x0 - rag(k + 20, 1) + 40, y0 + bh * k / 9]);
    paint(pts, { wash: i % 2 ? c1 : c2, washOp: 255, fill: i % 2 ? c2 : c1, fillOp: 70, bleed: .05, tex: .8, border: .6, ink: null,
      hatch: { d: 44, a: 0, o: { rand: .6, gradient: .5 }, b: 'charcoal', c: i % 2 ? c2 : PAL.cream, w: .8 } });
  }
  pop();
}

// ---------- narrator caption (the karaoke bar, typed on instead of sung) ----------
function caption(t) {
  const L = CAPS.find(l => t >= l[0] && t < l[1]); if (!L) return;
  const [a, b, txt] = L;
  outX.font = '800 50px "Shantell Sans", sans-serif';
  const tw = outX.measureText(txt).width, grow = easeOut((t - a) / .18) * (1 - ease((t - (b - .12)) / .12));
  if (grow < .02) return;
  const w = (tw + 110) * grow, x0 = 960 - w / 2, y0 = 978;
  const pts = [[x0 + jit(8), y0 + jit(4)], [x0 + w / 2, y0 - 4 + jit(4)], [x0 + w + jit(8), y0 + jit(4)], [x0 + w + 14 + jit(8), y0 + 44], [x0 + w + jit(8), y0 + 88 + jit(4)], [x0 + w / 2, y0 + 92 + jit(4)], [x0 + jit(8), y0 + 88 + jit(4)], [x0 - 14 + jit(8), y0 + 44]];
  paint(pts, { wash: PAL.ink, washOp: 225, fill: '#C8324A', fillOp: 60, tex: .7, border: .4, ink: null });
  KARAOKE = { a, b, txt, grow };
}
function drawKaraokeText(c) {
  if (!KARAOKE || KARAOKE.grow < .85) return;
  const { a, b, txt } = KARAOKE;
  c.font = '800 50px "Shantell Sans", sans-serif'; c.textBaseline = 'middle'; c.textAlign = 'center';
  const n = Math.floor(clamp((T - a) / Math.min(b - a - .3, .3 + txt.length * .035)) * txt.length);
  c.fillStyle = PAL.cream;
  const full = c.measureText(txt).width;
  c.textAlign = 'left'; c.fillText(txt.slice(0, n), 960 - full / 2, 1022);
}
