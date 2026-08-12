function apiUrl(path) {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "";
  return `${baseUrl}${path}`;
}

function blobToDataUrl(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("SHARE_ENCODE_FAILED"));
    reader.readAsDataURL(blob);
  });
}

export async function createShareLink({ blob, format }) {
  const imageDataUrl = await blobToDataUrl(blob);
  const response = await fetch(apiUrl("/api/share"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ imageDataUrl, format }),
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.message || "SHARE_PREPARATION_FAILED");
  }
  return body;
}
