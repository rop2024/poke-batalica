import React from "react";
import { useApp } from "../BattleContext";
import { useNavigate, Link } from "react-router-dom";

export default function LoginPage() {
  const { login, register } = useApp();
  const navigate = useNavigate();
  const [mode, setMode] = React.useState<"login" | "register">("login");
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") await login(username, password);
      else await register(username, password);
      navigate("/lobby");
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="center" style={{ minHeight: "60vh" }}>
      <div className="card" style={{ maxWidth: 400, width: "100%" }}>
        <h2>{mode === "login" ? "Sign in" : "Create account"}</h2>
        <form onSubmit={handleSubmit}>
          <label>Username</label>
          <input
            className="search-input"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Choose a username"
            required
          />
          <label>Password</label>
          <input
            className="search-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Choose a password"
            required
          />
          {error && <div className="small" style={{ color: "var(--danger)", marginBottom: 10 }}>{error}</div>}
          <button className="btn btn-primary btn-full" disabled={loading}>
            {loading ? <span className="spinner" /> : (mode === "login" ? "Sign in" : "Create account")}
          </button>
        </form>
        <p className="small" style={{ marginTop: 14, textAlign: "center" }}>
          {mode === "login" ? "Don't have an account? " : "Already have an account? "}
          <button
            type="button"
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            className="link-btn"
          >
            {mode === "login" ? "Create one" : "Sign in"}
          </button>
        </p>
      </div>
      <p className="small" style={{ marginTop: 16, textAlign: "center" }}>
        <Link to="/">Back to home</Link>
      </p>
    </div>
  );
}
