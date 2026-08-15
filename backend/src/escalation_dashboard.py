"""
escalation_dashboard.py
A lightweight Flask dashboard to view and manage Dhan Rakshak escalation requests.
Run with:  python escalation_dashboard.py
Then open: http://localhost:5050
"""

import os
import sys

# Allow imports from src/ whether run from backend/ or backend/src/
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from flask import Flask, render_template_string, request, jsonify

try:
    import db
except ImportError:
    import src.db as db

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Shared nav tab snippet (injected into both pages)
# ---------------------------------------------------------------------------
NAV_TABS_HTML = """
<div class="tab-bar">
  <a href="/" class="tab-link {esc_active}">🛡️ Escalations</a>
  <a href="/analytics" class="tab-link {ana_active}">📊 Call Analytics</a>
</div>
"""

NAV_TAB_CSS = """
    .tab-bar {
      display: flex; gap: .5rem; padding: .75rem 2rem;
      background: var(--surface); border-bottom: 1px solid var(--border);
    }
    .tab-link {
      padding: .4rem 1.1rem; border-radius: 8px; font-size: .82rem; font-weight: 600;
      text-decoration: none; color: var(--muted); transition: all .2s;
      border: 1px solid transparent;
    }
    .tab-link:hover { color: var(--text); border-color: var(--border); }
    .tab-link.active { background: var(--accent); color: #fff; border-color: var(--accent); }
"""

# ---------------------------------------------------------------------------
# HTML Template — premium dark design (Escalations page)
# ---------------------------------------------------------------------------
DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Dhan Rakshak – Escalation Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg:        #0d0f1a;
      --surface:   #141726;
      --surface2:  #1c2035;
      --border:    #252a40;
      --accent:    #6c63ff;
      --accent2:   #a78bfa;
      --text:      #e2e8f0;
      --muted:     #8892a4;
      --green:     #22c55e;
      --amber:     #f59e0b;
      --red:       #ef4444;
      --blue:      #3b82f6;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }

    nav {
      display: flex; align-items: center; justify-content: space-between;
      padding: 1rem 2rem; background: var(--surface);
      border-bottom: 1px solid var(--border);
      position: sticky; top: 0; z-index: 100;
    }
    .nav-brand { display: flex; align-items: center; gap: .75rem; }
    .nav-brand .logo {
      width: 38px; height: 38px;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem;
    }
    .nav-brand h1 { font-size: 1.1rem; font-weight: 700; }
    .nav-brand span { font-size: .75rem; color: var(--muted); }
    .nav-right { display: flex; align-items: center; gap: 1rem; }
    .badge-count {
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      color: #fff; font-size: .72rem; font-weight: 700;
      padding: .25rem .65rem; border-radius: 999px;
    }
    .refresh-btn {
      background: var(--surface2); border: 1px solid var(--border); color: var(--text);
      padding: .4rem .9rem; border-radius: 8px; font-size: .8rem; cursor: pointer;
      text-decoration: none; transition: background .2s;
    }
    .refresh-btn:hover { background: var(--border); }

    main { max-width: 1300px; margin: 0 auto; padding: 2rem 1.5rem; }

    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.2rem 1.4rem; transition: transform .2s; }
    .stat-card:hover { transform: translateY(-2px); }
    .stat-card .label { font-size: .72rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin-bottom: .4rem; }
    .stat-card .value { font-size: 2rem; font-weight: 700; }
    .c-open .value   { color: var(--red); }
    .c-prog .value   { color: var(--amber); }
    .c-done .value   { color: var(--green); }
    .c-total .value  { color: var(--accent2); }

    .filters { display: flex; gap: .5rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
    .filter-btn {
      padding: .4rem 1rem; border-radius: 8px; font-size: .8rem; font-weight: 500;
      cursor: pointer; border: 1px solid var(--border); background: var(--surface); color: var(--muted); transition: all .2s;
    }
    .filter-btn.active, .filter-btn:hover { background: var(--accent); border-color: var(--accent); color: #fff; }

    .table-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; }
    table { width: 100%; border-collapse: collapse; }
    thead tr { background: var(--surface2); }
    th { padding: .85rem 1rem; font-size: .72rem; text-transform: uppercase; letter-spacing: .07em; color: var(--muted); font-weight: 600; text-align: left; }
    tbody tr { border-top: 1px solid var(--border); transition: background .15s; }
    tbody tr:hover { background: var(--surface2); }
    td { padding: .9rem 1rem; font-size: .88rem; vertical-align: top; }

    .badge { display: inline-block; padding: .2rem .6rem; border-radius: 6px; font-size: .72rem; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; }
    .badge-high      { background: rgba(239,68,68,.15);   color: var(--red); }
    .badge-medium    { background: rgba(245,158,11,.15);  color: var(--amber); }
    .badge-low       { background: rgba(59,130,246,.15);  color: var(--blue); }
    .badge-fraud     { background: rgba(239,68,68,.1);    color: #f87171; }
    .badge-scope     { background: rgba(107,99,255,.1);   color: var(--accent2); }
    .badge-open      { background: rgba(239,68,68,.12);   color: var(--red); }
    .badge-in-progress { background: rgba(245,158,11,.12); color: var(--amber); }
    .badge-resolved  { background: rgba(34,197,94,.12);   color: var(--green); }

    .ref-id { font-family: 'Courier New', monospace; font-weight: 700; color: var(--accent2); font-size: .92rem; }
    .summary-text { color: var(--text); max-width: 240px; line-height: 1.5; }
    .checked-text { color: var(--muted); font-size: .8rem; max-width: 200px; line-height: 1.4; }

    .action-group { display: flex; flex-direction: column; gap: .4rem; }
    .act-btn { border: none; border-radius: 7px; padding: .3rem .7rem; font-size: .75rem; font-weight: 600; cursor: pointer; transition: opacity .2s; white-space: nowrap; }
    .act-btn:hover { opacity: .8; }
    .act-btn.in-prog  { background: rgba(245,158,11,.2); color: var(--amber); }
    .act-btn.resolve  { background: rgba(34,197,94,.2);  color: var(--green); }
    .act-btn.reopen   { background: rgba(107,99,255,.2); color: var(--accent2); }

    .ts { color: var(--muted); font-size: .78rem; }

    .empty { text-align: center; padding: 4rem 2rem; color: var(--muted); }
    .empty .icon { font-size: 3rem; margin-bottom: 1rem; }
    .empty h3 { font-size: 1.1rem; margin-bottom: .4rem; color: var(--text); }

    #toast {
      position: fixed; bottom: 1.5rem; right: 1.5rem;
      background: var(--green); color: #fff;
      padding: .75rem 1.25rem; border-radius: 10px; font-size: .85rem; font-weight: 600;
      opacity: 0; transform: translateY(10px); transition: all .3s; pointer-events: none;
    }
    #toast.show { opacity: 1; transform: translateY(0); }

    /* Tab bar */
    .tab-bar {
      display: flex; gap: .5rem; padding: .75rem 2rem;
      background: var(--surface); border-bottom: 1px solid var(--border);
    }
    .tab-link {
      padding: .4rem 1.1rem; border-radius: 8px; font-size: .82rem; font-weight: 600;
      text-decoration: none; color: var(--muted); transition: all .2s;
      border: 1px solid transparent;
    }
    .tab-link:hover { color: var(--text); border-color: var(--border); }
    .tab-link.active { background: var(--accent); color: #fff; border-color: var(--accent); }
  </style>
</head>
<body>

<nav>
  <div class="nav-brand">
    <div class="logo">🛡️</div>
    <div>
      <h1>Dhan Rakshak</h1>
      <span>Human Escalation Dashboard</span>
    </div>
  </div>
  <div class="nav-right">
    <span class="badge-count">{{ open_count }} Open</span>
    <a class="refresh-btn" href="/">⟳ Refresh</a>
  </div>
</nav>

<div class="tab-bar">
  <a href="/" class="tab-link active">🛡️ Escalations</a>
  <a href="/analytics" class="tab-link">📊 Call Analytics</a>
</div>

<main>
  <div class="stats">
    <div class="stat-card c-total"><div class="label">Total</div><div class="value">{{ escalations|length }}</div></div>
    <div class="stat-card c-open"><div class="label">Open</div><div class="value">{{ open_count }}</div></div>
    <div class="stat-card c-prog"><div class="label">In Progress</div><div class="value">{{ prog_count }}</div></div>
    <div class="stat-card c-done"><div class="label">Resolved</div><div class="value">{{ done_count }}</div></div>
  </div>

  <div class="filters">
    <button class="filter-btn active" onclick="filterRows('all', this)">All</button>
    <button class="filter-btn" onclick="filterRows('open', this)">🔴 Open</button>
    <button class="filter-btn" onclick="filterRows('in-progress', this)">🟡 In Progress</button>
    <button class="filter-btn" onclick="filterRows('resolved', this)">🟢 Resolved</button>
    <button class="filter-btn" onclick="filterRows('fraud_report', this)">⚠️ Fraud</button>
    <button class="filter-btn" onclick="filterRows('out_of_scope_decision', this)">📋 Out of Scope</button>
  </div>

  {% if escalations %}
  <div class="table-wrap">
    <table id="esc-table">
      <thead>
        <tr>
          <th>Ref ID</th><th>Caller</th><th>Reason</th><th>Situation</th>
          <th>Agent Checked</th><th>Urgency</th><th>Language</th>
          <th>Follow-up</th><th>Status</th><th>Created</th><th>Action</th>
        </tr>
      </thead>
      <tbody>
        {% for e in escalations %}
        <tr data-status="{{ e.status }}" data-reason="{{ e.reason }}" id="row-{{ e.ref_id }}">
          <td><span class="ref-id">{{ e.ref_id }}</span></td>
          <td>{{ e.caller_name or 'Unknown' }}</td>
          <td>
            {% if e.reason == 'fraud_report' %}
              <span class="badge badge-fraud">🚨 Fraud</span>
            {% else %}
              <span class="badge badge-scope">📋 Out of Scope</span>
            {% endif %}
          </td>
          <td><div class="summary-text">{{ e.situation_summary }}</div></td>
          <td><div class="checked-text">{{ e.what_agent_checked }}</div></td>
          <td><span class="badge badge-{{ e.urgency }}">{{ e.urgency|upper }}</span></td>
          <td>{{ e.caller_language }}</td>
          <td>{{ e.preferred_followup }}</td>
          <td id="status-{{ e.ref_id }}">
            <span class="badge badge-{{ e.status|replace('_','-') }}">{{ e.status|replace('_',' ')|title }}</span>
          </td>
          <td><span class="ts">{{ e.created_at[:16].replace('T', ' ') if e.created_at else '-' }}</span></td>
          <td>
            <div class="action-group" id="actions-{{ e.ref_id }}">
              {% if e.status != 'in_progress' and e.status != 'resolved' %}
              <button class="act-btn in-prog" onclick="updateStatus('{{ e.ref_id }}', 'in_progress')">🔄 In Progress</button>
              {% endif %}
              {% if e.status != 'resolved' %}
              <button class="act-btn resolve" onclick="updateStatus('{{ e.ref_id }}', 'resolved')">✅ Resolve</button>
              {% endif %}
              {% if e.status == 'resolved' %}
              <button class="act-btn reopen" onclick="updateStatus('{{ e.ref_id }}', 'open')">↩ Reopen</button>
              {% endif %}
            </div>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% else %}
  <div class="empty">
    <div class="icon">✅</div>
    <h3>No escalations yet</h3>
    <p>All conversations are being handled by Dhan Rakshak. Escalation requests will appear here.</p>
  </div>
  {% endif %}
</main>

<div id="toast">Status updated</div>

<script>
  function filterRows(filter, btn) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('#esc-table tbody tr').forEach(row => {
      const st = row.dataset.status;
      const re = row.dataset.reason;
      if (filter === 'all') { row.style.display = ''; return; }
      if (filter === 'in-progress') { row.style.display = st === 'in_progress' ? '' : 'none'; return; }
      row.style.display = (st === filter || re === filter) ? '' : 'none';
    });
  }

  async function updateStatus(refId, newStatus) {
    const resp = await fetch('/update/' + refId, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({status: newStatus})
    });
    const data = await resp.json();
    if (data.success) {
      const label = newStatus.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      document.getElementById('status-' + refId).innerHTML =
        '<span class="badge badge-' + newStatus.replace('_','-') + '">' + label + '</span>';
      document.getElementById('row-' + refId).dataset.status = newStatus;

      let btns = '';
      if (newStatus !== 'in_progress' && newStatus !== 'resolved')
        btns += '<button class="act-btn in-prog" onclick="updateStatus(\'' + refId + '\', \'in_progress\')">🔄 In Progress</button>';
      if (newStatus !== 'resolved')
        btns += '<button class="act-btn resolve" onclick="updateStatus(\'' + refId + '\', \'resolved\')">✅ Resolve</button>';
      if (newStatus === 'resolved')
        btns += '<button class="act-btn reopen" onclick="updateStatus(\'' + refId + '\', \'open\')">↩ Reopen</button>';
      document.getElementById('actions-' + refId).innerHTML = btns;
      showToast('Status updated to ' + label);
    }
  }

  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
  }

  // Auto-refresh every 30 seconds
  setTimeout(() => window.location.reload(), 30000);
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Analytics HTML Template
# ---------------------------------------------------------------------------
ANALYTICS_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Dhan Rakshak – Call Analytics</title>
  <meta name="description" content="Call analytics dashboard showing total, successful, and failed calls for Dhan Rakshak voice agent." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4/dist/chart.umd.min.js"></script>
  <style>
    :root {
      --bg:       #0d0f1a;
      --surface:  #141726;
      --surface2: #1c2035;
      --border:   #252a40;
      --accent:   #6c63ff;
      --accent2:  #a78bfa;
      --text:     #e2e8f0;
      --muted:    #8892a4;
      --green:    #22c55e;
      --amber:    #f59e0b;
      --red:      #ef4444;
      --blue:     #3b82f6;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }

    nav {
      display: flex; align-items: center; justify-content: space-between;
      padding: 1rem 2rem; background: var(--surface);
      border-bottom: 1px solid var(--border);
      position: sticky; top: 0; z-index: 100;
    }
    .nav-brand { display: flex; align-items: center; gap: .75rem; }
    .nav-brand .logo {
      width: 38px; height: 38px;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem;
    }
    .nav-brand h1 { font-size: 1.1rem; font-weight: 700; }
    .nav-brand span { font-size: .75rem; color: var(--muted); }
    .nav-right { display: flex; align-items: center; gap: 1rem; }
    .refresh-btn {
      background: var(--surface2); border: 1px solid var(--border); color: var(--text);
      padding: .4rem .9rem; border-radius: 8px; font-size: .8rem; cursor: pointer;
      text-decoration: none; transition: background .2s;
    }
    .refresh-btn:hover { background: var(--border); }

    /* Tab bar */
    .tab-bar {
      display: flex; gap: .5rem; padding: .75rem 2rem;
      background: var(--surface); border-bottom: 1px solid var(--border);
    }
    .tab-link {
      padding: .4rem 1.1rem; border-radius: 8px; font-size: .82rem; font-weight: 600;
      text-decoration: none; color: var(--muted); transition: all .2s;
      border: 1px solid transparent;
    }
    .tab-link:hover { color: var(--text); border-color: var(--border); }
    .tab-link.active { background: var(--accent); color: #fff; border-color: var(--accent); }

    main { max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }

    h2.section-title {
      font-size: 1rem; font-weight: 600; color: var(--muted);
      text-transform: uppercase; letter-spacing: .08em;
      margin-bottom: 1rem;
    }

    /* KPI cards */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2.5rem;
    }
    .kpi-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 1.5rem 1.75rem;
      position: relative; overflow: hidden;
      transition: transform .25s, box-shadow .25s;
    }
    .kpi-card::before {
      content: '';
      position: absolute; top: 0; left: 0; right: 0; height: 3px;
      border-radius: 18px 18px 0 0;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0,0,0,.4); }
    .kpi-card .kpi-icon { font-size: 1.8rem; margin-bottom: .6rem; }
    .kpi-card .kpi-label { font-size: .75rem; text-transform: uppercase; letter-spacing: .07em; color: var(--muted); margin-bottom: .35rem; }
    .kpi-card .kpi-value { font-size: 3rem; font-weight: 800; line-height: 1; }
    .kpi-card .kpi-sub { font-size: .78rem; color: var(--muted); margin-top: .4rem; }

    .kpi-total::before   { background: linear-gradient(90deg, var(--accent), var(--accent2)); }
    .kpi-success::before { background: linear-gradient(90deg, #16a34a, var(--green)); }
    .kpi-failed::before  { background: linear-gradient(90deg, #b91c1c, var(--red)); }

    .kpi-total   .kpi-value { color: var(--accent2); }
    .kpi-success .kpi-value { color: var(--green); }
    .kpi-failed  .kpi-value { color: var(--red); }

    /* Chart + rate strip */
    .analytics-grid {
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }
    @media (max-width: 768px) { .analytics-grid { grid-template-columns: 1fr; } }

    .chart-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 1.5rem;
      display: flex; flex-direction: column; align-items: center; gap: 1rem;
    }
    .chart-card h3 { font-size: .82rem; text-transform: uppercase; letter-spacing: .07em; color: var(--muted); align-self: flex-start; }
    .chart-wrap { width: 220px; height: 220px; position: relative; }
    .rate-legend { display: flex; flex-direction: column; gap: .5rem; width: 100%; }
    .rate-row { display: flex; align-items: center; gap: .6rem; font-size: .82rem; }
    .rate-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

    .info-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 1.5rem;
    }
    .info-card h3 { font-size: .82rem; text-transform: uppercase; letter-spacing: .07em; color: var(--muted); margin-bottom: 1.25rem; }
    .rate-bar-wrap { margin-bottom: 1.2rem; }
    .rate-bar-label { display: flex; justify-content: space-between; font-size: .82rem; margin-bottom: .4rem; }
    .rate-bar-track { height: 8px; background: var(--surface2); border-radius: 999px; overflow: hidden; }
    .rate-bar-fill { height: 100%; border-radius: 999px; transition: width 1s ease; }
    .rate-bar-fill.success { background: linear-gradient(90deg, #16a34a, var(--green)); }
    .rate-bar-fill.failed  { background: linear-gradient(90deg, #b91c1c, var(--red)); }
    .rate-bar-fill.inprog  { background: linear-gradient(90deg, #b45309, var(--amber)); }

    .divider { height: 1px; background: var(--border); margin: 1.25rem 0; }

    .stat-row { display: flex; justify-content: space-between; align-items: center; padding: .5rem 0; font-size: .85rem; }
    .stat-row .sr-label { color: var(--muted); }
    .stat-row .sr-val   { font-weight: 600; }

    /* Recent calls table */
    .table-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; }
    table { width: 100%; border-collapse: collapse; }
    thead tr { background: var(--surface2); }
    th { padding: .85rem 1rem; font-size: .72rem; text-transform: uppercase; letter-spacing: .07em; color: var(--muted); font-weight: 600; text-align: left; }
    tbody tr { border-top: 1px solid var(--border); transition: background .15s; }
    tbody tr:hover { background: var(--surface2); }
    td { padding: .85rem 1rem; font-size: .86rem; vertical-align: middle; }

    .badge { display: inline-block; padding: .22rem .65rem; border-radius: 6px; font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
    .badge-success  { background: rgba(34,197,94,.15);  color: var(--green); }
    .badge-failed   { background: rgba(239,68,68,.15);  color: var(--red); }
    .badge-inprog   { background: rgba(245,158,11,.15); color: var(--amber); }
    .badge-browser  { background: rgba(59,130,246,.12); color: var(--blue); }
    .badge-sip      { background: rgba(107,99,255,.12); color: var(--accent2); }

    .ts { color: var(--muted); font-size: .78rem; }
    .call-id { font-family: 'Courier New', monospace; font-size: .78rem; color: var(--muted); max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .duration-val { font-weight: 600; }

    .empty { text-align: center; padding: 4rem 2rem; color: var(--muted); }
    .empty .icon { font-size: 3rem; margin-bottom: 1rem; }
    .empty h3 { font-size: 1.1rem; margin-bottom: .4rem; color: var(--text); }

    .live-dot {
      display: inline-block; width: 8px; height: 8px;
      background: var(--green); border-radius: 50%;
      animation: pulse 2s infinite;
      margin-right: .4rem;
      vertical-align: middle;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50%       { opacity: .5; transform: scale(1.3); }
    }
  </style>
</head>
<body>

<nav>
  <div class="nav-brand">
    <div class="logo">📊</div>
    <div>
      <h1>Dhan Rakshak</h1>
      <span>Call Analytics Dashboard</span>
    </div>
  </div>
  <div class="nav-right">
    <span style="font-size:.8rem;color:var(--muted);"><span class="live-dot"></span>Live • auto-refreshes</span>
    <a class="refresh-btn" href="/analytics">⟳ Refresh</a>
  </div>
</nav>

<div class="tab-bar">
  <a href="/" class="tab-link">🛡️ Escalations</a>
  <a href="/analytics" class="tab-link active">📊 Call Analytics</a>
</div>

<main>

  <!-- KPI cards -->
  <h2 class="section-title">Overview</h2>
  <div class="kpi-grid">
    <div class="kpi-card kpi-total" id="card-total">
      <div class="kpi-icon">📞</div>
      <div class="kpi-label">Total Calls</div>
      <div class="kpi-value" id="kpi-total">{{ stats.total }}</div>
      <div class="kpi-sub">All calls tracked by Dhan Rakshak</div>
    </div>
    <div class="kpi-card kpi-success" id="card-success">
      <div class="kpi-icon">✅</div>
      <div class="kpi-label">Successful Calls</div>
      <div class="kpi-value" id="kpi-success">{{ stats.successful }}</div>
      <div class="kpi-sub">Caller received eligibility result or document list</div>
    </div>
    <div class="kpi-card kpi-failed" id="card-failed">
      <div class="kpi-icon">❌</div>
      <div class="kpi-label">Failed Calls</div>
      <div class="kpi-value" id="kpi-failed">{{ stats.failed }}</div>
      <div class="kpi-sub">Call ended before completing the objective</div>
    </div>
  </div>

  <!-- Chart + rates -->
  <h2 class="section-title">Outcome Breakdown</h2>
  <div class="analytics-grid">
    <div class="chart-card">
      <h3>🎯 Success vs Failure</h3>
      <div class="chart-wrap">
        <canvas id="outcomeChart"></canvas>
      </div>
      <div class="rate-legend">
        <div class="rate-row"><div class="rate-dot" style="background:var(--green)"></div><span>Successful — {{ stats.successful }}</span></div>
        <div class="rate-row"><div class="rate-dot" style="background:var(--red)"></div><span>Failed — {{ stats.failed }}</span></div>
        <div class="rate-row"><div class="rate-dot" style="background:var(--amber)"></div><span>In Progress — {{ stats.in_progress }}</span></div>
      </div>
    </div>

    <div class="info-card">
      <h3>📊 Rate Breakdown</h3>

      <div class="rate-bar-wrap">
        <div class="rate-bar-label">
          <span>✅ Success Rate</span>
          <strong id="pct-success">{{ success_pct }}%</strong>
        </div>
        <div class="rate-bar-track">
          <div class="rate-bar-fill success" id="bar-success" style="width:{{ success_pct }}%"></div>
        </div>
      </div>

      <div class="rate-bar-wrap">
        <div class="rate-bar-label">
          <span>❌ Failure Rate</span>
          <strong id="pct-failed">{{ failed_pct }}%</strong>
        </div>
        <div class="rate-bar-track">
          <div class="rate-bar-fill failed" id="bar-failed" style="width:{{ failed_pct }}%"></div>
        </div>
      </div>

      {% if stats.in_progress %}
      <div class="rate-bar-wrap">
        <div class="rate-bar-label">
          <span>⏳ In Progress</span>
          <strong id="pct-inprog">{{ inprog_pct }}%</strong>
        </div>
        <div class="rate-bar-track">
          <div class="rate-bar-fill inprog" id="bar-inprog" style="width:{{ inprog_pct }}%"></div>
        </div>
      </div>
      {% endif %}

      <div class="divider"></div>

      <div class="stat-row">
        <span class="sr-label">Total calls tracked</span>
        <span class="sr-val">{{ stats.total }}</span>
      </div>
      <div class="stat-row">
        <span class="sr-label">Success definition</span>
        <span class="sr-val" style="font-size:.76rem;color:var(--muted);text-align:right;max-width:220px;">
          Eligibility check or document list delivered
        </span>
      </div>
      <div class="stat-row">
        <span class="sr-label">Privacy</span>
        <span class="sr-val" style="font-size:.76rem;color:var(--muted);">No PII displayed</span>
      </div>
    </div>
  </div>

  <!-- Recent calls table -->
  <h2 class="section-title">Recent Calls</h2>
  {% if calls %}
  <div class="table-wrap">
    <table id="calls-table">
      <thead>
        <tr>
          <th>Room ID</th>
          <th>Type</th>
          <th>Started</th>
          <th>Duration</th>
          <th>Outcome</th>
          <th>Success Trigger</th>
        </tr>
      </thead>
      <tbody>
        {% for c in calls %}
        <tr>
          <td><span class="call-id" title="{{ c.call_id }}">{{ c.call_id }}</span></td>
          <td>
            {% if c.call_type == 'sip' %}
              <span class="badge badge-sip">📞 SIP</span>
            {% else %}
              <span class="badge badge-browser">🌐 Browser</span>
            {% endif %}
          </td>
          <td><span class="ts">{{ c.started_at[:16].replace('T', ' ') if c.started_at else '-' }}</span></td>
          <td>
            {% if c.ended_at and c.started_at %}
              <span class="duration-val">{{ c.duration_s }}s</span>
            {% else %}
              <span class="ts">⏳ active</span>
            {% endif %}
          </td>
          <td>
            {% if c.outcome == 'success' %}
              <span class="badge badge-success">✅ Success</span>
            {% elif c.outcome == 'failed' %}
              <span class="badge badge-failed">❌ Failed</span>
            {% else %}
              <span class="badge badge-inprog">⏳ In Progress</span>
            {% endif %}
          </td>
          <td><span class="ts">{{ c.success_trigger or '—' }}</span></td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% else %}
  <div class="empty">
    <div class="icon">📞</div>
    <h3>No calls recorded yet</h3>
    <p>Make a call through the browser agent or SIP to see analytics appear here.</p>
  </div>
  {% endif %}

</main>

<script>
  // Chart.js doughnut
  (function () {
    const ctx = document.getElementById('outcomeChart');
    if (!ctx) return;
    const success = {{ stats.successful }};
    const failed  = {{ stats.failed }};
    const inprog  = {{ stats.in_progress }};
    const total   = success + failed + inprog;

    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Successful', 'Failed', 'In Progress'],
        datasets: [{
          data: total > 0 ? [success, failed, inprog] : [1, 0, 0],
          backgroundColor: [
            'rgba(34,197,94,0.85)',
            'rgba(239,68,68,0.85)',
            'rgba(245,158,11,0.85)',
          ],
          borderColor: '#141726',
          borderWidth: 3,
          hoverOffset: 8,
        }],
      },
      options: {
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(ctx) {
                const val = ctx.raw;
                const pct = total > 0 ? Math.round(val / total * 100) : 0;
                return ` ${ctx.label}: ${val} (${pct}%)`;
              }
            }
          }
        },
        animation: { animateRotate: true, duration: 900 },
      },
    });
  })();

  // Live polling via /api/stats every 30 s
  async function pollStats() {
    try {
      const r = await fetch('/api/stats');
      const d = await r.json();
      document.getElementById('kpi-total').textContent   = d.total;
      document.getElementById('kpi-success').textContent = d.successful;
      document.getElementById('kpi-failed').textContent  = d.failed;

      const t = d.total || 1;
      const sp = Math.round(d.successful / t * 100);
      const fp = Math.round(d.failed / t * 100);

      const pctS = document.getElementById('pct-success');
      const pctF = document.getElementById('pct-failed');
      const barS = document.getElementById('bar-success');
      const barF = document.getElementById('bar-failed');
      if (pctS) { pctS.textContent = sp + '%'; barS.style.width = sp + '%'; }
      if (pctF) { pctF.textContent = fp + '%'; barF.style.width = fp + '%'; }
    } catch(e) {
      console.warn('Stats poll failed:', e);
    }
  }

  setInterval(pollStats, 30000);
  // Also full-reload every 60 s to refresh the calls table
  setTimeout(() => window.location.reload(), 60000);
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    db.init_db()
    escalations = db.get_all_escalations()
    open_count = sum(1 for e in escalations if e["status"] == "open")
    prog_count = sum(1 for e in escalations if e["status"] == "in_progress")
    done_count = sum(1 for e in escalations if e["status"] == "resolved")
    return render_template_string(
        DASHBOARD_HTML,
        escalations=escalations,
        open_count=open_count,
        prog_count=prog_count,
        done_count=done_count,
    )


@app.route("/analytics")
def analytics():
    db.init_db()
    stats = db.get_call_stats()
    raw_calls = db.get_recent_calls(limit=50)

    # Compute duration in seconds for display
    from datetime import datetime as dt
    calls = []
    for c in raw_calls:
        row = dict(c)
        if c["started_at"] and c["ended_at"]:
            try:
                start = dt.fromisoformat(c["started_at"])
                end   = dt.fromisoformat(c["ended_at"])
                row["duration_s"] = int((end - start).total_seconds())
            except Exception:
                row["duration_s"] = None
        else:
            row["duration_s"] = None
        calls.append(row)

    total = stats["total"] or 1  # avoid division by zero
    success_pct = round(stats["successful"] / total * 100)
    failed_pct  = round(stats["failed"]     / total * 100)
    inprog_pct  = round(stats["in_progress"] / total * 100)

    return render_template_string(
        ANALYTICS_HTML,
        stats=stats,
        calls=calls,
        success_pct=success_pct,
        failed_pct=failed_pct,
        inprog_pct=inprog_pct,
    )


@app.route("/api/stats")
def api_stats():
    """JSON endpoint for live KPI polling from the analytics page."""
    db.init_db()
    return jsonify(db.get_call_stats())


@app.route("/update/<ref_id>", methods=["POST"])
def update_status(ref_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "open")
    allowed = {"open", "in_progress", "resolved"}
    if new_status not in allowed:
        return jsonify({"success": False, "error": "Invalid status"}), 400
    updated = db.update_escalation_status(ref_id, new_status)
    return jsonify({"success": updated, "ref_id": ref_id, "status": new_status})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    db.init_db()
    print("\n" + "=" * 55)
    print("  Shield  Dhan Rakshak – Escalation Dashboard")
    print("  Escalations:  http://localhost:5050/")
    print("  Analytics:    http://localhost:5050/analytics")
    print("  Stats API:    http://localhost:5050/api/stats")
    print("  Auto-refreshes every 30 seconds")
    print("=" * 55 + "\n")
    app.run(host="0.0.0.0", port=5050, debug=False)
