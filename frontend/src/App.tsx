import React from "react";
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from "react-router-dom";
import { AppProvider, useApp } from "./BattleContext";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import LobbyPage from "./pages/LobbyPage";
import RoomPage from "./pages/RoomPage";
import BattlePage from "./pages/BattlePage";
import ResultsPage from "./pages/ResultsPage";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user } = useApp();
  const navigate = useNavigate();
  React.useEffect(() => {
    if (!user) navigate("/login");
  }, [user, navigate]);
  if (!user) return null;
  return <>{children}</>;
}

function SignOutButton() {
  const { logout } = useApp();
  return <button onClick={logout}>Sign out</button>;
}

function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <div className="app">
          <nav className="nav">
            <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
              Pokemon Battle
            </NavLink>
            <NavLink to="/lobby" className={({ isActive }) => (isActive ? "active" : "")}>
              Lobby
            </NavLink>
            <div className="userbar">
              <RequireAuth>
                <SignOutButton />
              </RequireAuth>
            </div>
          </nav>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/lobby" element={<RequireAuth><LobbyPage /></RequireAuth>} />
            <Route path="/room/:roomId" element={<RequireAuth><RoomPage /></RequireAuth>} />
            <Route path="/battle/:battleId" element={<RequireAuth><BattlePage /></RequireAuth>} />
            <Route path="/results" element={<RequireAuth><ResultsPage /></RequireAuth>} />
          </Routes>
        </div>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
