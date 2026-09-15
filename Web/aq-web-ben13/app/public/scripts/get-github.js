document.forms[0].addEventListener("submit", async function (e) {
  e.preventDefault();
  const formData = new FormData(this);
  const url = formData.get("url") || "";

  const res = await fetch("/get-github", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    alert("Error fetching data: " + res.statusText);
    return;
  }

  const data = await res.text();
  document.getElementById("result").textContent = data;
});
