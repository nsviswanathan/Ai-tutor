import { useEffect, useState } from "react";
import Link from "next/link";
import { get } from "../lib/api";

export default function Skills() {
  const [userId, setUserId] = useState("demo");
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");

  async function load() {
    setErr("");
    try {
      const data = await get(`/api/skills/${encodeURIComponent(userId)}`);
      setRows(data);
    } catch (e) {
      setErr(String(e.message || e));
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="container">
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <h1>Skill Dashboard</h1>
        <div className="small"><Link href="/">← Back to chat</Link></div>
      </div>

      <div className="card" style={{marginBottom: 12}}>
        <div className="small">User</div>
        <div style={{display:"flex", gap: 8, marginTop: 6}}>
          <input value={userId} onChange={(e)=>setUserId(e.target.value)} />
          <button onClick={load}>Load</button>
        </div>
        {err ? <div style={{marginTop: 8}} className="small">{err}</div> : null}
      </div>

      <div className="card">
        <div className="small">Skills tracked: {rows.length}</div>
        <div style={{marginTop: 10, overflowX:"auto"}}>
          <table style={{width:"100%", borderCollapse:"collapse"}}>
            <thead>
              <tr className="small">
                <th style={{textAlign:"left", padding:"8px"}}>skill_id</th>
                <th style={{textAlign:"left", padding:"8px"}}>strength</th>
                <th style={{textAlign:"left", padding:"8px"}}>interval_days</th>
                <th style={{textAlign:"left", padding:"8px"}}>next_due</th>
                <th style={{textAlign:"left", padding:"8px"}}>streak</th>
                <th style={{textAlign:"left", padding:"8px"}}>mistakes</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.skill_id} style={{borderTop:"1px solid #23283a"}}>
                  <td style={{padding:"8px"}}><span className="pill">{r.skill_id}</span></td>
                  <td style={{padding:"8px"}} className="small">{Number(r.strength).toFixed(2)}</td>
                  <td style={{padding:"8px"}} className="small">{r.interval_days}</td>
                  <td style={{padding:"8px"}} className="small">{r.next_due ? new Date(r.next_due).toLocaleString() : "-"}</td>
                  <td style={{padding:"8px"}} className="small">{r.streak}</td>
                  <td style={{padding:"8px"}} className="small">{r.mistakes}</td>
                </tr>
              ))}
              {rows.length === 0 ? (
                <tr><td colSpan={6} className="small" style={{padding:"10px"}}>No skills yet. Chat a bit first.</td></tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
