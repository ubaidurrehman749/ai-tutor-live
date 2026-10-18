import json
import time
from datetime import datetime, timedelta, timezone

import streamlit as st
import streamlit.components.v1 as components
from google import genai

st.set_page_config(page_title="AI Tutor | Ubaid Ur Rehman", page_icon="🎓", layout="centered")

OWNER = "Ubaid Ur Rehman"
# Agar model ka error aaye to sirf ye naam badalna (AI Studio mein Live model ka naam dekho)
MODEL = "gemini-3.1-flash-live-preview"

PROMPT = """You are a friendly tutor on a live voice call with a student.
Listen carefully. If the student's answer is wrong, gently tell them, explain why, and give the correct answer.
Answer questions on any topic in a simple way.
Keep replies to 2-3 short sentences because this is a voice call.
Reply in the student's language (Urdu or English).
If you are not sure, say so clearly and do not guess."""

st.markdown(
    """
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: #f4f1ec; }
    .block-container { max-width: 620px; padding: 0.6rem 0.6rem 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def make_token():
    c = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"],
        http_options={"api_version": "v1alpha"},
    )
    now = datetime.now(timezone.utc)
    t = c.auth_tokens.create(
        config={
            "uses": 20,
            "expire_time": now + timedelta(minutes=30),
            "new_session_expire_time": now + timedelta(minutes=25),
            "http_options": {"api_version": "v1alpha"},
        }
    )
    return t.name


if "tok" not in st.session_state or time.time() - st.session_state.tok_time > 20 * 60:
    try:
        st.session_state.tok = make_token()
        st.session_state.tok_time = time.time()
    except Exception as e:
        st.error("Token error: " + str(e)[:300])
        st.stop()

HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: Georgia, 'Times New Roman', serif; background: #f4f1ec; color: #1c1917; }
  .hero { background: #1c1917; color: #fff; border-radius: 22px; padding: 22px 20px; box-shadow: 0 10px 26px rgba(0,0,0,.25); }
  .hero h1 { margin: 0 0 8px; font-size: 1.55rem; font-weight: 600; }
  .hero p { margin: 0; font-size: .9rem; color: #d6d3d1; line-height: 1.55; }
  .hero .by { display: inline-block; margin-top: 12px; padding: 5px 14px; border: 1px solid #57534e; border-radius: 999px; font-size: .8rem; color: #fafaf9; }
  .card { background: #fff; border: 1px solid #e7e5e4; border-radius: 22px; margin-top: 14px; padding: 26px 16px; text-align: center; }
  .circle { width: 96px; height: 96px; border-radius: 50%; background: #e7e5e4; margin: 0 auto 16px; display: flex; align-items: center; justify-content: center; transition: background .3s; }
  .circle svg { width: 38px; height: 38px; stroke: #78716c; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
  .circle.live { background: #dcfce7; animation: pulse 1.6s infinite; }
  .circle.live svg { stroke: #16a34a; }
  .circle.speak { background: #e0e7ff; animation: pulse 0.9s infinite; }
  .circle.speak svg { stroke: #4f46e5; }
  @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(99,102,241,.35); } 70% { box-shadow: 0 0 0 20px rgba(99,102,241,0); } 100% { box-shadow: 0 0 0 0 rgba(99,102,241,0); } }
  h3 { margin: 0 0 6px; font-size: 1.02rem; font-family: Arial, sans-serif; }
  .sub { margin: 0 0 18px; font-size: .8rem; color: #78716c; font-family: Arial, sans-serif; }
  button { font-family: Arial, sans-serif; font-weight: 600; font-size: .9rem; border: 0; border-radius: 12px; padding: 13px 26px; background: #1c1917; color: #fff; }
  button.end { background: #dc2626; }
  button:disabled { opacity: .6; }
  .err { margin-top: 12px; color: #b91c1c; font-size: .82rem; font-family: Arial, sans-serif; word-break: break-word; }
  #chat { margin-top: 14px; }
  .row { display: flex; margin: 8px 0; }
  .row.me { justify-content: flex-end; }
  .b { max-width: 86%; padding: 10px 14px; border-radius: 16px; font-size: .92rem; line-height: 1.6; font-family: Arial, sans-serif; }
  .me .b { background: #1c1917; color: #fff; border-bottom-right-radius: 4px; }
  .bot .b { background: #fff; border: 1px solid #e7e5e4; border-bottom-left-radius: 4px; }
  .foot { margin-top: 22px; text-align: center; font-size: .8rem; color: #78716c; font-family: Arial, sans-serif; padding-bottom: 10px; }
  .foot b { display: block; margin-top: 3px; font-size: .95rem; color: #1c1917; }
</style>
</head>
<body>
  <div class="hero">
    <h1>Live Voice Tutor</h1>
    <p>Have a continuous, real-time voice conversation with your AI tutor. No button clicking needed, and it handles interruptions.</p>
    <span class="by">Created by __OWNER__</span>
  </div>

  <div class="card">
    <div id="circle" class="circle">
      <svg viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>
    </div>
    <h3 id="title">Ready to connect to Live Voice Tutor</h3>
    <p class="sub" id="sub">Click Start to begin continuous voice conversation.</p>
    <button id="btn">Start Live Voice Session</button>
    <div class="err" id="err"></div>
  </div>

  <div id="chat"></div>

  <div class="foot">Made with ❤️ by <b>__OWNER__</b></div>

<script>
const TOKEN = __TOKEN__, MODEL = __MODEL__, PROMPT = __PROMPT__;
const $ = id => document.getElementById(id);
let ws, micCtx, playCtx, stream, proc, nextT = 0, sources = [];
let active = false, ready = false, curMe = null, curBot = null;

function setState(s) {
  const c = $('circle');
  c.className = 'circle' + (s === 'live' ? ' live' : s === 'speak' ? ' speak' : '');
  const btn = $('btn');
  if (s === 'idle') {
    $('title').textContent = 'Ready to connect to Live Voice Tutor';
    $('sub').textContent = 'Click Start to begin continuous voice conversation.';
    btn.textContent = 'Start Live Voice Session'; btn.className = ''; btn.disabled = false;
  } else if (s === 'connecting') {
    $('title').textContent = 'Connecting...';
    $('sub').textContent = 'Mic ki ijazat do (Allow).';
    btn.textContent = 'Please wait'; btn.disabled = true;
  } else if (s === 'live') {
    $('title').textContent = 'Listening... bolo!';
    $('sub').textContent = 'Beech mein bol sakte ho, tutor ruk jayega.';
    btn.textContent = 'End Session'; btn.className = 'end'; btn.disabled = false;
  } else if (s === 'speak') {
    $('title').textContent = 'Tutor bol raha hai...';
  }
}

function bubble(role, text) {
  const row = document.createElement('div');
  row.className = 'row ' + (role === 'me' ? 'me' : 'bot');
  const b = document.createElement('div');
  b.className = 'b'; b.dir = 'auto'; b.textContent = text;
  row.appendChild(b);
  $('chat').appendChild(row);
  return b;
}

function toB64(buf) {
  let s = ''; const u = new Uint8Array(buf);
  for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000));
  return btoa(s);
}

function playChunk(b64) {
  const bin = atob(b64); const n = bin.length >> 1;
  const f = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    let v = bin.charCodeAt(2 * i) | (bin.charCodeAt(2 * i + 1) << 8);
    if (v >= 0x8000) v -= 0x10000;
    f[i] = v / 32768;
  }
  const buf = playCtx.createBuffer(1, n, 24000);
  buf.copyToChannel(f, 0);
  const s = playCtx.createBufferSource();
  s.buffer = buf; s.connect(playCtx.destination);
  nextT = Math.max(nextT, playCtx.currentTime);
  s.start(nextT); nextT += buf.duration;
  sources.push(s);
  s.onended = () => { sources = sources.filter(x => x !== s); if (!sources.length && active) setState('live'); };
  setState('speak');
}

function stopPlayback() {
  sources.forEach(s => { try { s.stop(); } catch (e) {} });
  sources = []; nextT = 0;
}

function handle(m) {
  if (m.setupComplete) { ready = true; startMic(); setState('live'); return; }
  const sc = m.serverContent; if (!sc) return;
  if (sc.interrupted) { stopPlayback(); curBot = null; }
  if (sc.inputTranscription && sc.inputTranscription.text) {
    if (!curMe) curMe = bubble('me', '');
    curMe.textContent += sc.inputTranscription.text;
  }
  if (sc.modelTurn && sc.modelTurn.parts) {
    sc.modelTurn.parts.forEach(p => { if (p.inlineData && p.inlineData.data) playChunk(p.inlineData.data); });
  }
  if (sc.outputTranscription && sc.outputTranscription.text) {
    curMe = null;
    if (!curBot) curBot = bubble('bot', '');
    curBot.textContent += sc.outputTranscription.text;
  }
  if (sc.turnComplete) { curMe = null; curBot = null; }
}

function startMic() {
  const src = micCtx.createMediaStreamSource(stream);
  proc = micCtx.createScriptProcessor(4096, 1, 1);
  proc.onaudioprocess = e => {
    if (!ready || !ws || ws.readyState !== 1) return;
    const f = e.inputBuffer.getChannelData(0);
    const i16 = new Int16Array(f.length);
    for (let i = 0; i < f.length; i++) i16[i] = Math.max(-1, Math.min(1, f[i])) * 32767;
    ws.send(JSON.stringify({ realtimeInput: { audio: { data: toB64(i16.buffer), mimeType: 'audio/pcm;rate=16000' } } }));
  };
  src.connect(proc); proc.connect(micCtx.destination);
}

function stop() {
  active = false; ready = false;
  try { proc && proc.disconnect(); } catch (e) {}
  try { stream && stream.getTracks().forEach(t => t.stop()); } catch (e) {}
  try { micCtx && micCtx.close(); } catch (e) {}
  stopPlayback();
  try { playCtx && playCtx.close(); } catch (e) {}
  try { ws && ws.close(); } catch (e) {}
  setState('idle');
}

function fail(msg) { $('err').textContent = 'Error: ' + msg; stop(); }

async function start() {
  $('err').textContent = ''; setState('connecting'); active = true;
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 }
    });
    playCtx = new AudioContext({ sampleRate: 24000 });
    micCtx = new AudioContext({ sampleRate: 16000 });
    await playCtx.resume(); await micCtx.resume();
    ws = new WebSocket('wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContentConstrained?access_token=' + encodeURIComponent(TOKEN));
    ws.onopen = () => ws.send(JSON.stringify({ setup: {
      model: 'models/' + MODEL,
      generationConfig: { responseModalities: ['AUDIO'] },
      systemInstruction: { parts: [{ text: PROMPT }] },
      inputAudioTranscription: {}, outputAudioTranscription: {}
    } }));
    ws.onmessage = async e => {
      const t = typeof e.data === 'string' ? e.data : await e.data.text();
      handle(JSON.parse(t));
    };
    ws.onerror = () => {};
    ws.onclose = ev => {
      if (active) fail('Connection band hogaya (' + ev.code + ') ' + (ev.reason || ''));
    };
  } catch (err) { fail(err.message || String(err)); }
}

$('btn').onclick = () => { active ? stop() : start(); };
</script>
</body>
</html>
"""

html = (
    HTML.replace("__TOKEN__", json.dumps(st.session_state.tok))
    .replace("__MODEL__", json.dumps(MODEL))
    .replace("__PROMPT__", json.dumps(PROMPT))
    .replace("__OWNER__", OWNER)
)

components.html(html, height=900, scrolling=True)
