import React, { useState } from "react";
import {apiFetch} from "./api";

export default function Compose({ user }) {
  const [to, setTo] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [attachment, setAttachment] = useState(null);
  const [status, setStatus] = useState("");
  const token = localStorage.getItem("token");

  const handleSend = async (e) => {
    e.preventDefault();
    setStatus("Sending...");
    const xml = `<message>
      <to>${to}</to>
      <subject>${subject}</subject>
      <body>${body}</body>
    </message>`;

    const form = new FormData();
    form.append("xml", xml);
    if (attachment) form.append("attachment", attachment);

    try {
      const res = await apiFetch("/api/compose", {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error("send failed");
      setStatus("Message sent!");
      setTo("");
      setSubject("");
      setBody("");
      setAttachment(null);
    } catch (e) {
      setStatus("Failed to send");
    }
  };

  return (
    <div>
      <h5>Compose</h5>
      <form onSubmit={handleSend}>
        <div className="mb-3">
          <input
            className="form-control"
            placeholder="To"
            value={to}
            onChange={(e) => setTo(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <input
            className="form-control"
            placeholder="Subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <textarea
            className="form-control"
            rows="5"
            placeholder="Message body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <input
            type="file"
            className="form-control"
            onChange={(e) => setAttachment(e.target.files[0])}
          />
        </div>
        <button className="btn btn-success">Send</button>
        {status && <span className="ms-3">{status}</span>}
      </form>
    </div>
  );
}
