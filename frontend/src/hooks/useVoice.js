/**
 * useVoice — Custom hook for the full voice pipeline
 * Records → sends to backend → plays back response audio
 */
import { useState, useRef } from "react";

export default function useVoice({
  apiUrl,
  mode,
  subject,
  sessionId,
  pendingQuiz,
  language = "en",
  onResult,
}) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const currentAudioRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunksRef.current = [];

      const mimeType = getSupportedMimeType();
      const mediaRecorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(100);
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied:", err);
      alert("Microphone access is required. Please allow it in your browser settings.");
    }
  };

  const stopRecording = () => {
    const mr = mediaRecorderRef.current;
    if (!mr || mr.state === "inactive") return;

    mr.onstop = async () => {
      setIsRecording(false);

      const mimeType = mr.mimeType || "audio/webm";
      const blob = new Blob(chunksRef.current, { type: mimeType });

      if (blob.size < 1000) {
        setIsProcessing(false);
        return;
      }

      setIsProcessing(true);
      try {
        let result;
        if (pendingQuiz && mode === "quiz") {
          result = await callEvaluate(blob);
        } else {
          result = await callVoice(blob);
        }

        if (result.audioUrl) {
          if (currentAudioRef.current) currentAudioRef.current.pause();
          const audio = new Audio(result.audioUrl);
          currentAudioRef.current = audio;
          audio.play().catch(console.warn);
        }

        onResult(result);
      } catch (err) {
        console.error("Voice pipeline error:", err);
        onResult({
          transcript: "[Error]",
          response: "Sorry, something went wrong. Please check your API keys and try again.",
          audioUrl: null,
          error: true,
        });
      } finally {
        setIsProcessing(false);
      }

      mr.stream.getTracks().forEach((t) => t.stop());
    };

    mr.stop();
  };

  async function callVoice(audioBlob) {
    const fd = new FormData();
    fd.append("audio", audioBlob, "recording.webm");
    fd.append("mode", mode);
    fd.append("subject", subject);
    fd.append("session_id", sessionId);
    fd.append("language", language);

    const res = await fetch(`${apiUrl}/voice`, { method: "POST", body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    return { ...data, audioUrl: data.audio_b64 ? b64ToUrl(data.audio_b64) : null, evaluationMode: false };
  }

  async function callEvaluate(audioBlob) {
    const fd = new FormData();
    fd.append("audio", audioBlob, "recording.webm");
    fd.append("question", pendingQuiz.question);
    fd.append("expected_answer", pendingQuiz.expectedAnswer);
    fd.append("subject", subject);
    fd.append("session_id", sessionId);
    fd.append("language", language);

    const res = await fetch(`${apiUrl}/quiz/evaluate`, { method: "POST", body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    return {
      transcript: data.student_answer,
      response: data.feedback,
      quiz_question: null,
      is_correct: data.is_correct,
      is_struggling: data.is_struggling,
      score: data.score,
      audioUrl: data.audio_b64 ? b64ToUrl(data.audio_b64) : null,
      evaluationMode: true,
    };
  }

  function b64ToUrl(b64, type = "audio/mpeg") {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return URL.createObjectURL(new Blob([bytes], { type }));
  }

  function getSupportedMimeType() {
    const types = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"];
    return types.find((t) => MediaRecorder.isTypeSupported(t)) || "";
  }

  return { isRecording, isProcessing, startRecording, stopRecording };
}
