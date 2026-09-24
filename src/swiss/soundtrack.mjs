// soundtrack.mjs: synthesizes the Swiss short's soundtrack (no samples, no dependencies) → assets/swiss.wav
//   node src/swiss/soundtrack.mjs
// A little oompah band on the film's 88 BPM grid (beat n at 0.21 + n * 0.682 s), plus the on-screen gags:
// the departing train, the grandma whoosh, five cowbells, the alphorn, the chomp, a yodel with echoes,
// a record scratch at the coffee price and a sad tuba to finish.
import { writeFileSync } from 'node:fs';

const SR = 44100, DUR = 27, N = SR * DUR, out = new Float32Array(N);
const BEAT = 60 / 88, OFF = 0.21;
const midi = m => 440 * Math.pow(2, (m - 69) / 12);
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

function add(t0, dur, gain, fn) {
  const a = Math.max(0, Math.floor(t0 * SR)), b = Math.min(N, Math.floor((t0 + dur) * SR));
  for (let i = a; i < b; i++) { const t = i / SR - t0; out[i] += gain * fn(t, t / dur); }
}
const env = (t, atk, dec) => Math.min(1, t / atk) * Math.exp(-t / dec);
const saw = (f, t, h = 8) => { let s = 0; for (let k = 1; k <= h; k++) s += Math.sin(2 * Math.PI * f * k * t) / k; return s; };

// ---------- the band (stops dead at the coffee price, 25.0 s) ----------
const MUSIC_END = 25.0;
const PROG = ['F', 'F', 'C', 'C', 'F', 'Bb', 'C', 'F'];
const CH = { F: [53, 57, 60], C: [48, 52, 55, 58], Bb: [46, 50, 53] };
const BASS = { F: [41, 36], C: [36, 43], Bb: [34, 41] };
const MEL = {
  F: [72, 69, 65, 69, 72, 69, 77, 72], C: [67, 64, 60, 64, 67, 70, 72, 67], Bb: [70, 65, 62, 65, 70, 74, 72, 70]
};
for (let n = 0; ; n++) {
  const t = OFF + n * BEAT; if (t >= MUSIC_END) break;
  const bar = Math.floor(n / 4), chord = PROG[bar % PROG.length], beat = n % 4;
  if (beat % 2 === 0) {   // oom: tuba
    const f = midi(BASS[chord][beat / 2]);
    add(t, .45, .32, (x) => env(x, .015, .18) * (saw(f, x, 5) * .7 + Math.sin(2 * Math.PI * f * x) * .5));
  } else {                // pah: short accordion chord
    for (const m of CH[chord].slice(0, 3)) { const f = midi(m); add(t, .2, .07, x => env(x, .008, .07) * (saw(f, x, 6) + saw(f * 1.004, x, 6))); }
  }
  for (let e = 0; e < 2; e++) {   // melody on eighths, accordion reeds slightly detuned
    const m = MEL[chord][beat * 2 + e], f = midi(m), te = t + e * BEAT / 2;
    if (te >= MUSIC_END) break;
    add(te, BEAT / 2 * .9, .075, x => Math.min(1, x / .02) * Math.min(1, (BEAT / 2 * .9 - x) / .03) * (saw(f, x, 5) + saw(f * 1.006, x, 5) * .8) * (1 + .15 * Math.sin(2 * Math.PI * 6 * x)));
  }
}
// record scratch at the price
add(MUSIC_END - .02, .35, .35, (x, k) => (rnd() * 2 - 1) * .5 * (1 - k) + Math.sin(2 * Math.PI * (900 - 2400 * k) * x) * (1 - k) * .6);

// ---------- gags ----------
const noise = (t0, dur, gain, shape) => add(t0, dur, gain, (x, k) => (rnd() * 2 - 1) * shape(x, k));
// 2. the train: brakes release, then it whooshes off
noise(4.3 + 2.25, .5, .25, (x, k) => Math.sin(Math.PI * k) * (.6 + .4 * Math.sin(x * 900)));
noise(4.3 + 2.6, 1.3, .3, (x, k) => Math.sin(Math.PI * k) * Math.pow(1 - k, .5));
add(4.3 + 2.4, .5, .12, (x, k) => Math.sin(2 * Math.PI * 660 * x) * (1 - k) + Math.sin(2 * Math.PI * 830 * x) * (1 - k));   // departure chime
// 3. the grandma whooshes past
noise(8.6 + 1.7, .6, .28, (x, k) => Math.sin(Math.PI * k) * Math.sin(Math.PI * k));
// 4. cowbells: inharmonic partials; the last one is enormous
const bell = (t, f, g, dec) => add(t, dec * 4, g, x => env(x, .002, dec) * (Math.sin(2 * Math.PI * f * x) + .7 * Math.sin(2 * Math.PI * f * 1.47 * x) + .45 * Math.sin(2 * Math.PI * f * 2.09 * x) + .3 * Math.sin(2 * Math.PI * f * 2.76 * x)));
for (const [lt, f] of [[.35, 620], [1.03, 700], [1.7, 590], [2.4, 680]]) bell(13 + lt, f, .22, .25);
bell(13 + 3.1, 196, .55, .7);
// 5. the alphorn unfolds, then the chomp
add(17.4 + 2.85, 1.0, .3, (x, k) => Math.min(1, x / .08) * (1 - k) * saw(midi(46) * (1 + .01 * Math.sin(2 * Math.PI * 5 * x)), x, 10));
noise(17.4 + 3.55, .12, .5, (x, k) => (1 - k) * (1 - k));
// 6. the yodel (chest/head flips) and two echoes, then a thud and a sad tuba
const YODEL = [[65, .22], [72, .18], [69, .22], [77, .18], [72, .22], [81, .5]];
const yodel = (t0, g) => { let t = t0; for (const [m, d] of YODEL) { const f = midi(m); add(t, d + .04, g, (x, k) => Math.min(1, x / .02) * Math.min(1, (d + .04 - x) / .04) * (Math.sin(2 * Math.PI * f * x) + .3 * Math.sin(4 * Math.PI * f * x) + .12 * Math.sin(6 * Math.PI * f * x)) * (1 + .1 * Math.sin(2 * Math.PI * 5.5 * x))); t += d; } };
yodel(21.8 + 1.0, .22); yodel(21.8 + 1.6, .08); yodel(21.8 + 2.1, .035);
add(21.8 + 4.05, .45, .6, (x, k) => (1 - k) * Math.sin(2 * Math.PI * (90 - 50 * k) * x));
[[46, .0], [45, .38], [44, .76], [43, 1.14]].forEach(([m, d], i) => add(26.0 - 1.35 + d + .1, i === 3 ? .9 : .36, .2, (x, k) => Math.min(1, x / .03) * (1 - k * .6) * saw(midi(m) * (i === 3 ? 1 + .012 * Math.sin(2 * Math.PI * 6 * x) : 1), x, 6)));

// ---------- normalise, fade, write 16-bit mono WAV ----------
let peak = 0; for (let i = 0; i < N; i++) peak = Math.max(peak, Math.abs(out[i]));
const buf = Buffer.alloc(44 + N * 2);
buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 2, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(1, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(N * 2, 40);
for (let i = 0; i < N; i++) { const fade = Math.min(1, (N - i) / (SR * .3)), v = Math.tanh(out[i] / peak * 1.1) * .85 * fade; buf.writeInt16LE(Math.round(v * 32767), 44 + i * 2); }
writeFileSync('assets/swiss.wav', buf);
console.log('wrote assets/swiss.wav');
