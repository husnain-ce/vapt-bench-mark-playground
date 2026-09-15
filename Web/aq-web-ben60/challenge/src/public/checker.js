async function main() {
  const params = new URLSearchParams(window.location.search);
  const url = params.get("url");
  if(url) {
    setTimeout(() => {
      somethingWentWrong();
    }, 8000);
    document.getElementById("div_url").style.visibility = 'visible';
    let url_cleaned = DOMPurify.sanitize(url);
    document.getElementById("msg_url").innerHTML = url_cleaned;
    const input = document.createElement("input");
    input.name = "url";
    input.type = "url";
    input.id = "input_url"
    input.required = true;
    input.value = url;
    const form = document.getElementById("scrap_form");
    form.appendChild(input);
    form.submit();
  } else {
    document.getElementById("div_url").remove();
    document.getElementById("error_url").remove();
    document.getElementById("input").innerHTML = '<input name="url" type="url" required placeholder="https://exemple.com" />';
  }
}

function somethingWentWrong() {
  let url = document.getElementById("msg_url").textContent;
  let error = document.getElementById("error_url");
  error.style.visibility = 'visible';
  error.innerHTML = `Something went wrong while scrapping ${url}`;
}

main();