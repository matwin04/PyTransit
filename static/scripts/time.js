function formatDepartureTimes() {
  const elements = document.querySelectorAll('.departure-time');
  elements.forEach(el => {
    const timeStr = el.dataset.utc; // e.g., "2025-07-11T15:00:00Z"
    if (!timeStr) return;

    const date = new Date(timeStr);
    const options = {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      month: 'numeric',
      day: 'numeric',
      year: '2-digit',
    };
    el.textContent = date.toLocaleString(undefined, options);
  });
}

document.addEventListener("DOMContentLoaded", formatDepartureTimes);