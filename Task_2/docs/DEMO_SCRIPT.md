# End-to-end demo script

1. Show `/ready` and explain that demo mode is labelled, with no hidden provider key.
2. Ask “What is retrieval augmented generation?” by text; point out answer, source, `PASS`, and RAG latency.
3. Record a short voice question; show transcript, STT latency, RAG latency, and end-to-end latency separately.
4. Ask `RAG क्या है?`; show language detection/source metadata.
5. Ask an off-topic question; explain the `INSUFFICIENT_CONTEXT` refusal.
6. Ask an unsafe request and an instruction-override request; show that neither reaches generation.
7. Open the benchmark report generated on the current machine, stating its dataset/index/model context.

For live voice, configure Sarvam and repeat step 3 with a <=30 second WAV/MP3/WebM recording.
