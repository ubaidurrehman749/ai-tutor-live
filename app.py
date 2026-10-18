import json
import time
from datetime import datetime, timedelta, timezone

import streamlit as st
import streamlit.components.v1 as components
from google import genai

st.set_page_config(page_title="AI English Coach | Ubaid Ur Rehman", page_icon="🎓", layout="centered")

OWNER = "Ubaid Ur Rehman"
# If you get a model error, only change this name
MODEL = "gemini-3.1-flash-live-preview"

MODE_LABELS = {
    "talk": "💬 Free Talk",
    "ielts": "🎯 IELTS Speaking",
    "grammar": "✍️ Grammar Fix",
    "vocab": "📚 Vocab & Synonyms",
    "pron": "🗣️ Pronunciation",
}
MODE_DESC = {
    "talk": "Natural conversation. The tutor corrects your mistakes as you speak.",
    "ielts": "Full IELTS Speaking test (Part 1, 2, 3) with an estimated band score at the end.",
    "grammar": "Say a sentence. The tutor fixes it and explains the grammar rule.",
    "vocab": "Learn useful IELTS words with synonyms and example sentences.",
    "pron": "Repeat sentences and get feedback on stress, sounds and pace.",
}

st.markdown(
    """
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: linear-gradient(165deg, #0f172a 0%, #1e1b4b 45%, #4c1d95 100%); background-attachment: fixed; }
    .block-container { max-width: 620px; padding: 0.8rem 0.7rem 1.5rem; }

    .hero { text-align: center; padding: 22px 16px; border-radius: 26px;
        background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);
        box-shadow: 0 16px 40px rgba(0,0,0,0.35); margin-bottom: 18px; }
    .hero .em { font-size: 2.4rem; line-height: 1; }
    .hero h1 { margin: 8px 0 4px; font-size: 1.7rem; font-weight: 800; padding: 0;
        background: linear-gradient(90deg, #c4b5fd, #f9a8d4, #fcd34d);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .hero p { color: #cbd5e1 !important; font-size: 0.88rem; margin: 0; }
    .hero .by { display: inline-block; margin-top: 12px; padding: 5px 16px; border-radius: 999px;
        background: linear-gradient(135deg, #8b5cf6, #ec4899); color: #fff; font-size: 0.78rem; font-weight: 700; }

    .sec { color: #e9d5ff; font-weight: 700; font-size: 0.78rem; letter-spacing: 1px;
        text-transform: uppercase; margin: 14px 0 8px 2px; }

    div[role="radiogroup"] { display: grid !important; grid-template-columns: 1fr 1fr; gap: 10px; }
    div[role="radiogroup"] label { width: 100%; margin: 0 !important; padding: 14px 12px;
        border-radius: 16px; background: rgba(255,255,255,0.08);
        border: 1.5px solid rgba(255,255,255,0.2); }
    div[role="radiogroup"] label p { color: #ffffff !important; font-weight: 600; font-size: 0.92rem; }
    div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, #8b5cf6, #ec4899); border-color: transparent;
        box-shadow: 0 10px 24px rgba(236,72,153,0.4); }
    div[role="radiogroup"] label:last-child { grid-column: span 2; }

    [data-testid="stWidgetLabel"] p { color: #e2e8f0 !important; font-weight: 600; }

    .picked { margin-top: 12px; padding: 11px 14px; border-radius: 14px;
        background: rgba(16,185,129,0.15); border: 1px solid rgba(52,211,153,0.5);
        color: #d1fae5; font-size: 0.85rem; line-height: 1.5; }

    .my-footer { margin-top: 22px; text-align: center; color: #94a3b8; font-size: 0.8rem; }
    .my-footer b { display: block; margin-top: 3px; font-size: 1rem;
        background: linear-gradient(90deg, #c4b5fd, #f9a8d4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
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

st.markdown(
    f"""
    <div class="hero">
        <div class="em">🎓</div>
        <h1>AI English Coach</h1>
        <p>IELTS Speaking, Grammar, Vocabulary and Spoken English on a live voice call</p>
        <span class="by">✨ Created by {OWNER}</span>
    </div>
    <div class="sec">1 · Choose your mode</div>
    """,
    unsafe_allow_html=True,
)

mode = st.radio(
    "Mode",
    list(MODE_LABELS.keys()),
    format_func=lambda k: MODE_LABELS[k],
    label_visibility="collapsed",
    key="mode_pick",
)
st.markdown(
    f'<div class="picked">✅ <b>{MODE_LABELS[mode]}</b> selected. {MODE_DESC[mode]}</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="sec">2 · Your level</div>', unsafe_allow_html=True)
level = st.selectbox(
    "Level",
    ["Beginner", "Intermediate", "Advanced"],
    index=1,
    label_visibility="collapsed",
    key="level_pick",
)

st.markdown('<div class="sec">3 · Start your live call</div>', unsafe_allow_html=True)

HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  body { margin: 0; font-family: Arial, sans-serif; background: transparent; color: #1e1b4b; }
  button { cursor: pointer; touch-action: manipulation; font-family: Arial, sans-serif; }
  .card { background: #ffffff; border-radius: 22px; margin-bottom: 14px; padding: 18px; box-shadow: 0 12px 30px rgba(0,0,0,.25); }
  .lbl { font-size: .72rem; font-weight: 700; letter-spacing: 1px; color: #7c3aed; margin: 0 0 10px; text-transform: uppercase; }
  .call { text-align: center; padding: 26px 16px; }
  .circle { width: 104px; height: 104px; border-radius: 50%; background: linear-gradient(135deg,#ede9fe,#fce7f3); margin: 0 auto 14px; display: flex; align-items: center; justify-content: center; }
  .circle svg { width: 40px; height: 40px; stroke: #7c3aed; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
  .circle.live { background: linear-gradient(135deg,#bbf7d0,#a7f3d0); animation: pulseG 1.6s infinite; } .circle.live svg { stroke: #059669; }
  .circle.speak { background: linear-gradient(135deg,#c7d2fe,#e9d5ff); animation: pulseP .9s infinite; } .circle.speak svg { stroke: #6d28d9; }
  @keyframes pulseG { 0% { box-shadow: 0 0 0 0 rgba(16,185,129,.45); } 70% { box-shadow: 0 0 0 24px rgba(16,185,129,0); } 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); } }
  @keyframes pulseP { 0% { box-shadow: 0 0 0 0 rgba(139,92,246,.5); } 70% { box-shadow: 0 0 0 24px rgba(139,92,246,0); } 100% { box-shadow: 0 0 0 0 rgba(139,92,246,0); } }
  h3 { margin: 0 0 4px; font-size: 1.05rem; }
  .sub { margin: 0 0 14px; font-size: .8rem; color: #6b7280; line-height: 1.5; }
  #timer { font-size: .85rem; color: #7c3aed; font-weight: 700; margin-bottom: 10px; display: none; }
  #btn { border: 0; border-radius: 999px; padding: 15px 36px; background: linear-gradient(135deg,#8b5cf6,#ec4899); color: #fff; font-weight: 700; font-size: 1rem; box-shadow: 0 10px 22px rgba(236,72,153,.4); }
  #btn.end { background: linear-gradient(135deg,#ef4444,#dc2626); box-shadow: 0 10px 22px rgba(220,38,38,.4); }
  #btn:disabled { opacity: .6; }
  .err { margin-top: 12px; color: #b91c1c; font-size: .8rem; word-break: break-word; }
  #qa { display: none; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 16px; }
  .qa { border: 1px solid #ddd6fe; background: #f5f3ff; color: #5b21b6; border-radius: 12px; padding: 10px 12px; font-size: .78rem; font-weight: 700; }
  #chat { max-height: 330px; overflow-y: auto; }
  .empty { text-align: center; color: #9ca3af; font-size: .85rem; padding: 14px 0; }
  .row { display: flex; margin: 8px 0; } .row.me { justify-content: flex-end; }
  .b { max-width: 88%; padding: 10px 14px; border-radius: 16px; font-size: .88rem; line-height: 1.6; }
  .me .b { background: linear-gradient(135deg,#8b5cf6,#ec4899); color: #fff; border-bottom-right-radius: 4px; }
  .bot .b { background: #f3f4f6; color: #1f2937; border-bottom-left-radius: 4px; }
  .wod { background: linear-gradient(135deg,#fffbeb,#fef3c7); }
  .wod .w { font-size: 1.4rem; font-weight: 800; font-family: Georgia, serif; color: #78350f; }
  .wod .m { font-size: .86rem; color: #57534e; margin: 4px 0 6px; }
  .tag { display: inline-block; background: #fff; color: #92400e; border: 1px solid #fcd34d; border-radius: 999px; padding: 3px 11px; font-size: .75rem; margin: 3px 3px 0 0; font-weight: 600; }
  .wod .e { font-size: .84rem; font-style: italic; color: #44403c; margin-top: 10px; }
</style>
</head>
<body>
  <div class="card call">
    <div id="circle" class="circle"><svg viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg></div>
    <h3 id="title">Ready to start</h3>
    <p class="sub" id="sub">Put on your earphones and tap Start.</p>
    <div id="timer">00:00</div>
    <button id="btn" type="button">Start Live Session</button>
    <div class="err" id="err"></div>
    <div id="qa"></div>
  </div>

  <div class="card">
    <p class="lbl">Transcript</p>
    <div id="chat"><div class="empty" id="empty">Your conversation will appear here</div></div>
  </div>

  <div class="card wod">
    <p class="lbl">📚 Word of the Day</p>
    <div class="w" id="ww"></div><div class="m" id="wm"></div>
    <div id="ws2"></div><div class="e" id="we"></div>
  </div>

<script>
const TOKEN = __TOKEN__, MODEL = __MODEL__, MODE = __MODE__, LEVEL = __LEVEL__;
const $ = id => document.getElementById(id);
const BASE = "You are a friendly English tutor on a live voice call. Speak and explain ONLY in English. Never use Urdu, Hindi or Roman Urdu. If the student speaks another language, gently ask them to try in English and help them say it in English. Keep spoken replies short (2-4 sentences). Be warm and encouraging. If you are not sure about something, say so and never guess.";
const MODES = {
  talk: { n: "Free Talk", i: "💬", p: "Have a natural spoken English conversation. After each student turn, briefly correct any grammar or word choice mistake by saying the corrected sentence, then continue with a follow-up question.", h: "Greet the student warmly and ask what they would like to talk about." },
  ielts: { n: "IELTS Speaking", i: "🎯", p: "Act as a kind but strict IELTS Speaking examiner. Run Part 1 (3-4 short personal questions), then Part 2 (give a cue card topic, tell the student they have one minute to prepare and then should speak for up to two minutes), then Part 3 (3-4 abstract discussion questions). Ask one question at a time. Do not give feedback until asked or until the test ends. At the end give an estimated band score for Fluency, Vocabulary, Grammar and Pronunciation with one tip each.", h: "Introduce yourself as the examiner, ask for the student's full name, then start Part 1." },
  grammar: { n: "Grammar Fix", i: "✍️", p: "Be a grammar coach. Ask the student to say or describe something. Then repeat their sentence corrected, name the grammar rule in one simple line, and give one more example. Then ask for a new sentence using that rule.", h: "Greet the student and ask them to tell you what they did today in 2-3 sentences." },
  vocab: { n: "Vocab & Synonyms", i: "📚", p: "Be a vocabulary coach for IELTS. Teach one useful word at a time: meaning, 3 synonyms, one example sentence. Then ask the student to make their own sentence with it, correct it, and move to the next word. Also give better synonyms when the student uses simple words like good, bad or very.", h: "Greet the student and teach the first IELTS-level word." },
  pron: { n: "Pronunciation", i: "🗣️", p: "Be a pronunciation and fluency coach. Give the student a short sentence or tongue twister to repeat. Listen, say what sounded good, what to improve (stress, sounds, pace), and let them try again. Increase difficulty slowly.", h: "Greet the student and give the first short sentence to repeat." }
};
const QA = [
  ["➡️ Next question", "Please ask me the next question."],
  ["✍️ Fix my grammar", "Please correct the grammar of my last answer and say the corrected version."],
  ["📚 Synonyms", "Give me 3 better synonyms for the key words in my last answer."],
  ["🐢 Speak slower", "Please speak slower and use simpler words."],
  ["📊 Feedback", "Please stop and give me detailed feedback on my speaking so far: estimated IELTS band for fluency, vocabulary, grammar and pronunciation, plus my top 3 tips."]
];
const WORDS = [
  ["resilient", "able to recover quickly from difficulties", "tough, adaptable, hardy", "She is resilient and never gives up."],
  ["significant", "important or large enough to matter", "major, notable, considerable", "There was a significant rise in prices."],
  ["beneficial", "having a good effect", "helpful, useful, advantageous", "Exercise is beneficial for health."],
  ["diverse", "showing a lot of variety", "varied, mixed, assorted", "Pakistan has a diverse culture."],
  ["inevitable", "certain to happen", "unavoidable, certain, inescapable", "Change is inevitable."],
  ["enhance", "to make something better", "improve, boost, strengthen", "Reading can enhance your vocabulary."],
  ["reluctant", "not willing to do something", "unwilling, hesitant, unenthusiastic", "He was reluctant to speak in public."],
  ["crucial", "extremely important", "vital, essential, critical", "Sleep is crucial for students."],
  ["ambiguous", "having more than one possible meaning", "unclear, vague, uncertain", "The question was ambiguous."],
  ["flourish", "to grow and develop successfully", "thrive, prosper, bloom", "Small businesses flourish here."]
];

let ws, micCtx, playCtx, stream, proc, nextT = 0, sources = [];
let active = false, ready = false, gotReply = false, curMe = null, curBot = null, tInt = null, t0 = 0, prepT = null;

(function init() {
  const w = WORDS[Math.floor(Date.now() / 86400000) % WORDS.length];
  $('ww').textContent = w[0]; $('wm').textContent = w[1];
  $('ws2').innerHTML = w[2].split(', ').map(s => '<span class="tag">' + s + '</span>').join('');
  $('we').textContent = '"' + w[3] + '"';
  QA.forEach(q => {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'qa'; b.textContent = q[0];
    b.addEventListener('click', () => { bubble('me', q[0]); askTutor(q[1]); });
    $('qa').appendChild(b);
  });
  const p = document.createElement('button');
  p.type = 'button'; p.className = 'qa'; p.id = 'prep'; p.textContent = '⏱ 1-min prep';
  p.addEventListener('click', prepTimer); $('qa').appendChild(p);
  $('sub').textContent = 'Mode: ' + MODES[MODE].i + ' ' + MODES[MODE].n + ' | Level: ' + LEVEL + '. Put on earphones and tap Start.';
})();

function buildPrompt() {
  return BASE + " " + MODES[MODE].p + " Student level: " + LEVEL + ".";
}

// Try one way first; if the tutor stays silent for 4 seconds, try the other way
function askTutor(t) {
  if (!(ws && ws.readyState === 1 && ready)) return;
  gotReply = false;
  ws.send(JSON.stringify({ realtimeInput: { text: t } }));
  setTimeout(() => {
    if (active && ready && !gotReply && ws && ws.readyState === 1) {
      ws.send(JSON.stringify({ clientContent: { turns: [{ role: 'user', parts: [{ text: t }] }], turnComplete: true } }));
    }
  }, 4000);
}

function prepTimer() {
  const p = $('prep');
  if (prepT) { clearInterval(prepT); prepT = null; p.textContent = '⏱ 1-min prep'; return; }
  let s = 60; p.textContent = '⏱ 60s';
  prepT = setInterval(() => {
    s--; p.textContent = '⏱ ' + s + 's';
    if (s <= 0) {
      clearInterval(prepT); prepT = null; p.textContent = '⏱ 1-min prep';
      askTutor("My one minute preparation time is over. Tell me to start speaking now.");
    }
  }, 1000);
}

function setState(s) {
  const c = $('circle'), btn = $('btn');
  c.className = 'circle' + (s === 'live' ? ' live' : s === 'speak' ? ' speak' : '');
  if (s === 'idle') {
    $('title').textContent = 'Ready to start';
    $('sub').textContent = 'Mode: ' + MODES[MODE].i + ' ' + MODES[MODE].n + ' | Level: ' + LEVEL + '. Put on earphones and tap Start.';
    btn.textContent = 'Start Live Session'; btn.className = ''; btn.disabled = false;
    $('qa').style.display = 'none'; $('timer').style.display = 'none';
  } else if (s === 'connecting') {
    $('title').textContent = 'Connecting...';
    $('sub').textContent = 'Please allow microphone access.';
    btn.textContent = 'Please wait'; btn.disabled = true;
  } else if (s === 'live') {
    $('title').textContent = MODES[MODE].i + ' ' + MODES[MODE].n + ' | Listening';
    $('sub').textContent = 'Speak now. You can interrupt the tutor anytime. If the tutor stays silent, say "Hello".';
    btn.textContent = 'End Session'; btn.className = 'end'; btn.disabled = false;
    $('qa').style.display = 'flex'; $('timer').style.display = 'block';
    $('prep').style.display = MODE === 'ielts' ? '' : 'none';
  } else if (s === 'speak') {
    $('title').textContent = 'Tutor is speaking...';
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
    setTimeout(() => askTutor(MODES[MODE].h), 400);
    return;
  }
  const sc = m.serverContent; if (!sc) return;
  if (sc.interrupted) { stopPlayback(); curBot = null; }
  if (sc.inputTranscription && sc.inputTranscription.text) {
    if (!curMe) curMe = bubble('me', '');
    curMe.textContent += sc.inputTranscription.text;
    $('chat').scrollTop = $('chat').scrollHeight;
  }
  if (sc.modelTurn && sc.modelTurn.parts) {
    sc.modelTurn.parts.forEach(p => {
      if (p.inlineData && p.inlineData.data) { gotReply = true; playChunk(p.inlineData.data); }
    });
  }
  if (sc.outputTranscription && sc.outputTranscription.text) {
    gotReply = true; curMe = null;
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
  $('err').textContent = ''; setState('connecting'); active = true; curMe = curBot = null; gotReply = false;
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
    ws.onclose = ev => { if (active) fail('Connection closed (' + ev.code + ') ' + (ev.reason || '')); };
  } catch (err) { fail(err.message || String(err)); }
}

$('btn').addEventListener('click', () => { active ? stop() : start(); });
</script>
</body>
</html>
"""

html = (
    HTML.replace("__TOKEN__", json.dumps(st.session_state.tok))
    .replace("__MODEL__", json.dumps(MODEL))
    .replace("__MODE__", json.dumps(mode))
    .replace("__LEVEL__", json.dumps(level))
)

components.html(html, height=1150, scrolling=True)

st.markdown(
    f"""
    <div class="my-footer">
        Made with ❤️ by
        <b>{OWNER}</b>
        © 2026 AI English Coach. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True,
)
