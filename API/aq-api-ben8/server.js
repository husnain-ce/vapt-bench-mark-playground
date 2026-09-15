#!/usr/bin/env node
/*
 * Target 14. Proto-Pollute-API  -- deliberately vulnerable to PROTOTYPE POLLUTION,
 * a class NONE of the other 10 labs cover. A naive recursive merge copies the
 * "__proto__" key, so an attacker writes onto Object.prototype and every object
 * in the process inherits attacker-chosen fields (e.g. isAdmin=true) -> auth bypass.
 *
 * Zero dependencies -- pure Node stdlib.   Run:  node server.js
 */
const http = require("http");

const FLAG = "flag{prototype_pollution_authz_bypass}";
const USERS = { alice: { password: "alice123", role: "user" } };

// VULN: recursive merge with no __proto__ guard -> pollutes Object.prototype
function merge(target, source) {
  for (const key in source) {
    if (key in source) {
      if (typeof source[key] === "object" && source[key] !== null) {
        if (!target[key]) target[key] = {};
        merge(target[key], source[key]);          // recurses into __proto__
      } else {
        target[key] = source[key];
      }
    }
  }
  return target;
}

function body(req) {
  return new Promise((res) => {
    let d = "";
    req.on("data", (c) => (d += c));
    req.on("end", () => { try { res(JSON.parse(d || "{}")); } catch { res({}); } });
  });
}
const send = (r, code, obj) => {
  r.writeHead(code, { "Content-Type": "application/json" });
  r.end(JSON.stringify(obj));
};

const server = http.createServer(async (req, res) => {
  const url = req.url.split("?")[0];

  if (url === "/" ) {
    return send(res, 200, {
      app: "Proto-Pollute-API",
      hint: "POST /register {profile...}  then  GET /admin",
      quick_win: 'POST /register -d \'{"__proto__":{"isAdmin":true}}\'  then GET /admin',
    });
  }

  // merges arbitrary client JSON into a fresh object -> the sink
  if (url === "/register" && req.method === "POST") {
    const input = await body(req);
    const account = {};
    merge(account, input);                          // <-- pollution happens here
    return send(res, 200, { ok: true, account });
  }

  // gate depends on a plain object's inherited property
  if (url === "/admin" && req.method === "GET") {
    const ctx = {};                                 // brand-new empty object
    if (ctx.isAdmin === true) {                     // only true if prototype polluted
      return send(res, 200, { msg: "welcome admin", flag: FLAG });
    }
    return send(res, 403, { error: "admins only", isAdmin: ctx.isAdmin || false });
  }

  send(res, 404, { error: "not found" });
});

server.listen(9014, "0.0.0.0", () =>
  console.log(" * Proto-Pollute-API on http://0.0.0.0:9014  (zero deps)")
);
