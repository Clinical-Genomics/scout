// Function used to refresh login token before submitting a request to chanjo2
async function refreshAndSubmit(form, refreshUrl) {
  const res = await fetch(refreshUrl, { method: "POST" });
  const data = await res.json();
  if (!data.id_token) {
    console.log("Could not retrieve login token.")
  }
  form.querySelector('input[name="id_token"]').value = data.id_token || "";
  form.submit();
}
