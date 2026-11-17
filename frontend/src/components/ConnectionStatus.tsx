interface Props {
  status: string;
}

export default function ConnectionStatus({ status }: Props) {
  const dotColor = status === "connected" ? "var(--success)" : status === "connecting" ? "var(--warning)" : "var(--danger)";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.85rem", color: "var(--muted)" }}>
      <div style={{ width: 8, height: 8, borderRadius: "50%", background: dotColor }} />
      {status === "connected" ? "Connected" : status === "connecting" ? "Connecting..." : "Disconnected"}
    </div>
  );
}
