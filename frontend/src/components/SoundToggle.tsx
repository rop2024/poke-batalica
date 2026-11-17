interface Props {
  sound: { muted: boolean; master: number; effects: number; music: number };
  onToggle: () => void;
}

export default function SoundToggle({ sound, onToggle }: Props) {
  return (
    <div className="sound-row">
      <button className="sound-btn" onClick={onToggle} style={{ color: sound.muted ? "var(--danger)" : "var(--text)" }}>
        {sound.muted ? "\u{1F507}" : "\u{1F50A}"}
      </button>
      <span>{sound.muted ? "Sound off" : "Sound on"}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        <span className="sound-label">Master</span>
        <input
          className="sound-range"
          type="range"
          min="0"
          max="1"
          step="0.1"
          defaultValue={String(sound.master)}
        />
      </div>
    </div>
  );
}
