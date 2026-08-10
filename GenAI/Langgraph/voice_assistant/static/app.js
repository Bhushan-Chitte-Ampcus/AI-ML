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
    // Status restored by the caller (_afterTTS or wake mode)
  }

  // Called every time TTS finishes (or is skipped).
  // Decides what to do next: auto-listen or return to standby.
  // afterWelcome=true forces auto-listen even if wake mode is off.
  function _afterTTS(afterWelcome = false) {
    // Auto-start listening if wake mode is ON, or right after the welcome greeting
    if ((wakeActive || afterWelcome) && SpeechRecognition) {
      setTimeout(() => {
        if (!isListening && !isSpeaking) {
          _startManualCommand();
        }
      }, 350);
      return;
    }
    // Wake mode OFF and not welcome — restore idle status
    setStatus('Click the orb to speak');
  }

  function speak(text, onDone) {
    if (!autoSpeak.checked) {
      // Auto-speak is off — still trigger auto-listen if wake mode is on
      _afterTTS();
      onDone?.();
      return;
    }

    stopAudio();  // cancel any in-progress speech

    isSpeaking = true;
    waveTarget = 0.85;
    setOrbState('speaking');
    setStatus('Speaking…', 'speaking');

    const audio  = new Audio(API_TTS(text));
    currentAudio = audio;

    audio.onended = () => {
      stopAudio();
      _afterTTS();
      onDone?.();
    };
    audio.onerror = () => {
      stopAudio();
      setStatus('TTS error — is the server running?', 'error');
      onDone?.();
    };

    audio.play().catch(() => {
      stopAudio();
      _afterTTS();
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

      const welcomeMsg = `Welcome to CortexAI, ${userName}! How can I assist you today?`;
      appendMessage('assistant', welcomeMsg);
      setTimeout(() => speak(welcomeMsg, () => _afterTTS(true)), 200);
      textInput.focus();
    }, { once: true });
  }

  nameSubmitBtn.addEventListener('click', submitName);
  nameInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') submitName();
  });

  // ═══════════════════════════════════════════════════════════
  // SPEECH RECOGNITION — unified single-instance approach
  //
  // One continuous SpeechRecognition instance handles everything:
  //
  //  STANDBY mode  (wakeActive=true, mode='standby')
  //    → runs continuously, silently filters for wake phrases
  //    → on wake phrase → switches to COMMAND mode instantly
  //
  //  COMMAND mode  (mode='command')
  //    → captures the full user query (strips the wake phrase prefix)
  //    → on silence/end → sends message, returns to STANDBY
  //
  //  MANUAL mode   (mode='command', triggered by orb click)
  //    → same as COMMAND but without wake phrase stripping
  //
  // Single instance = no restart gap, no two-instance race conditions.
  // Chrome auto-stop on silence is handled by restarting in onend.
  // ═══════════════════════════════════════════════════════════

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  // Accepted wake phrases (fuzzy — Chrome mishears proper nouns)
  const WAKE_PHRASES = [
    'hey cortex', 'hey cortexai', 'hey cortex ai',
    'cortex ai',  'ok cortex',    'okay cortex',
    'hi cortex',  'hello cortex',
  ];

  // How long (ms) to wait after wake phrase before treating new speech as command
  const WAKE_CAPTURE_DELAY = 400;

  let wakeActive    = false;  // is wake-word mode enabled
  let srMode        = 'idle'; // 'idle' | 'standby' | 'command'
  let sr            = null;   // single SpeechRecognition instance
  let srRunning     = false;  // Chrome state tracking
  let srRestartTimer = null;
  let wakeDetectedAt = 0;     // timestamp when wake phrase was last heard
  let capturedQuery  = '';    // accumulates command after wake phrase

  function _containsWakePhrase(text) {
    const t = text.toLowerCase().trim();
    return WAKE_PHRASES.some(p => t.includes(p));
  }

  function _stripWakePhrase(text) {
    // Remove the wake phrase from the front so it isn't sent to the LLM
    let t = text.toLowerCase().trim();
    let result = text.trim();
    for (const phrase of WAKE_PHRASES) {
      const idx = t.indexOf(phrase);
      if (idx !== -1) {
        result = text.slice(idx + phrase.length).trim();
        // Remove leading punctuation/comma
        result = result.replace(/^[,.\s]+/, '').trim();
        break;
      }
    }
    return result;
  }

  function _buildSR() {
    if (!SpeechRecognition) return null;
    const r       = new SpeechRecognition();
    r.continuous     = true;
    r.interimResults = true;
    r.lang           = 'en-US';
    r.maxAlternatives = 3;      // more alternatives = better wake phrase matching

    r.onstart = () => { srRunning = true; };

    r.onresult = (e) => {
      for (let i = e.resultIndex; i < e.results.length; i++) {
        // Collect all alternatives for better wake phrase coverage
        let heard = '';
        for (let a = 0; a < e.results[i].length; a++) {
          heard += ' ' + e.results[i][a].transcript;
        }
        heard = heard.toLowerCase().trim();
        const isFinal = e.results[i].isFinal;

        // ── STANDBY: watching for wake phrase ──────────────
        if (srMode === 'standby') {
          if (_containsWakePhrase(heard)) {
            wakeDetectedAt = Date.now();
            capturedQuery  = _stripWakePhrase(e.results[i][0].transcript);
            _enterCommandMode();
          }
          continue;
        }

        // ── COMMAND: capturing the user's query ─────────────
        if (srMode === 'command') {
          const raw = e.results[i][0].transcript;

          // If wake phrase is in same utterance, strip it
          const stripped = _containsWakePhrase(raw.toLowerCase())
            ? _stripWakePhrase(raw)
            : raw;

          if (isFinal) {
            capturedQuery = stripped.trim();
            // Finalise immediately on final result
            _finaliseCommand();
          } else {
            // Show interim transcript in the text box
            textInput.value = stripped.trim();
            waveTarget = Math.min(1, 0.65 + i * 0.05);
          }
        }
      }
    };

    r.onend = () => {
      srRunning = false;
      if (srMode === 'command') {
        // Silence timeout — treat whatever we have as the final command
        _finaliseCommand();
        return;
      }
      // Standby: Chrome stopped on silence — restart
      if (srMode === 'standby') {
        clearTimeout(srRestartTimer);
        srRestartTimer = setTimeout(_restartSR, 500);
      }
    };

    r.onerror = (e) => {
      srRunning = false;
      if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
        wakeActive             = false;
        wakeWordToggle.checked = false;
        srMode = 'idle';
        micBtn.classList.remove('wake-standby');
        setStatus('Microphone access denied — check browser settings', 'error');
        return;
      }
      if (e.error === 'no-speech' || e.error === 'network' || e.error === 'aborted') {
        if (srMode === 'command') {
          _finaliseCommand();
          return;
        }
        if (srMode === 'standby') {
          clearTimeout(srRestartTimer);
          srRestartTimer = setTimeout(_restartSR, 600);
        }
      }
    };

    return r;
  }

  function _restartSR() {
    if (srMode !== 'standby' || srRunning) return;
    sr = _buildSR();
    try {
      sr.start();
      _setStandbyUI();
    } catch (_) {
      srRestartTimer = setTimeout(_restartSR, 1000);
    }
  }

  function _enterCommandMode() {
    srMode = 'command';
    isListening = true;
    waveTarget  = 0.75;
    setOrbState('listening');
    setStatus('Listening for your command…', 'listening');
    // Brief flash on the orb to confirm wake word heard
    micBtn.classList.add('wake-triggered');
    setTimeout(() => micBtn.classList.remove('wake-triggered'), 600);
  }

  function _finaliseCommand() {
    if (srMode !== 'command') return;
    const query = capturedQuery || textInput.value.trim();
    capturedQuery = '';
    textInput.value = '';
    isListening = false;
    waveTarget  = 0;
    setOrbState('');

    if (query) {
      textInput.value = query;
      sendMessage();
      // _afterTTS() will auto-restart listening once TTS completes
    }

    // Go back to standby (not command) — auto-listen will be triggered by _afterTTS
    if (wakeActive) {
      srMode = 'standby';
      // Keep the SR instance running in standby so it can wake again if needed
      clearTimeout(srRestartTimer);
      srRestartTimer = setTimeout(() => {
        if (srMode === 'standby' && !isSpeaking) {
          sr = _buildSR();
          try { sr.start(); } catch (_) {}
          _setStandbyUI();
        }
      }, 800);
    } else {
      srMode = 'idle';
      setStatus('Click the orb to speak');
    }
  }

  function _setStandbyUI() {
    micBtn.classList.add('wake-standby');
    setStatus("Say 'Hey CortexAI' or wait after my reply…", 'wake');
  }

  // ── Manual orb click ───────────────────────────────────────
  function _startManualCommand() {
    stopAudio();
    capturedQuery = '';
    textInput.value = '';

    if (srMode === 'standby') {
      // Reuse running instance — just switch mode
      srMode = 'command';
      micBtn.classList.remove('wake-standby');
      isListening = true;
      waveTarget  = 0.7;
      setOrbState('listening');
      setStatus('Listening…', 'listening');
      return;
    }

    // Not running — start fresh
    srMode = 'command';
    clearTimeout(srRestartTimer);
    if (!sr) sr = _buildSR();
    try {
      sr.start();
      isListening = true;
      waveTarget  = 0.7;
      setOrbState('listening');
      setStatus('Listening…', 'listening');
    } catch (_) {
      // Already running — just update mode
      isListening = true;
      waveTarget  = 0.7;
      setOrbState('listening');
      setStatus('Listening…', 'listening');
    }
  }

  function _stopManualCommand() {
    capturedQuery = '';
    textInput.value = '';
    isListening = false;
    waveTarget  = 0;
    setOrbState('');
    try { sr?.stop(); } catch (_) {}
    if (wakeActive) {
      srMode = 'standby';
      srRestartTimer = setTimeout(_restartSR, 500);
    } else {
      srMode = 'idle';
      setStatus('Click the orb to speak');
    }
  }

  // ── Wake word toggle ───────────────────────────────────────
  wakeWordToggle.addEventListener('change', () => {
    if (wakeWordToggle.checked) {
      if (!SpeechRecognition) {
        wakeWordToggle.checked = false;
        setStatus('Speech recognition not supported — use Chrome or Edge', 'error');
        return;
      }
      wakeActive = true;
      srMode     = 'standby';
      clearTimeout(srRestartTimer);
      sr = _buildSR();
      try {
        sr.start();
        _setStandbyUI();
      } catch (_) {
        srRestartTimer = setTimeout(_restartSR, 500);
      }
    } else {
      wakeActive = false;
      clearTimeout(srRestartTimer);
      srRunning = false;
      try { sr?.stop(); } catch (_) {}
      sr     = null;
      srMode = 'idle';
      micBtn.classList.remove('wake-standby', 'wake-triggered');
      isListening = false;
      waveTarget  = 0;
      setOrbState('');
      setStatus('Click the orb to speak');
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
    if (!SpeechRecognition) return;
    if (srMode === 'command' && isListening) {
      _stopManualCommand();
    } else {
      _startManualCommand();
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
