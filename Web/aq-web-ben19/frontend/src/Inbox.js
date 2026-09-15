import React, { useEffect, useState } from "react";
import { apiFetch } from "./api";

export default function Inbox({ user }) {
  const [messages, setMessages] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    apiFetch("/api/inbox", )
      .then((r) => r.json())
      .then(setMessages)
      .catch(() => setMessages([]));
  }, []);

  const openMail = async (id) => {
    try {
      const res = await apiFetch(`/api/mail/${id}`);
      const data = await res.json();
      setSelected(data);
    } catch (e) {
      alert("Failed to load email");
    }
  };

  return (
    <div>
      <h5>Your Inbox</h5>
      <table className="table table-sm table-striped">
        <thead>
          <tr>
            <th>From</th>
            <th>Subject</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {messages.map((m) => (
            <tr key={m.id} onClick={() => openMail(m.id)} style={{ cursor: "pointer" }}>
              <td>{m.from}</td>
              <td>{m.subject}</td>
              <td>{new Date(m.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {selected && (
        <div className="modal show d-block" tabIndex="-1" role="dialog">
          <div className="modal-dialog modal-lg" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">{selected.subject}</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setSelected(null)}
                ></button>
              </div>
              <div className="modal-body">
                <p>
                  <strong>From:</strong> {selected.from} <br />
                  <strong>To:</strong> {selected.to} <br />
                  <strong>Date:</strong> {new Date(selected.created_at).toLocaleString()}
                </p>
                <hr />
                <p>{selected.body}</p>
                {selected.attachments && selected.attachments.length > 0 && (
                  <>
                    <hr />
                    <h6>Attachments:</h6>
                    <ul>
                      {selected.attachments.map((a, i) => (
                        <li key={i}>
                          <a href={"/files" + a.url} target="_blank" rel="noreferrer">
                            {a.name}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
