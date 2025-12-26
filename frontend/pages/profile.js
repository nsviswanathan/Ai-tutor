import { useEffect, useState } from "react";
import Link from "next/link";
import { get, post } from "../lib/api";

const CONTEXTS = ["Airport", "Restaurant", "Classroom", "Office", "Shopping"];
const LEVELS = ["Beginner", "Intermediate", "Advanced"];

export default function Profile() {
  const [userId, setUserId] = useState("demo");
  const [profile, setProfile] = useState(null);
  const [progress, setProgress] = useState(null);
  const [err, setErr] = useState("");
  const [saving, setSaving] = useState(false);

  async function load() {
    setErr("");
    try {
      const pr = await get(`/api/profile/${encodeURIComponent(userId)}`);
      const pg = await get(`/api/progress/${encodeURIComponent(userId)}`);
      setProfile(pr);
      setProgress(pg);
    } catch (e) {
      setErr(String(e.message || e));
    }
  }

  useEffect(() => { load(); }, []);

  async function save() {
    if (!profile) return;
    setSaving(true);
    setErr("");
    try {
      // Backend expects PUT, but we use post helper; call fetch directly for PUT
      const base = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
      const r = await fetch(`${base}/api/profile/${encodeURIComponent(userId)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          native_language: profile.native_language,
          target_language: profile.target_language,
          level: profile.level,
          daily_minutes_goal: Number(profile.daily_minutes_goal),
          weekly_minutes_goal: Number(profile.weekly_minutes_goal),
          focus_contexts: profile.focus_contexts || []
        })
      });
      if (!r.ok) throw new Error(await r.text());
      const pr = await r.json();
      setProfile(pr);
      const pg = await get(`/api/progress/${encodeURIComponent(userId)}`);
      setProgress(pg);
    } catch (e) {
      setErr(String(e.message || e));
    } finally {
      setSaving(false);
    }
  }

  function toggleContext(c) {
    const set = new Set(profile.focus_contexts || []);
    if (set.has(c)) set.delete(c);
    else set.add(c);
    setProfile({ ...profile, focus_contexts: Array.from(set) });
  }

  return (
    <div className="container">
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <h1>User Profile</h1>
        <div className="small"><Link href="/">← Back</Link></div>
      </div>

      <div className="card" style={{marginBottom: 12}}>
        <div className="small">User</div>
        <div style={{display:"flex", gap: 8, marginTop: 6}}>
          <input value={userId} onChange={(e)=>setUserId(e.target.value)} />
          <button onClick={load}>Load</button>
        </div>
        {err ? <div className="small" style={{marginTop: 8}}>{err}</div> : null}
      </div>

      {!profile ? (
        <div className="card"><div className="small">Loading…</div></div>
      ) : (
        <div className="row">
          <div className="card">
            <h2>Settings</h2>

            <div className="small" style={{marginTop: 10}}>Native language</div>
            <input value={profile.native_language} onChange={(e)=>setProfile({...profile, native_language: e.target.value})} />

            <div className="small" style={{marginTop: 10}}>Target language</div>
            <input value={profile.target_language} onChange={(e)=>setProfile({...profile, target_language: e.target.value})} />

            <div className="small" style={{marginTop: 10}}>Level</div>
            <select value={profile.level} onChange={(e)=>setProfile({...profile, level: e.target.value})}>
              {LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
            </select>

            <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap: 10}}>
              <div>
                <div className="small" style={{marginTop: 10}}>Daily minutes goal</div>
                <input type="number" value={profile.daily_minutes_goal} onChange={(e)=>setProfile({...profile, daily_minutes_goal: e.target.value})} />
              </div>
              <div>
                <div className="small" style={{marginTop: 10}}>Weekly minutes goal</div>
                <input type="number" value={profile.weekly_minutes_goal} onChange={(e)=>setProfile({...profile, weekly_minutes_goal: e.target.value})} />
              </div>
            </div>

            <div className="small" style={{marginTop: 10}}>Focus contexts</div>
            <div style={{marginTop: 6}}>
              {CONTEXTS.map(c => (
                <span
                  key={c}
                  className="pill"
                  onClick={()=>toggleContext(c)}
                  style={{cursor:"pointer", opacity: (profile.focus_contexts||[]).includes(c) ? 1 : 0.5}}
                >
                  {c}
                </span>
              ))}
            </div>

            <div style={{marginTop: 14}}>
              <button onClick={save} disabled={saving}>{saving ? "Saving..." : "Save"}</button>
            </div>

            <div className="small" style={{marginTop: 10}}>
              Created: {new Date(profile.created_at).toLocaleString()}<br/>
              Updated: {new Date(profile.updated_at).toLocaleString()}
            </div>
          </div>

          <div className="card">
            <h2>Progress</h2>
            {!progress ? (
              <div className="small">Loading…</div>
            ) : (
              <>
                <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap: 10}}>
                  <div className="card">
                    <div className="small">Today</div>
                    <div style={{fontSize: 26, marginTop: 4}}>
                      {progress.today_minutes}/{progress.daily_goal} min
                    </div>
                    <div className="small" style={{marginTop: 6}}>
                      Daily: {(progress.daily_pct*100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="card">
                    <div className="small">Last 7 days</div>
                    <div style={{fontSize: 26, marginTop: 4}}>
                      {progress.week_minutes}/{progress.weekly_goal} min
                    </div>
                    <div className="small" style={{marginTop: 6}}>
                      Weekly: {(progress.weekly_pct*100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                <div className="small" style={{marginTop: 10}}>
                  Last activity: {progress.last_activity ? new Date(progress.last_activity).toLocaleString() : "—"}
                </div>

                <hr />

                <div className="small">How progress is counted (MVP)</div>
                <div className="small" style={{marginTop: 6}}>
                  Each user message counts as ~1 minute by default. You can later replace this with real timers,
                  speech session duration, or lesson completion metrics.
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
