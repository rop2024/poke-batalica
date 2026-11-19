import type { SoundPrefs } from "./types";

const AUDIO_DIR = "/audio";

const SFX_FILES: Record<string, string> = {
  click: "click.wav",
  hit: "hit.wav",
  "critical-hit": "critical-hit.wav",
  victory: "victory.wav",
  defeat: "defeat.wav",
  "super-effective": "super-effective.wav",
  "not-very-effective": "not-very-effective.wav",
  faint: "faint.wav",
};

let audioCtx: AudioContext | null = null;
let masterGain: GainNode | null = null;
let effectsGain: GainNode | null = null;
let musicGain: GainNode | null = null;
let musicSource: AudioBufferSourceNode | null = null;
let musicBuffer: AudioBuffer | null = null;
let musicLooping = false;

const soundBuffers: Record<string, AudioBuffer> = {};

function ensureContext(prefs: SoundPrefs) {
  if (audioCtx) return audioCtx;
  audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
  masterGain = audioCtx.createGain();
  effectsGain = audioCtx.createGain();
  musicGain = audioCtx.createGain();
  masterGain.connect(audioCtx.destination);
  effectsGain.connect(masterGain);
  musicGain.connect(masterGain);
  applyPrefs(prefs);
  return audioCtx;
}

function applyPrefs(prefs: SoundPrefs) {
  if (masterGain) masterGain.gain.value = prefs.muted ? 0 : prefs.master;
  if (effectsGain) effectsGain.gain.value = prefs.effects;
  if (musicGain) musicGain.gain.value = prefs.music;
  if (audioCtx) {
    audioCtx.resume();
  }
}

async function loadBuffer(name: string, path: string): Promise<AudioBuffer> {
  if (soundBuffers[name]) return soundBuffers[name];
  const ctx = ensureContext({ master: 1, effects: 1, music: 1, muted: false } as SoundPrefs);
  const res = await fetch(path);
  const arrayBuffer = await res.arrayBuffer();
  const buffer = await ctx.decodeAudioData(arrayBuffer);
  soundBuffers[name] = buffer;
  return buffer;
}

export function initAudio(prefs: SoundPrefs) {
  ensureContext(prefs);
  applyPrefs(prefs);
  // Preload all SFX buffers (ignoring failures silently)
  Object.entries(SFX_FILES).forEach(([name, file]) => {
    loadBuffer(name, `${AUDIO_DIR}/${file}`).catch(() => {});
  });
}

export function playSound(name: string, prefs: SoundPrefs) {
  if (prefs.muted) return;
  ensureContext(prefs);
  applyPrefs(prefs);
  const buffer = soundBuffers[name];
  if (!buffer) {
    // Fallback: try loading on demand
    const file = SFX_FILES[name];
    if (!file) return;
    loadBuffer(name, `${AUDIO_DIR}/${file}`).then((buf) => {
      playBuffer(buf, effectsGain);
    }).catch(() => {});
    return;
  }
  playBuffer(buffer, effectsGain);
}

function playBuffer(buffer: AudioBuffer, gainNode: GainNode | null) {
  if (!gainNode || !audioCtx) return;
  const src = audioCtx.createBufferSource();
  src.buffer = buffer;
  src.connect(gainNode);
  src.start(0);
  src.onended = () => {
    src.disconnect();
  };
}

export function playCry(cryUrl: string | null, prefs: SoundPrefs) {
  if (prefs.muted || !cryUrl) return;
  // Cries are typically ogg/mp3; use HTML audio for streaming
  const audio = new Audio(cryUrl);
  audio.volume = (prefs.master * prefs.effects);
  audio.play().catch(() => {});
}

export function playMusic(prefs: SoundPrefs) {
  if (prefs.muted || !audioCtx || !musicBuffer) return;
  if (musicSource) {
    musicSource.stop();
    musicSource.disconnect();
  }
  musicSource = audioCtx.createBufferSource();
  musicSource.buffer = musicBuffer;
  musicSource.loop = musicLooping;
  musicSource.connect(musicGain!);
  musicSource.start(0);
}

export function stopMusic() {
  if (musicSource) {
    try { musicSource.stop(); } catch {}
    musicSource.disconnect();
    musicSource = null;
  }
}

export function loadMusic(url: string) {
  return fetch(url)
    .then((r) => r.arrayBuffer())
    .then((ab) => {
      if (!audioCtx) return;
      return audioCtx.decodeAudioData(ab);
    })
    .then((buf) => {
      if (buf) musicBuffer = buf;
    });
}

export type { SoundPrefs };
