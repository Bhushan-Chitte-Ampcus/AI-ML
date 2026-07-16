/**
 * AI Voice Assistant — Frontend
 *
 * Features:
 *  - Welcome overlay: asks for user name, speaks personalised greeting
 *  - Animated particle background (bgCanvas)
 *  - Dual cyan/magenta sound wave visualizer (waveCanvas)
 *  - Glowing orb mic button with state-driven animations
 *  - Voice output via gTTS (/api/tts) — Indian English accent
 *  - Web Speech API for voice input (mic)
 *  - Multi-turn chat via /api/chat
 */

(() => {
  'use strict';

  // ── Config ───────────────────────────────────────────────────
  const API_CHAT_STREAM = '/api/chat/stream';
  const API_TTS   = (text) => `/api/tts?text=${encodeURIComponent(text)}`;
  const API_CLEAR = (id)   => `/api/session/${id}`;

  // ── State ────────────────────────────────────────────────────
  let sessionId    = crypto.randomUUID();
  let userName     = '';
  let isListening  = false;
  let isSpeaking   = false;
  let waveAmp      = 0;
  let waveTarget   = 0;
  let currentAudio = null;   // active <Audio> element — allows cancel

  // ── DOM refs ─────────────────────────────────────────────────
  const welcomeOverlay = document.getElementById('welcomeOverlay');
  const mainApp        = document.getElementById('mainApp');
  const nameInput      = document.getElementById('nameInput');
  const nameSubmitBtn  = document.getElementById('nameSubmitBtn');
  const userGreeting   = document.getElementById('userGreeting');
  const chatWindow     = document.getElementById('chatWindow');
  const textInput      = document.getElementById('textInput');
  const sendBtn        = document.getElementById('sendBtn');
  const micBtn         = document.getElementById('micBtn');
  const clearBtn       = document.getElementById('clearBtn');
  const autoSpeak      = document.getElementById('autoSpeak');
  const wakeWordToggle = document.getElementById('wakeWordToggle');
  const statusDot      = document.getElementById('statusDot');
  const statusText     = document.getElementById('statusText');
  const statusBar      = statusDot.parentElement;
  const waveCanvas     = document.getElementById('waveCanvas');
  const bgCanvas       = document.getElementById('bgCanvas');
  const wCtx           = waveCanvas.getContext('2d');
  const bCtx           = bgCanvas.getContext('2d');

  // ═══════════════════════════════════════════════════════════
  // BACKGROUND PARTICLE CANVAS
  // ═══════════════════════════════════════════════════════════
  const PARTICLE_COUNT = 80;
  const particles = [];

  function initParticles() {
    particles.length = 0;
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x:   Math.random() * bgCanvas.width,
        y:   Math.random() * bgCanvas.height,
        r:   Math.random() * 1.5 + 0.3,
        vx:  (Math.random() - .5) * .25,
        vy:  (Math.random() - .5) * .25,
        a:   Math.random(),
        hue: Math.random() > .5 ? 185 : 300,  // cyan or magenta
      });
    }
  }

  function resizeCanvases() {
    bgCanvas.width    = window.innerWidth;
    bgCanvas.height   = window.innerHeight;
    waveCanvas.width  = waveCanvas.offsetWidth;
    waveCanvas.height = waveCanvas.offsetHeight;
    initParticles();
  }

  function drawParticles() {
    bCtx.clearRect(0, 0, bgCanvas.width, bgCanvas.height);
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0)              p.x = bgCanvas.width;
      if (p.x > bgCanvas.width) p.x = 0;
      if (p.y < 0)               p.y = bgCanvas.height;
      if (p.y > bgCanvas.height) p.y = 0;
      p.a += (Math.random() - .5) * .02;
      p.a  = Math.max(.05, Math.min(.6, p.a));
      bCtx.beginPath();
      bCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      bCtx.fillStyle = `hsla(${p.hue}, 100%, 70%, ${p.a})`;
      bCtx.fill();
    });
    // Faint connecting lines between nearby particles
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx   = particles[i].x - particles[j].x;
        const dy   = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 90) {
          const alpha = (1 - dist / 90) * 0.12;
          const hue   = (particles[i].hue + particles[j].hue) / 2;
          bCtx.beginPath();
          bCtx.moveTo(particles[i].x, particles[i].y);
          bCtx.lineTo(particles[j].x, particles[j].y);
          bCtx.strokeStyle = `hsla(${hue}, 100%, 70%, ${alpha})`;
          bCtx.lineWidth   = 0.5;
          bCtx.stroke();
        }
      }
    }
  }

  // ═══════════════════════════════════════════════════════════
  // WAVE VISUALIZER CANVAS
  // ═══════════════════════════════════════════════════════════
  let wavePhase = 0;

  function drawWaves() {
    const W = waveCanvas.width;
    const H = waveCanvas.height;
    wCtx.clearRect(0, 0, W, H);

    waveAmp += (waveTarget - waveAmp) * 0.08;
    const amp  = H * 0.28 * waveAmp;
    const base = H / 2;

    const waves = [
      { color: '#00e5ff', phaseOffset: 0,        dir: -1 },
      { color: '#ff00c8', phaseOffset: Math.PI,   dir:  1 },
    ];

    waves.forEach(({ color, phaseOffset, dir }) => {
      wCtx.beginPath();
      wCtx.shadowBlur  = 18;
      wCtx.shadowColor = color;
      for (let x = 0; x <= W; x++) {
        const t   = (x / W) * Math.PI * 2;
        const env = Math.sin((x / W) * Math.PI);
        const y   = base
          + amp * env * Math.sin(t * 2.5 + wavePhase * dir + phaseOffset)
          + amp * .4  * env * Math.sin(t * 5 + wavePhase * dir * 1.3 + phaseOffset);
        x === 0 ? wCtx.moveTo(x, y) : wCtx.lineTo(x, y);
      }
      const grad = wCtx.createLinearGradient(0, 0, W, 0);
      if (dir === -1) {
        grad.addColorStop(0,   color);
        grad.addColorStop(0.5, color + '88');
        grad.addColorStop(1,   color + '00');
      } else {
        grad.addColorStop(0,   color + '00');
        grad.addColorStop(0.5, color + '88');
        grad.addColorStop(1,   color);
      }
      wCtx.strokeStyle = grad;
      wCtx.lineWidth   = 2.5;
      wCtx.stroke();
      wCtx.shadowBlur  = 0;
    });

    // Particle spray near the orb center
    if (waveAmp > 0.1) {
      const cx    = W / 2;
      const spray = 12 + waveAmp * 20;
      for (let i = 0; i < 6; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r  = spray * (0.5 + Math.random());
        const px = cx + Math.cos(angle) * r;
        const py = base + Math.sin(angle) * r * 0.4;
        const hue = Math.random() > .5 ? '#00e5ff' : '#ff00c8';
        wCtx.beginPath();
        wCtx.arc(px, py, Math.random() * 1.5 + 0.3, 0, Math.PI * 2);
        wCtx.fillStyle = hue + 'cc';
        wCtx.fill();
      }
    }

    wavePhase += isListening ? 0.06 : isSpeaking ? 0.05 : 0.015;
  }

  // ═══════════════════════════════════════════════════════════
  // ANIMATION LOOP
  // ═══════════════════════════════════════════════════════════
  function animate() {
    drawParticles();
    drawWaves();
    requestAnimationFrame(animate);
  }

  // ═══════════════════════════════════════════════════════════
  // STATUS / ORB HELPERS
  // ═══════════════════════════════════════════════════════════
  function setStatus(text, state = '') {
    statusText.textContent = text;
    statusBar.className    = 'status-bar ' + state;
  }

  function setOrbState(state) {
    micBtn.classList.remove('listening', 'speaking');
    if (state) micBtn.classList.add(state);
  }

  // ═══════════════════════════════════════════════════════════
  // VOICE OUTPUT — gTTS via /api/tts
  // ═══════════════════════════════════════════════════════════
  function stopAudio() {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.src = '';
      currentAudio     = null;
    }
    isSpeaking = false;
    waveTarget = 0;
    setOrbState('');
    // Restore correct status depending on wake mode
    if (wakeActive) {
      micBtn.classList.add('wake-standby');
      setStatus("Listening for 'Hey CortexAI'…", 'wake');
    } else {
      setStatus('Click the orb to speak');
    }
  }

  function speak(text, onDone) {
    if (!autoSpeak.checked) { onDone?.(); return; }

    stopAudio();  // cancel any in-progress speech

    isSpeaking = true;
    waveTarget = 0.85;
    setOrbState('speaking');
    setStatus('Speaking…', 'speaking');

    const audio  = new Audio(API_TTS(text));
    currentAudio = audio;

    audio.onended = () => { stopAudio(); onDone?.(); };
    audio.onerror = () => {
      stopAudio();
      setStatus('TTS error — is the server running?', 'error');
      onDone?.();
    };

    audio.play().catch(() => {
      // Autoplay policy blocked playback — degrade gracefully
      stopAudio();
      onDone?.();
    });
  }

  // ═══════════════════════════════════════════════════════════
  // WELCOME OVERLAY — NAME GATE
  // ═══════════════════════════════════════════════════════════
  function submitName() {
    const raw = nameInput.value.trim();
    if (!raw) {
      nameInput.classList.add('shake');
      nameInput.addEventListener('animationend', () => nameInput.classList.remove('shake'), { once: true });
      return;
    }

    userName = raw.charAt(0).toUpperCase() + raw.slice(1);
    userGreeting.textContent = `Hello, ${userName}`;

    welcomeOverlay.classList.add('hiding');
    welcomeOverlay.addEventListener('animationend', () => {
      welcomeOverlay.style.display = 'none';
      mainApp.style.display        = 'flex';
      resizeCanvases();

      const welcomeMsg = `Welcome to CortexAI, ${userName}!`;
      appendMessage('assistant', welcomeMsg);
      setTimeout(() => speak(welcomeMsg), 200);
      textInput.focus();
    }, { once: true });
  }

  nameSubmitBtn.addEventListener('click', submitName);
  nameInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') submitName();
  });

  // ═══════════════════════════════════════════════════════════
  // SPEECH RECOGNITION — wake word + command (two-stage)
  //
  // Stage 1 — wakeRecognition: continuous, low-footprint listener.
  //   Runs whenever "Hey CortexAI" toggle is ON.
  //   Only looks for wake phrases; ignores everything else.
  //
  // Stage 2 — recognition: single-shot command capture.
  //   Fires automatically after wake word detected, OR manually
  //   when the user clicks the orb.
  // ═══════════════════════════════════════════════════════════
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  // Wake phrases — any of these triggers command mode
  const WAKE_PHRASES = ['hey cortexai', 'hey cortex ai', 'cortex ai', 'hey cortex'];

  let recognition     = null;   // command recogniser (single-shot)
  let wakeRecognition = null;   // wake-word recogniser (continuous)
  let wakeActive      = false;  // is continuous listening running?
  let commandPending  = false;  // prevents double-trigger

  function _containsWakePhrase(text) {
    const t = text.toLowerCase();
    return WAKE_PHRASES.some(p => t.includes(p));
  }

  // ── Command recogniser (single-shot) ───────────────────────
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous     = false;
    recognition.interimResults = true;
    recognition.lang           = 'en-US';

    recognition.onstart = () => {
      isListening = true;
      waveTarget  = 0.7;
      setOrbState('listening');
      setStatus('Listening…', 'listening');
    };
    recognition.onresult = (e) => {
      const transcript = Array.from(e.results).map(r => r[0].transcript).join('');
      textInput.value  = transcript;
      waveTarget       = Math.min(1, 0.6 + e.results.length * 0.05);
    };
    recognition.onend = () => {
      isListening    = false;
      commandPending = false;
      waveTarget     = 0;
      setOrbState('');
      // Restore status based on wake mode
      if (wakeActive) {
        setStatus("Listening for 'Hey CortexAI'…", 'wake');
      } else {
        setStatus('Click the orb to speak');
      }
      if (textInput.value.trim()) sendMessage();
      // Resume wake listener if toggle is still on
      if (wakeActive) _startWakeListener();
    };
    recognition.onerror = (e) => {
      isListening    = false;
      commandPending = false;
      waveTarget     = 0;
      setOrbState('');
      if (e.error !== 'no-speech') {
        setStatus(`Mic error: ${e.error}`, 'error');
      } else if (wakeActive) {
        setStatus("Listening for 'Hey CortexAI'…", 'wake');
        _startWakeListener();
      } else {
        setStatus('Click the orb to speak');
      }
    };
  } else {
    micBtn.style.cursor = 'not-allowed';
    micBtn.title        = 'Speech recognition not supported. Use Chrome or Edge.';
    setStatus('Voice input unavailable — use Chrome or Edge', 'error');
  }

  // ── Wake-word recogniser (continuous) ──────────────────────
  function _buildWakeRecognition() {
    if (!SpeechRecognition) return null;
    const wr          = new SpeechRecognition();
    wr.continuous     = true;
    wr.interimResults = true;
    wr.lang           = 'en-US';

    wr.onresult = (e) => {
      if (commandPending) return;
      const last  = e.results[e.results.length - 1];
      const heard = last[0].transcript.toLowerCase();
      if (_containsWakePhrase(heard)) {
        commandPending = true;
        _triggerCommandMode();
      }
    };
    wr.onend = () => {
      // Continuous recognition stops itself in some browsers — restart it
      if (wakeActive && !isListening) {
        setTimeout(() => { if (wakeActive && !isListening) wr.start(); }, 300);
      }
    };
    wr.onerror = (e) => {
      if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
        wakeActive = false;
        wakeWordToggle.checked = false;
        setStatus('Microphone permission denied', 'error');
      }
    };
    return wr;
  }

  function _startWakeListener() {
    if (!wakeActive || isListening) return;
    if (!wakeRecognition) wakeRecognition = _buildWakeRecognition();
    try { wakeRecognition.start(); } catch (_) { /* already running */ }
    micBtn.classList.add('wake-standby');
    setStatus("Listening for 'Hey CortexAI'…", 'wake');
  }

  function _stopWakeListener() {
    wakeActive = false;
    try { wakeRecognition?.stop(); } catch (_) {}
    micBtn.classList.remove('wake-standby');
    setStatus('Click the orb to speak');
  }

  function _triggerCommandMode() {
    // Stop wake listener, start command capture
    try { wakeRecognition?.stop(); } catch (_) {}
    micBtn.classList.remove('wake-standby');
    stopAudio();    // stop TTS before listening

    // Brief visual feedback that wake word was heard
    setStatus('Wake word detected — speak now!', 'listening');
    waveTarget = 0.5;

    setTimeout(() => {
      if (!isListening) {
        try { recognition.start(); } catch (_) {}
      }
    }, 250);
  }

  // ── Wake word toggle ────────────────────────────────────────
  wakeWordToggle.addEventListener('change', () => {
    if (wakeWordToggle.checked) {
      wakeActive = true;
      // Rebuild recogniser so it starts fresh
      wakeRecognition = _buildWakeRecognition();
      _startWakeListener();
    } else {
      _stopWakeListener();
    }
  });

  // ═══════════════════════════════════════════════════════════
  // CHAT UI HELPERS
  // ═══════════════════════════════════════════════════════════
  function appendMessage(role, text) {
    const wrap   = document.createElement('div');
    wrap.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className   = 'msg-avatar';
    avatar.textContent = role === 'assistant' ? 'AI' : (userName ? userName[0].toUpperCase() : 'U');

    const bubble = document.createElement('div');
    bubble.className   = 'bubble';
    bubble.textContent = text;

    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    chatWindow.appendChild(wrap);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return bubble;
  }

  function setBusy(busy) {
    sendBtn.disabled   = busy;
    textInput.disabled = busy;
    if (!busy) textInput.focus();
  }

  // ═══════════════════════════════════════════════════════════
  // SEND MESSAGE  — SSE streaming
  // ═══════════════════════════════════════════════════════════
  async function sendMessage() {
    const text = textInput.value.trim();
    if (!text) return;

    textInput.value = '';
    appendMessage('user', text);
    setBusy(true);
    waveTarget = 0.3;

    // Create the assistant bubble immediately — tokens stream into it
    const wrap   = document.createElement('div');
    wrap.className = 'message assistant';
    const avatar = document.createElement('div');
    avatar.className   = 'msg-avatar';
    avatar.textContent = 'AI';
    const bubble = document.createElement('div');
    bubble.className = 'bubble streaming';
    bubble.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
    chatWindow.appendChild(wrap);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    let fullText    = '';
    let firstToken  = true;

    try {
      const res = await fetch(API_CHAT_STREAM, {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error ${res.status}`);
      }

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let   buffer  = '';

      // Read the SSE stream line by line
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();           // keep incomplete last line

        for (const line of lines) {
          if (!line.startsWith('data:')) continue;
          const raw = line.slice(5).trim();
          if (!raw) continue;

          let evt;
          try { evt = JSON.parse(raw); } catch { continue; }

          if (evt.type === 'token') {
            if (firstToken) {
              bubble.textContent = '';  // clear the typing dots
              bubble.classList.remove('streaming');
              firstToken = false;
            }
            fullText += evt.text;
            bubble.textContent = fullText;
            chatWindow.scrollTop = chatWindow.scrollHeight;
            // Gentle wave pulse while tokens arrive
            waveTarget = 0.35;

          } else if (evt.type === 'done') {
            fullText = evt.text || fullText;
            bubble.textContent = fullText;
            chatWindow.scrollTop = chatWindow.scrollHeight;
            speak(fullText);

          } else if (evt.type === 'error') {
            bubble.textContent = `⚠️ ${evt.text}`;
            setStatus(evt.text, 'error');
            waveTarget = 0;
          }
        }
      }

    } catch (err) {
      bubble.textContent = `⚠️ ${err.message}`;
      setStatus(err.message, 'error');
      waveTarget = 0;
    } finally {
      bubble.classList.remove('streaming');
      if (!isSpeaking) waveTarget = 0;
      setBusy(false);
    }
  }

  // ═══════════════════════════════════════════════════════════
  // EVENT LISTENERS
  // ═══════════════════════════════════════════════════════════
  sendBtn.addEventListener('click', sendMessage);

  textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  micBtn.addEventListener('click', () => {
    if (!recognition) return;
    if (isListening) {
      recognition.stop();
    } else {
      stopAudio();          // stop TTS before listening
      // Pause wake listener while command runs (it resumes in recognition.onend)
      try { wakeRecognition?.stop(); } catch (_) {}
      micBtn.classList.remove('wake-standby');
      try { recognition.start(); } catch (_) {}
    }
  });

  clearBtn.addEventListener('click', async () => {
    await fetch(API_CLEAR(sessionId), { method: 'DELETE' }).catch(() => {});
    sessionId = crypto.randomUUID();
    chatWindow.innerHTML = '';
    const msg = `Session cleared. Ready for you, ${userName}.`;
    appendMessage('assistant', msg);
    speak(msg);
    waveTarget = 0.4;
    setTimeout(() => { if (!isSpeaking) waveTarget = 0; }, 1200);
  });

  window.addEventListener('resize', resizeCanvases);

  // ═══════════════════════════════════════════════════════════
  // INIT
  // ═══════════════════════════════════════════════════════════
  resizeCanvases();
  animate();
  nameInput.focus();

  // Gentle idle pulse to keep the visualizer alive
  setInterval(() => {
    if (!isListening && !isSpeaking && waveTarget === 0) {
      waveTarget = 0.18;
      setTimeout(() => { if (!isListening && !isSpeaking) waveTarget = 0; }, 800);
    }
  }, 4000);

})();
