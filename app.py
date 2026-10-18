import json
import time
from datetime import datetime, timedelta, timezone

import streamlit as st
import streamlit.components.v1 as components
from google import genai

st.set_page_config(page_title="AI English Coach | Ubaid Ur Rehman", page_icon="🎓", layout="centered")

OWNER = "Ubaid Ur Rehman"
# Model ka error aaye to sirf ye naam badalna
MODEL = "gemini-3.1-flash-live-preview"

st.markdown(
    """
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: #f4f1ec; }
    .block-container { max-width: 620px; padding: 0.5rem 0.5rem 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def make_token():
    c = genai.Client(api_key=st.secrets["GEMINI_API_KEY"], http_options={"api_version": "v1alpha"})
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
  body { margin: 0; font-family: Arial, sans-serif; background: #f4f1ec; color: #1c1917; }
  .hero { background: linear-gradient(135deg,#1c1917,#44403c); color: #fff; border-radius: 22px; padding: 18px; text-align: center; }
  .hero h1 { margin: 0; font-size: 1.4rem; font-family: Georgia, serif; }
  .hero p { margin: 6px 0 0; font-size: .82rem; color: #d6d3d1; }
  .by { display: inline-block; margin-top: 10px; padding: 4px 14px; border: 1px solid #78716c; border-radius: 999px; font-size: .75rem; }
  .card { background: #fff; border: 1px solid #e7e5e4; border-radius: 20px; margin-top: 12px; padding: 16px; }
  .lbl { font-size: .72rem; font-weight: 700; letter-spacing: .5px; color: #78716c; margin: 0 0 8px; text-transform: uppercase; }
  #chips { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 6px; }
  .chip { flex: 0 0 auto; border: 1px solid #d6d3d1; background: #fafaf9; color: #44403c; border-radius: 999px; padding: 9px 14px; font-size: .82rem; font-weight: 600; }
  .chip.on { background: #1c1917; color: #fff; border-color: #1c1917; }
  .two { display: flex; gap: 8px; margin-top: 10px; }
  .two div { flex: 1; }
  select { width: 100%; padding: 10px; border-radius: 12px; border: 1px solid #d6d3d1; background: #fafaf9; font-size: .85rem; }
  .locked { opacity: .5; pointer-events: none; }
  .call { text-align: center; padding: 22px 16px; }
  .circle { width: 88px; height: 88px; border-radius: 50%; background: #e7e5e4; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; }
  .circle svg { width: 34px; height: 34px; stroke: #78716c; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
  .circle.live { background: #dcfce7; animation: pulse 1.6s infinite; } .circle.live svg { stroke: #16a34a; }
  .circle.speak { background: #e0e7ff; animation: pulse .9s infinite; } .circle.speak svg { stroke: #4f46e5; }
  @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(99,102,241,.35); } 70% { box-shadow: 0 0 0 18px rgba(99,102,241,0); } 100% { box-shadow: 0 0 0 0 rgba(99,102,241,0); } }
  h3 { margin: 0 0 4px; font-size: 1rem; }
  .sub { margin: 0 0 14px; font-size: .78rem; color: #78716c; }
  #timer { font-size: .8rem; color: #78716c; margin-bottom: 10px; display: none; }
  #btn { border: 0; border-radius: 12px; padding: 13px 28px; background: #1c1917; color: #fff; font-weight: 700; font-size: .9rem; }
  #btn.end { background: #dc2626; } #btn:disabled { opacity: .6; }
  .err { margin-top: 10px; color: #b91c1c; font-size: .8rem; word-break: break-word; }
  #qa { display: none; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 14px; }
  .qa { border: 1px solid #c7d2fe; background: #eef2ff; color: #3730a3; border-radius: 12px; padding: 9px 12px; font-size: .78rem; font-weight: 600; }
  #chat { max-height: 340px; overflow-y: auto; }
  .empty { text-align: center; color: #a8a29e; font-size: .85rem; padding: 14px 0; }
  .row { display: flex; margin: 7px 0; } .row.me { justify-content: flex-end; }
  .b { max-width: 88%; padding: 9px 13px; border-radius: 15px; font-size: .88rem; line-height: 1.6; }
  .me .b { background: #1c1917; color: #fff; border-bottom-right-radius: 4px; }
  .bot .b { background: #f5f5f4; border-bottom-left-radius: 4px; }
  .wod .w { font-size: 1.3rem; font-weight: 700; font-family: Georgia, serif; }
  .wod .m { font-size: .85rem; color: #57534e; margin: 4px 0; }
  .tag { display: inline-block; background: #fef3c7; color: #92400e; border-radius: 999px; padding: 3px 10px; font-size: .75rem; margin: 3px 3px 0 0; }
  .wod .e { font-size: .82rem; font-style: italic; color: #44403c; margin-top: 8px; }
  .foot { margin: 18px 0 8px; text-align: center; font-size: .78rem; color: #78716c; }
  .foot b { display: block; font-size: .92rem; color: #1c1917; }
</style>
</head>
<body>
  <div class="hero">
    <h1>🎓 AI English Coach</h1>
    <p>IELTS Speaking, Grammar, Vocabulary aur Spoken English, live voice par</p>
    <span class="by">Created by __OWNER__</span>
  </div>

  <div class="card" id="settings">
    <p class="lbl">1. Mode chuno</p>
    <div id="chips"></div>
    <div class="two">
      <div><p class="lbl">Level</p>
        <select id="level"><option>Beginner</option><option selected>Intermediate</option><option>Advanced</option></select></div>
      <div><p class="lbl">Samjhana</p>
        <select id="lang"><option value="en">English only</option><option value="mix" selected>English + Urdu</option></select></div>
    </div>
  </div>

  <div class="card call">
    <div id="circle" class="circle"><svg viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg></div>
    <h3 id="title">Ready to start</h3>
    <p class="sub" id="sub">Mode chuno aur Start dabao. Earphones laga lo.</p>
    <div id="timer">00:00</div>
    <button id="btn">Start Live Session</button>
    <div class="err" id="err"></div>
    <div id="qa"></div>
  </div>

  <div class="card">
    <p class="lbl">Transcript</p>
    <div id="chat"><div class="empty" id="empty">Baat cheet yahan nazar aayegi</div></div>
  </div>

  <div class="card wod">
    <p class="lbl">📚 Word of the Day</p>
    <div class="w" id="ww"></div><div class="m" id="wm"></div>
    <div id="ws2"></div><div class="e" id="we"></div>
  </div>

  <div class="foot">Made with ❤️ by <b>__OWNER__</b></div>

<script>
const TOKEN = __TOKEN__, MODEL = __MODEL__;
const $ = id => document.getElementById(id);
const BASE = "You are a friendly English tutor on a live voice call. Keep spoken replies short (2-4 sentences). Be warm and encouraging. If you are not sure about something, say so and never guess.";
const MODES = {
  talk: { n: "Free Talk", i: "💬", p: "Have a natural spoken English conversation. After each student turn, briefly correct any grammar or word choice mistake by saying the corrected sentence, then continue with a follow-up question.", h: "Greet the student warmly and ask what they would like to talk about." },
  ielts: { n: "IELTS Speaking", i: "🎯", p: "Act as a kind but strict IELTS Speaking examiner. Run Part 1 (3-4 short personal questions), then Part 2 (give a cue card topic, tell the student they have one minute to prepare and then should speak for up to two minutes), then Part 3 (3-4 abstract discussion questions). Ask one question at a time. Do not give feedback until asked or until the test ends. At the end give an estimated band score for Fluency, Vocabulary, Grammar and Pronunciation with one tip each.", h: "Introduce yourself as the examiner, ask for the student's full name, then start Part 1." },
  grammar: { n: "Grammar Fix", i: "✍️", p: "Be a grammar coach. Ask the student to say or describe something. Then repeat their sentence corrected, name the grammar rule in one simple line, and give one more example. Then ask for a new sentence using that rule.", h: "Greet the student and ask them to tell you what they did today in 2-3 sentences." },
  vocab: { n: "Vocab & Synonyms", i: "📚", p: "Be a vocabulary coach for IELTS. Teach one useful word at a time: meaning, 3 synonyms, one example sentence. Then ask the student to make their own sentence with it, correct it, and move to the next word. Also give better synonyms when the student uses simple words like good, bad or very.", h: "Greet the student and teach the first IELTS-level word." },
  pron: { n: "Fluency & Pronunciation", i: "🗣️", p: "Be a pronunciation and fluency coach. Give the student a short sentence or tongue twister to repeat. Listen, say what sounded good, what to improve (stress, sounds, pace), and let them try again. Increase difficulty slowly.", h: "Greet the student and give the first short sentence to repeat." }
};
const QA = [
  ["➡️ Next question", "Please ask me the next question."],
  ["✍️ Fix my grammar", "Please correct the grammar of my last answer and say the corrected version."],
  ["📚 Synonyms", "Give me 3 better synonyms for the key words in my last answer."],
  ["🐢 Speak slower", "Please speak slower and use simpler words."],
  ["📊 Feedback", "Please stop and give me detailed feedback on my speaking so far: estimated IELTS band for fluency, vocabulary, grammar and pronunciation, plus my top 3 tips."]
];
const WORDS = [
  ["resilient", "mushkil se jaldi ubharne wala", "tough, adaptable, hardy", "She is resilient and never gives up."],
  ["significant", "ahem, qabil-e-zikr", "major, notable, considerable", "There was a significant rise in prices."],
  ["beneficial", "faidemand", "helpful, useful, advantageous", "Exercise is beneficial for health."],
  ["diverse", "mukhtalif, rang-birangi", "varied, mixed, assorted", "Pakistan has a diverse culture."],
  ["inevitable", "jisse bacha na ja sake", "unavoidable, certain, inescapable", "Change is inevitable."],
  ["enhance", "behtar banana", "improve, boost, strengthen", "Reading can enhance your vocabulary."],
  ["reluctant", "hichkichane wala", "unwilling, hesitant, unenthusiastic", "He was reluctant to speak in public."],
  ["crucial", "bohat zaroori", "vital, essential, critical", "Sleep is crucial for students."],
  ["ambiguous", "mubham, ghair wazeh", "unclear, vague, uncertain", "The question was ambiguous."],
  ["flourish", "phalna phoolna", "thrive, prosper, bloom", "Small businesses flourish here."]
];

const S = { mode: "talk" };
let ws, micCtx, playCtx, stream, proc, nextT = 0, sources = [];
let active = false, ready = false, curMe = null, curBot = null, tInt = null, t0 = 0, prepT = null;

(function init() {
  const w = WORDS[Math.floor(Date.now() / 86400000) % WORDS.length];
  $('ww').textContent = w[0]; $('wm').textContent = w[1];
  $('ws2').innerHTML = w[2].split(', ').map(s => '<span class="tag">' + s + '</span>').join('');
  $('we').textContent = '"' + w[3] + '"';
  Object.keys(MODES).forEach(k => {
    const b = document.createElement('button');
    b.className = 'chip' + (k === S.mode ? ' on' : '');
    b.textContent = MODES[k].i + ' ' + MODES[k].n;
    b.onclick = () => {
      if (active) return;
      S.mode = k;
      [...$('chips').children].forEach(c => c.classList.remove('on'));
      b.classList.add('on');
    };
    $('chips').appendChild(b);
  });
  QA.forEach(q => {
    const b = document.createElement('button');
    b.className = 'qa'; b.textContent = q[0];
    b.onclick = () => { bubble('me', q[0]); sendText(q[1]); };
    $('qa').appendChild(b);
  });
  const p = document.createElement('button');
  p.className = 'qa'; p.id = 'prep'; p.textContent = '⏱ 1-min prep';
  p.onclick = prepTimer; $('qa').appendChild(p);
})();

function buildPrompt() {
  return BASE + " " + MODES[S.mode].p + " Student level: " + $('level').value + ". " +
    ($('lang').value === 'mix'
      ? "When explaining mistakes or word meanings, add a short Urdu explanation too."
      : "Explain only in simple English.");
}

function sendText(t) {
  if (ws && ws.readyState === 1 && ready) ws.send(JSON.stringify({ realtimeInput: { text: t } }));
}

function prepTimer() {
  const p = $('prep');
  if (prepT) { clearInterval(prepT); prepT = null; p.textContent = '⏱ 1-min prep'; return; }
  let s = 60; p.textContent = '⏱ 60s';
  prepT = setInterval(() => {
    s--; p.textContent = '⏱ ' + s + 's';
    if (s <= 0) {
      clearInterval(prepT); prepT = null; p.textContent = '⏱ 1-min prep';
      sendText("My one minute preparation time is over. Tell me to start speaking now.");
    }
  }, 1000);
}

function setState(s) {
  const c = $('circle'), btn = $('btn');
  c.className = 'circle' + (s === 'live' ? ' live' : s === 'speak' ? ' speak' : '');
  if (s === 'idle') {
    $('title').textContent = 'Ready to start';
    $('sub').textContent = 'Mode chuno aur Start dabao. Earphones laga lo.';
    btn.textContent = 'Start Live Session'; btn.className = ''; btn.disabled = false;
    $('qa').style.display = 'none'; $('timer').style.display = 'none';
    $('settings').classList.remove('locked');
  } else if (s === 'connecting') {
    $('title').textContent = 'Connecting...';
    $('sub').textContent = 'Mic ki ijazat do (Allow).';
    btn.textContent = 'Please wait'; btn.disabled = true;
    $('settings').classList.add('locked');
  } else if (s === 'live') {
    $('title').textContent = MODES[S.mode].i + ' ' + MODES[S.mode].n + ' | Listening';
    $('sub').textContent = 'Bolo! Beech mein bol sakte ho, tutor ruk jayega.';
    btn.textContent = 'End Session'; btn.className = 'end'; btn.disabled = false;
    $('qa').style.display = 'flex'; $('timer').style.display = 'block';
    $('prep').style.display = S.mode === 'ielts' ? '' : 'none';
  } else if (s === 'speak') {
    $('title').textContent = 'Tutor bol raha hai...';
  }
}

function bubble(role, text) {
  const e = $('empty'); if (e) e.remove();
  const row = document.createElement('div');
  row.className = 'row ' + (role === 'me' ? 'me' : 'bot');
  const b = document.createElement('div');
  b.className = 'b'; b.dir = 'auto'; b.textContent = text;
  row.appendChild(b); $('chat').appendChild(row);
  $('chat').scrollTop = $('chat').scrollHeight;
  return b;
}

function toB64(buf) {
  let s = ''; const u = new Uint8Array(buf);
  for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000));
  return btoa(s);
}

function playChunk(b64) {
  const bin = atob(b64), n = bin.length >> 1, f = new Float32Array(n);
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
  if (m.setupComplete) {
    ready = true; startMic(); setState('live'); startTimer();
    sendText(MODES[S.mode].h); return;
  }
  const sc = m.serverContent; if (!sc) return;
  if (sc.interrupted) { stopPlayback(); curBot = null; }
  if (sc.inputTranscription && sc.inputTranscription.text) {
    if (!curMe) curMe = bubble('me', '');
    curMe.textContent += sc.inputTranscription.text;
    $('chat').scrollTop = $('chat').scrollHeight;
  }
  if (sc.modelTurn && sc.modelTurn.parts) {
    sc.modelTurn.parts.forEach(p => { if (p.inlineData && p.inlineData.data) playChunk(p.inlineData.data); });
  }
  if (sc.outputTranscription && sc.outputTranscription.text) {
    curMe = null;
    if (!curBot) curBot = bubble('bot', '');
    curBot.textContent += sc.outputTranscription.text;
    $('chat').scrollTop = $('chat').scrollHeight;
  }
  if (sc.turnComplete) { curMe = null; curBot = null; }
}

function startTimer() {
  t0 = Date.now();
  tInt = setInterval(() => {
    const s = Math.floor((Date.now() - t0) / 1000);
    $('timer').textContent = '⏳ ' + String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
  }, 1000);
}

function startMic() {
  const src = micCtx.createMediaStreamSource(stream);
  proc = micCtx.createScriptProcessor(4096, 1, 1);
  proc.onaudioprocess = e => {
    if (!ready || !ws || ws.readyState !== 1) return;
    const f = e.inputBuffer.getChannelData(0), i16 = new Int16Array(f.length);
    for (let i = 0; i < f.length; i++) i16[i] = Math.max(-1, Math.min(1, f[i])) * 32767;
    ws.send(JSON.stringify({ realtimeInput: { audio: { data: toB64(i16.buffer), mimeType: 'audio/pcm;rate=16000' } } }));
  };
  src.connect(proc); proc.connect(micCtx.destination);
}

function stop() {
  active = false; ready = false;
  clearInterval(tInt); if (prepT) { clearInterval(prepT); prepT = null; $('prep').textContent = '⏱ 1-min prep'; }
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
  $('err').textContent = ''; setState('connecting'); active = true; curMe = curBot = null;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 } });
    playCtx = new AudioContext({ sampleRate: 24000 });
    micCtx = new AudioContext({ sampleRate: 16000 });
    await playCtx.resume(); await micCtx.resume();
    ws = new WebSocket('wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContentConstrained?access_token=' + encodeURIComponent(TOKEN));
    ws.onopen = () => ws.send(JSON.stringify({ setup: {
      model: 'models/' + MODEL,
      generationConfig: { responseModalities: ['AUDIO'] },
      systemInstruction: { parts: [{ text: buildPrompt() }] },
      inputAudioTranscription: {}, outputAudioTranscription: {}
    } }));
    ws.onmessage = async e => {
      const t = typeof e.data === 'string' ? e.data : await e.data.text();
      handle(JSON.parse(t));
    };
    ws.onerror = () => {};
    ws.onclose = ev => { if (active) fail('Connection band hogaya (' + ev.code + ') ' + (ev.reason || '')); };
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
    .replace("__OWNER__", OWNER)
)

components.html(html, height=1500, scrolling=True)
