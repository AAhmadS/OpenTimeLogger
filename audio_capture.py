"""Microphone capture for dictation (ASR). 16 kHz mono WAV, captured with sounddevice."""
import base64
import io
import queue
import threading
import time
import wave


class Recorder:
    def __init__(self):
        self._q = queue.Queue()
        self._stop = False
        self._thread = None
        self._started = 0.0
        self._frames = []

    def begin(self):
        import sounddevice as sd
        self._started = time.time()
        self._stop = False
        self._frames = []

        def _cb(indata, frames, t, status):
            if self._stop:
                raise sd.CallbackAbort
            self._q.put(bytes(indata))

        def _run():
            try:
                with sd.RawInputStream(samplerate=16000, channels=1,
                                       dtype="int16", blocksize=1600, callback=_cb):
                    while not self._stop:
                        try:
                            self._frames.append(self._q.get(timeout=0.2))
                        except queue.Empty:
                            continue
            except Exception:
                pass

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        return {"ok": True}

    def seconds(self):
        return round(time.time() - self._started, 1) if self._started else 0

    def stop(self):
        self._stop = True
        if self._thread:
            self._thread.join(timeout=1.5)
        data = b"".join(self._frames)
        if len(data) < 1600 * 2:  # < ~0.1s
            return None
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(data)
        return base64.b64encode(buf.getvalue()).decode("ascii")
