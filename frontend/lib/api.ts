export async function fetchAlerts() {
  const res = await fetch("http://localhost:8000/api/alerts");
  return res.json();
}