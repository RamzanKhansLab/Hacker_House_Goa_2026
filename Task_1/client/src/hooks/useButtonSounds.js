import { useEffect, useRef } from "react";

function playClick(context) {
  const now = context.currentTime;
  const oscillator = context.createOscillator();
  const gain = context.createGain();

  oscillator.type = "square";
  oscillator.frequency.setValueAtTime(530, now);
  oscillator.frequency.exponentialRampToValueAtTime(760, now + 0.045);
  gain.gain.setValueAtTime(0.045, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + 0.07);
  oscillator.connect(gain).connect(context.destination);
  oscillator.start(now);
  oscillator.stop(now + 0.075);
}

export function useButtonSounds() {
  const audioContextRef = useRef(null);

  useEffect(() => {
    const onClick = (event) => {
      const button = event.target.closest("button:not(:disabled)");
      if (!button || !window.AudioContext) return;

      const context = audioContextRef.current || new window.AudioContext();
      audioContextRef.current = context;
      if (context.state === "suspended") context.resume();
      playClick(context);
    };

    document.addEventListener("click", onClick);
    return () => {
      document.removeEventListener("click", onClick);
      audioContextRef.current?.close();
    };
  }, []);
}
