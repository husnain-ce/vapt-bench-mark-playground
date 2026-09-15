import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import Auth from "./Auth";
import Inbox from "./Inbox";
import Compose from "./Compose";

export default function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    const token = localStorage.getItem("token");
    if (savedUser && token) setUser(JSON.parse(savedUser));
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
  };

  if (!user) return <Auth onLogin={setUser} />;

  return (
    <div className="container mt-4">
      <nav className="navbar navbar-light bg-light mb-3">
        <span className="navbar-brand mb-0 h1">📧 ASIS Mail</span>
        <div>
          <span className="me-3">Hi, {user.username}</span>
          <button className="btn btn-outline-primary me-2" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </nav>

      <ul className="nav nav-tabs mb-3">
        <li className="nav-item">
          <a className="nav-link active" data-bs-toggle="tab" href="#inbox">
            Inbox
          </a>
        </li>
        <li className="nav-item">
          <a className="nav-link" data-bs-toggle="tab" href="#compose">
            Compose
          </a>
        </li>
      </ul>

      <div className="tab-content">
        <div className="tab-pane fade show active" id="inbox">
          <Inbox user={user} />
        </div>
        <div className="tab-pane fade" id="compose">
          <Compose user={user} />
        </div>
      </div>
    </div>
  );
}
