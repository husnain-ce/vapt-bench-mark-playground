import React, { useState } from "react";

export default function Auth({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    setSuccess("");

    const endpoint = isRegister ? "/sso/register" : "/sso/login";

    try {
      const body = { username, password };

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error("Request failed");
      const data = await res.json();

      if (isRegister) {
        setSuccess("Registration successful! Please log in.");
        setIsRegister(false);
        setPassword("");
      } else {
        // Login success
        localStorage.setItem("token", data.token);
        localStorage.setItem("user", JSON.stringify(data.user));
        onLogin(data.user);
      }
    } catch (err) {
      setErr("Request failed");
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: 400 }}>
      <h3 className="mb-3">{isRegister ? "Register" : "Login"}</h3>

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <input
            className="form-control"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div className="mb-3">
          <input
            type="password"
            className="form-control"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {err && <div className="alert alert-danger">{err}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <button className="btn btn-primary w-100" type="submit">
          {isRegister ? "Create Account" : "Login"}
        </button>
      </form>

      <div className="text-center mt-3">
        {isRegister ? (
          <span>
            Already have an account?{" "}
            <button
              className="btn btn-link p-0"
              onClick={() => setIsRegister(false)}
            >
              Log in
            </button>
          </span>
        ) : (
          <span>
            New user?{" "}
            <button
              className="btn btn-link p-0"
              onClick={() => setIsRegister(true)}
            >
              Register
            </button>
          </span>
        )}
      </div>
    </div>
  );
}
