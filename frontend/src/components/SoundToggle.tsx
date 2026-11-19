import React, { useCallback } from "react";
import { useApp } from "../BattleContext";
import type { SoundPrefs } from "../types";

interface Props {
  sound: SoundPrefs;
}

export default function SoundToggle({ sound }: Props) {
  const { playSound, setSound, initAudioCtx } = useApp();

  const handleMasterChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = parseFloat(e.target.value);
      setSound({ master: value });
      if (!audioCtxInitialized) {
        initAudioCtx();
      }
      playSound("click");
    },
    [setSound, initAudioCtx, playSound]
  );

  const handleEffectsChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = parseFloat(e.target.value);
      setSound({ effects: value });
      playSound("click");
    },
    [setSound, playSound]
  );

  const handleMusicChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = parseFloat(e.target.value);
      setSound({ music: value });
      playSound("click");
    },
    [setSound, playSound]
  );

  const [audioCtxInitialized, setAudioCtxInitialized] = React.useState(false);

  const handleInit = useCallback(() => {
    initAudioCtx();
    setAudioCtxInitialized(true);
    playSound("click");
  }, [initAudioCtx, playSound]);

  return (
    <div className="sound-row" style={{ gap: 10 }}>
      <button
        className="sound-btn"
        onClick={() => {
          setSound({ muted: !sound.muted });
          playSound("click");
        }}
        style={{ color: sound.muted ? "var(--danger)" : "var(--text)" }}
      >
        {sound.muted ? "\u{1F507}" : "\u{1F50A}"}
      </button>
      {!audioCtxInitialized && (
        <button className="btn btn-ghost" onClick={handleInit} style={{ fontSize: "0.8rem", padding: "4px 10px" }}>
          Enable Audio
        </button>
      )}
      {audioCtxInitialized && (
        <>
          <span>{sound.muted ? "Sound off" : "Sound on"}</span>
          <div style={{ display: "flex", alignItems: "center", gap: 6, minWidth: 110 }}>
            <span className="sound-label" style={{ fontSize: "0.7rem" }}>M</span>
            <input
              className="sound-range"
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={sound.master}
              onChange={handleMasterChange}
              style={{ width: 60 }}
            />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, minWidth: 110 }}>
            <span className="sound-label" style={{ fontSize: "0.7rem" }}>E</span>
            <input
              className="sound-range"
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={sound.effects}
              onChange={handleEffectsChange}
              style={{ width: 60 }}
            />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, minWidth: 110 }}>
            <span className="sound-label" style={{ fontSize: "0.7rem" }}>Mus</span>
            <input
              className="sound-range"
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={sound.music}
              onChange={handleMusicChange}
              style={{ width: 60 }}
            />
          </div>
        </>
      )}
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        <input
          id="reduced-motion"
          type="checkbox"
          checked={sound.reducedMotion}
          onChange={() => setSound({ reducedMotion: !sound.reducedMotion })}
        />
        <label htmlFor="reduced-motion" className="sound-label" style={{ fontSize: "0.75rem" }}>
          Reduced motion
        </label>
      </div>
    </div>
  );
}
