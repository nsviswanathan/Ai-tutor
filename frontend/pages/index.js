import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { post, get } from "../lib/api";

const CONTEXTS = ["Airport", "Restaurant", "Classroom", "Office", "Shopping"];
const LEVELS = ["Beginner", "Intermediate", "Advanced"];

export default function Home() {
  const [userId, setUserId] = useState("demo");
  const [context, setContext] = useState("Airport");
  const [level, setLevel] = useState("Beginner");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const [chat, setChat] = useState([
    { role: "assistant", content: "Hey! Pick a context and talk to me like it’s real life. I’ll coach you and adapt what we practice next." }
  ]);

  const [plan, setPlan] = useState(null);
  const [progress, setProgress] = useState(null);
  const [profile, setProfile] = useState(null);

  const boxRef = useRef(null);

  useEffect(() => {
    if (boxRef.current) boxRef.current.scrollTop = boxRef.current.scrollHeight;
  }, [chat]);

  async function refreshProgress() {
  const p = await get(`/api/progress/${encodeURIComponent(userId)}`);
  setProgress(p);
}
async function refreshProfile() {
  const pr = await get(`/api/profile/${encodeURIComponent(userId)}`);
  setProfile(pr);
}

  async function refreshPlan() {
    const p = await post("/api/practice/next", { user_id: userId, context, level, limit: 6 });
    setPlan(p);
  }

  useEffect(() => { refreshPlan().catch(()=>{}); }, [context, level]);

  async function send() {
    if (!message.trim()) return;
    const userMsg = message.trim();
    setMessage("");
    setChat((c) => [...c, { role: "user", content: userMsg }]);
    setBusy(true);
    try {
      const res = await post("/api/chat", {
        user_id: userId,
        context,
        level,
        message: userMsg
      });
      setChat((c) => [...c, { role: "assistant", content: res.reply }]);
      await refreshPlan();
      await refreshProgress();
    } catch (e) {
      setChat((c) => [...c, { role: "assistant", content: "Error talking to backend. Check backend is running + CORS is set.\n\n" + String(e.message || e) }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="container">
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", gap: 12}}>
        <h1>AI Tutor</h1>
        <div className="small">
          <Link href="/skills">Skill Dashboard →</Link> · <Link href="/profile">Profile →</Link>
        </div>
      </div>

      <div className="row">
        <div className="card">
          <div style={{display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap: 8}}>
            <div>
              <div className="small">User</div>
              <input value={userId} onChange={(e)=>setUserId(e.target.value)} placeholder="demo" />
            </div>
            <div>
              <div className="small">Context</div>
              <select value={context} onChange={(e)=>setContext(e.target.value)}>
                {CONTEXTS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <div className="small">Level</div>
              <select value={level} onChange={(e)=>setLevel(e.target.value)}>
                {LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
          </div>

          <div style={{marginTop: 12}} className="chatBox" ref={boxRef}>
            {chat.map((m, idx) => (
              <div key={idx} className={`bubble ${m.role}`}>
                {m.content}
              </div>
            ))}
          </div>

          <div className="inputRow">
            <input
              value={message}
              onChange={(e)=>setMessage(e.target.value)}
              placeholder="Type a message…"
              onKeyDown={(e)=>{ if (e.key === "Enter") send(); }}
              disabled={busy}
            />
            <button onClick={send} disabled={busy}>Send</button>
          </div>

          <div className="small" style={{marginTop: 8}}>
            Tip: talk naturally. I’ll correct you and the practice plan will update automatically.
          </div>
        </div>

        <div className="card">
          <h2>Next Practice</h2>
<div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap: 10, marginBottom: 10}}>
  <div className="card">
    <div className="small">Today</div>
    <div style={{fontSize: 22, marginTop: 4}}>
      {progress ? `${progress.today_minutes}/${progress.daily_goal} min` : "—"}
    </div>
    <div className="small" style={{marginTop: 6}}>
      {progress ? `Daily: ${(progress.daily_pct*100).toFixed(0)}%` : ""}
    </div>
  </div>
  <div className="card">
    <div className="small">Last 7 days</div>
    <div style={{fontSize: 22, marginTop: 4}}>
      {progress ? `${progress.week_minutes}/${progress.weekly_goal} min` : "—"}
    </div>
    <div className="small" style={{marginTop: 6}}>
      {progress ? `Weekly: ${(progress.weekly_pct*100).toFixed(0)}%` : ""}
    </div>
  </div>
</div>

          {!plan ? (
            <div className="small">Loading…</div>
          ) : (
            <>
              <div className="small">Scenario prompt</div>
              <div style={{marginTop: 6}} className="card">{plan.scenario_prompt}</div>

              <hr />

              <div className="small">Due now</div>
              <div className="list" style={{marginTop: 6}}>
                {(plan.due || []).length === 0 ? (
                  <div className="small">Nothing due. Nice.</div>
                ) : (
                  plan.due.map((s) => (
                    <div key={s.skill_id}>
                      <span className="pill">{s.skill_id}</span>
                      <span className="small">strength {s.strength.toFixed(2)} · streak {s.streak} · mistakes {s.mistakes}</span>
                    </div>
                  ))
                )}
              </div>

              <div style={{marginTop: 14}} className="small">Weak next</div>
              <div className="list" style={{marginTop: 6}}>
                {(plan.weak || []).length === 0 ? (
                  <div className="small">No weak items right now.</div>
                ) : (
                  plan.weak.map((s) => (
                    <div key={s.skill_id}>
                      <span className="pill">{s.skill_id}</span>
                      <span className="small">strength {s.strength.toFixed(2)} · streak {s.streak} · mistakes {s.mistakes}</span>
                    </div>
                  ))
                )}
              </div>

              <div style={{marginTop: 14}} className="small">Suggested new</div>
              <div style={{marginTop: 6}}>
                {(plan.new || []).length === 0 ? (
                  <div className="small">No suggestions.</div>
                ) : plan.new.map((x) => <span key={x} className="pill">{x}</span>)}
              </div>

              <div style={{marginTop: 14}}>
                <button onClick={refreshPlan}>Refresh</button>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="small" style={{marginTop: 14}}>
        Backend: <code>{process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}</code>
      </div>
    </div>
  );
}
