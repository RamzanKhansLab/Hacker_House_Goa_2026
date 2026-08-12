import { useCallback, useState } from "react";
import { SHARE_CAPTION } from "../constants";
import { createShareLink } from "../services/shareService";

function xIntent(url) {
  return `https://x.com/intent/post?text=${encodeURIComponent(SHARE_CAPTION)}&url=${encodeURIComponent(url)}`;
}

export function useShare() {
  const [sharing, setSharing] = useState(false);
  const [shareMessage, setShareMessage] = useState("");

  const share = useCallback(async ({ getBlob, format }) => {
    setSharing(true);
    setShareMessage("");
    let xWindow = null;

    try {
      const blob = await getBlob();
      const filename = format === "id-card" ? "hh-goa-2026-builder.png" : "hh-goa-2026-pfp.png";
      const file = new File([blob], filename, { type: "image/png" });
      const shareData = { title: "Hacker House Goa 2026", text: SHARE_CAPTION, files: [file] };

      if (navigator.share && (!navigator.canShare || navigator.canShare(shareData))) {
        try {
          await navigator.share(shareData);
          setShareMessage("Your graphic is ready to share.");
          return { method: "native" };
        } catch (error) {
          if (error?.name === "AbortError") return { method: "cancelled" };
          // Some browsers expose share but reject file payloads; use the link fallback.
        }
      }

      // Open this synchronously with the user gesture so desktop popup blockers do not
      // discard the X intent while the image link is being prepared.
      xWindow = window.open("about:blank", "_blank");
      if (xWindow) xWindow.opener = null;
      const shareRecord = await createShareLink({ blob, format });
      const intent = xIntent(shareRecord.url);
      if (xWindow) xWindow.location.replace(intent);
      else window.location.assign(intent);
      setShareMessage("Your X post is ready — you can edit it before posting.");
      return { method: "x", url: shareRecord.url };
    } catch (error) {
      if (xWindow && !xWindow.closed) xWindow.close();
      setShareMessage("Your graphic is ready. Download it and share manually.");
      throw error;
    } finally {
      setSharing(false);
    }
  }, []);

  return { sharing, shareMessage, share };
}
