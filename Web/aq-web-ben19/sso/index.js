const express = require("express");
const bodyParser = require("body-parser");
const cookieParser = require("cookie-parser");
const bcrypt = require("bcrypt");
const { Pool } = require("pg");
const { v4: uuidv4 } = require("uuid");

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});
const EMAIL_DOMAIN = process.env.EMAIL_DOMAIN || "example.local";

const app = express();
app.use(bodyParser.json());
app.use(cookieParser());

// register
app.post("/register", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.status(400).send("bad");
  const hash = await bcrypt.hash(password, 10);
  const email = `${username}@${EMAIL_DOMAIN}`;
  try {
    await pool.query(
      "INSERT INTO users(username,password_hash,email) VALUES($1,$2,$3)",
      [username, hash, email]
    );
    // create a "welcome" email in db (local mailbox)
    const from = `no-reply@${EMAIL_DOMAIN}`;
    await pool.query(
      "INSERT INTO emails(user_id,from_addr,to_addr,subject,body) VALUES((SELECT id FROM users WHERE username=$1), $2, $3, $4, $5)",
      [username, from, email, "Welcome", "Welcome to the ASIS-Mail!"]
    );
    res.json({ ok: true });
  } catch (e) {
    console.error(e);
    res.status(500).send("err");
  }
});


const sessions = {};
app.post("/login", async (req, res) => {
  const { username, password } = req.body;
  const r = await pool.query(
    "SELECT id, password_hash, email FROM users WHERE username=$1",
    [username]
  );
  if (r.rows.length === 0) return res.status(401).send("bad");
  const user = r.rows[0];
  const ok = await bcrypt.compare(password, user.password_hash);
  if (!ok) return res.status(401).send("bad");
  const token = uuidv4();
  sessions[token] = {id: user.id, email: user.email};
  res.json({
    ok: true,
    token: token,
    user: { username: username, userId: user.id },
  });
});

app.get("/auth", async (req, res) => {
  const authHeader = req.headers["authorization"];
  if (!authHeader) return res.status(401).json({ message: "Unauthorized" });

  // Split the header into "Bearer <token>"
  const parts = authHeader.split(" ");
  if (parts.length !== 2 || parts[0] !== "Bearer") {
    return res.status(400).json({
      message: 'Invalid Authorization header format. Expected "Bearer <token>"',
    });
  }

  const token = parts[1];
  if (!token || !sessions[token])
    return res.status(401).json({ message: "Unauthorized" });

  const user = sessions[token];
  if (user) {
    res.set("X-User-Id", user.id);
    res.set("X-User-Email", user.email);
    return res.status(200).json({ message: "Authenticated" });
  }
});

app.get("/whoami", (req, res) => {
  const t = req.cookies.SSO_SESSION;
  if (!t || !sessions[t]) return res.status(401).json({ ok: false });
  res.json({ ok: true, user_id: sessions[t] });
});

const server = app.listen(3001, () => {
  console.log("SSO up on port 3001");
});

// Graceful shutdown
const shutdown = () => {
  console.log("Received kill signal, shutting down gracefully...");

  server.close(() => {
    console.log("Closed out remaining connections.");
    process.exit(0);
  });

  // If after 10 seconds it’s still not closed, force exit
  setTimeout(() => {
    console.error("Could not close connections in time, forcing shutdown");
    process.exit(1);
  }, 2000);
};

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);