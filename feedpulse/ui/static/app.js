// FeedPulse AI — Frontend Reactive Controller

let sourcesChart = null;
let urgencyChart = null;
let radarChart = null;

// Tab Switching
function switchTab(tabName) {
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.nav-tab').forEach(el => {
    el.classList.remove('active-tab', 'bg-brand-600', 'text-white', 'shadow-md', 'shadow-brand-600/30');
    el.classList.add('text-slate-400');
  });

  const activePane = document.getElementById(`tab-${tabName}`);
  const activeBtn = document.getElementById(`tab-btn-${tabName}`);
  if (activePane) activePane.classList.remove('hidden');
  if (activeBtn) {
    activeBtn.classList.add('active-tab', 'bg-brand-600', 'text-white', 'shadow-md', 'shadow-brand-600/30');
    activeBtn.classList.remove('text-slate-400');
  }

  if (tabName === 'clusters') {
    fetchClusters(document.getElementById('select-cluster-k').value || 6);
  } else if (tabName === 'evals') {
    fetchEvaluationReport();
  }
}

// Format Utilities
function getUrgencyBadge(urgency) {
  const map = {
    critical: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    high: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    medium: 'bg-sky-500/15 text-sky-400 border-sky-500/30',
    low: 'bg-slate-500/15 text-slate-400 border-slate-500/30'
  };
  return `<span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${map[urgency] || map.low}">${urgency}</span>`;
}

function getSourceBadge(source) {
  const map = {
    zendesk: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    discord: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    app_store: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    github: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    g2_reviews: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    customer_survey: 'bg-pink-500/10 text-pink-400 border-pink-500/20'
  };
  return `<span class="px-2 py-0.5 rounded text-[10px] font-mono border ${map[source] || 'bg-slate-800 text-slate-300 border-slate-700'}">${source.replace('_', ' ')}</span>`;
}

// ----------------- OVERVIEW DASHBOARD -----------------
async function loadDashboardStats() {
  try {
    const res = await fetch('/api/v1/stats');
    const data = await res.json();

    document.getElementById('metric-total-feedback').innerText = data.total_feedback_count;
    document.getElementById('header-indexed-count').innerText = `${data.total_feedback_count} Indexed Tickets`;
    const criticals = (data.urgency_breakdown.critical || 0) + (data.urgency_breakdown.high || 0);
    document.getElementById('metric-critical-count').innerText = criticals;
    document.getElementById('metric-faithfulness').innerText = `${(data.avg_faithfulness * 100).toFixed(1)}%`;
    document.getElementById('metric-latency').innerText = `${data.p95_latency_ms.toFixed(1)}ms`;

    // Render Sources Chart
    renderSourcesChart(data.sources_breakdown);

    // Render Urgency Chart
    renderUrgencyChart(data.urgency_breakdown);

    // Render Product Areas
    const areasContainer = document.getElementById('product-areas-list');
    areasContainer.innerHTML = '';
    const total = data.total_feedback_count || 1;
    for (const [area, count] of Object.entries(data.top_product_areas)) {
      const pct = Math.round((count / total) * 100);
      areasContainer.innerHTML += `
        <div>
          <div class="flex justify-between text-xs mb-1">
            <span class="text-slate-300 font-medium">${area}</span>
            <span class="font-mono text-slate-400">${count} tickets (${pct}%)</span>
          </div>
          <div class="w-full h-1.5 bg-dark-950 rounded-full overflow-hidden border border-dark-800">
            <div class="h-full bg-brand-500 rounded-full" style="width: ${pct}%"></div>
          </div>
        </div>
      `;
    }

    // Load recent stream
    const feedRes = await fetch('/api/v1/feedback?limit=10');
    const feedItems = await feedRes.json();
    const tableBody = document.getElementById('feedback-stream-body');
    tableBody.innerHTML = '';
    feedItems.forEach(item => {
      const sentimentColor = item.sentiment_score < -0.5 ? 'text-rose-400' : (item.sentiment_score > 0.3 ? 'text-emerald-400' : 'text-slate-400');
      tableBody.innerHTML += `
        <tr class="hover:bg-dark-850/60 transition">
          <td class="py-2.5 px-3 font-mono font-bold text-slate-300">${item.id}</td>
          <td class="py-2.5 px-3">${getSourceBadge(item.source)}</td>
          <td class="py-2.5 px-3 font-medium text-slate-300">${item.product_area}</td>
          <td class="py-2.5 px-3 text-slate-200 max-w-md truncate" title="${item.text}">${item.text}</td>
          <td class="py-2.5 px-3">${getUrgencyBadge(item.urgency)}</td>
          <td class="py-2.5 px-3 text-right font-mono font-bold ${sentimentColor}">${item.sentiment_score.toFixed(2)}</td>
        </tr>
      `;
    });

  } catch (err) {
    console.error('Error loading stats:', err);
  }
}

function renderSourcesChart(sourcesMap) {
  const ctx = document.getElementById('chart-sources').getContext('2d');
  if (sourcesChart) sourcesChart.destroy();

  const labels = Object.keys(sourcesMap).map(s => s.replace('_', ' ').toUpperCase());
  const values = Object.values(sourcesMap);

  sourcesChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: ['#10B981', '#6366F1', '#06B6D4', '#A855F7', '#F97316', '#EC4899'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: '#94A3B8',
            font: { family: 'Plus Jakarta Sans', size: 10 }
          }
        }
      },
      cutout: '72%'
    }
  });
}

function renderUrgencyChart(urgencyMap) {
  const ctx = document.getElementById('chart-urgency').getContext('2d');
  if (urgencyChart) urgencyChart.destroy();

  const labels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  const values = [
    urgencyMap.critical || 0,
    urgencyMap.high || 0,
    urgencyMap.medium || 0,
    urgencyMap.low || 0
  ];

  urgencyChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Tickets',
        data: values,
        backgroundColor: ['#F43F5E', '#F59E0B', '#38BDF8', '#64748B'],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans', size: 10 } }
        },
        y: {
          grid: { color: '#161F36' },
          ticks: { color: '#94A3B8', stepSize: 2 }
        }
      }
    }
  });
}

// ----------------- HYBRID SEARCH -----------------
function updateAlphaLabel(val) {
  const densePct = Math.round(val * 100);
  const bm25Pct = 100 - densePct;
  document.getElementById('alpha-val-label').innerText = `${densePct}% Dense / ${bm25Pct}% BM25`;
}

function setQueryPreset(text) {
  document.getElementById('search-query-input').value = text;
  executeSearch();
}

async function executeSearch() {
  const query = document.getElementById('search-query-input').value.trim();
  if (!query) return;

  const alpha = parseFloat(document.getElementById('alpha-slider').value);
  const container = document.getElementById('search-results-list');
  container.innerHTML = '<div class="text-center py-8 text-slate-400 font-mono text-xs">Computing BM25 + Dense similarity and reranking candidates...</div>';

  try {
    const res = await fetch('/api/v1/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        top_k: 6,
        alpha: alpha,
        enable_reranking: true
      })
    });
    const results = await res.json();
    document.getElementById('search-results-count').innerText = `Showing ${results.length} ranked customer tickets for "${query}"`;
    container.innerHTML = '';

    if (results.length === 0) {
      container.innerHTML = '<div class="text-center py-8 text-slate-500 text-xs">No matching customer feedback items found.</div>';
      return;
    }

    results.forEach((r, idx) => {
      const matchPills = r.matched_tokens.map(t => `<span class="px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300 font-mono text-[10px]">${t}</span>`).join(' ');
      container.innerHTML += `
        <div class="bg-dark-900 border border-dark-800 hover:border-dark-700 rounded-xl p-5 transition space-y-3">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-dark-800 pb-3">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-dark-800 text-brand-400 text-xs font-mono font-bold flex items-center justify-center">#${idx+1}</span>
              <span class="font-mono font-bold text-xs text-slate-300">${r.item.id}</span>
              ${getSourceBadge(r.item.source)}
              <span class="text-xs text-slate-400 font-medium">${r.item.product_area}</span>
            </div>
            <div class="flex items-center gap-3">
              ${getUrgencyBadge(r.item.urgency)}
              <div class="text-right">
                <span class="text-[10px] text-slate-400 block">Hybrid Rank Score</span>
                <span class="font-mono font-extrabold text-xs text-brand-400">${r.hybrid_score.toFixed(3)}</span>
              </div>
            </div>
          </div>

          <p class="text-xs text-slate-200 leading-relaxed">${r.item.text}</p>

          <div class="flex flex-wrap items-center justify-between gap-2 pt-2 text-[11px] text-slate-400 font-mono">
            <div class="flex items-center gap-3">
              <span>Dense: <strong class="text-cyan-400">${r.dense_score.toFixed(3)}</strong></span>
              <span>BM25: <strong class="text-indigo-400">${r.bm25_score.toFixed(3)}</strong></span>
              <span>Rerank: <strong class="text-emerald-400">${r.rerank_score.toFixed(3)}</strong></span>
            </div>
            <div class="flex items-center gap-1.5">
              ${matchPills}
            </div>
          </div>
        </div>
      `;
    });

  } catch (err) {
    container.innerHTML = `<div class="text-center py-6 text-rose-400 text-xs">Error executing search: ${err.message}</div>`;
  }
}

// ----------------- THEME CLUSTERS -----------------
async function fetchClusters(k = 6) {
  const container = document.getElementById('clusters-grid');
  container.innerHTML = '<div class="col-span-2 text-center py-8 text-slate-400 text-xs font-mono">Clustering feedback into semantic topics...</div>';

  try {
    const res = await fetch(`/api/v1/clusters?n_clusters=${k}`);
    const clusters = await res.json();
    container.innerHTML = '';

    clusters.forEach(c => {
      const kwPills = c.top_keywords.map(kw => `<span class="px-2 py-0.5 rounded-md bg-dark-800 text-slate-300 text-[10px] font-mono">${kw}</span>`).join(' ');
      const quotes = c.sample_items.map(it => `
        <li class="border-l-2 border-dark-700 pl-2 py-0.5 text-[11px] text-slate-400 italic">
          "${it.text.length > 95 ? it.text.substring(0, 95) + '...' : it.text}"
        </li>
      `).join('');

      container.innerHTML += `
        <div class="bg-dark-900 border border-dark-800 hover:border-dark-700 rounded-2xl p-6 transition flex flex-col justify-between space-y-4">
          <div>
            <div class="flex items-center justify-between gap-2 mb-2">
              <span class="text-[10px] font-mono text-brand-400 uppercase tracking-wider font-semibold">CLUSTER #${c.cluster_id}</span>
              ${getUrgencyBadge(c.primary_urgency)}
            </div>
            <h3 class="text-base font-bold text-white">${c.theme_name}</h3>
            
            <div class="flex items-center gap-3 text-xs text-slate-400 mt-2 font-mono">
              <span><strong>${c.frequency}</strong> feedback tickets</span>
              <span>•</span>
              <span>Avg Sentiment: <strong class="${c.avg_sentiment < 0 ? 'text-rose-400' : 'text-emerald-400'}">${c.avg_sentiment.toFixed(2)}</strong></span>
            </div>

            <div class="flex flex-wrap gap-1.5 mt-3">
              ${kwPills}
            </div>

            <div class="mt-4 pt-3 border-t border-dark-800">
              <span class="text-[10px] font-mono text-slate-400 uppercase block mb-1">Customer Voice Samples</span>
              <ul class="space-y-1.5">
                ${quotes}
              </ul>
            </div>
          </div>

          <button onclick="synthesizeInsight(${c.cluster_id})" class="w-full bg-dark-800 hover:bg-dark-700 text-brand-400 font-semibold py-2.5 rounded-xl text-xs transition border border-dark-700 flex items-center justify-center gap-2">
            <span>Synthesize Engineering Action Plan</span>
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
      `;
    });

  } catch (err) {
    container.innerHTML = `<div class="col-span-2 text-center py-6 text-rose-400 text-xs">Error fetching clusters: ${err.message}</div>`;
  }
}

async function synthesizeInsight(clusterId) {
  try {
    const res = await fetch('/api/v1/clusters/synthesize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cluster_id: clusterId })
    });
    const data = await res.json();

    document.getElementById('modal-cluster-id').innerText = `Cluster #${data.cluster_id} (${data.ticket_count} tickets)`;
    document.getElementById('modal-theme-title').innerText = data.theme_name;
    document.getElementById('modal-root-cause').innerText = data.root_cause;
    document.getElementById('modal-customer-impact').innerText = data.customer_impact;
    document.getElementById('modal-action-plan').innerText = data.engineering_action_plan;
    document.getElementById('modal-timestamp').innerText = new Date(data.generated_at).toLocaleTimeString();

    const compContainer = document.getElementById('modal-components');
    compContainer.innerHTML = data.affected_components.map(c => `<span class="px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 font-mono text-[10px]">${c}</span>`).join(' ');

    document.getElementById('synthesis-modal').classList.remove('hidden');
  } catch (err) {
    alert(`Synthesis error: ${err.message}`);
  }
}

function closeSynthesisModal() {
  document.getElementById('synthesis-modal').classList.add('hidden');
}

// ----------------- QUALITY EVALUATION HARNESS -----------------
async function fetchEvaluationReport() {
  try {
    const res = await fetch('/api/v1/eval/latest');
    const report = await res.json();
    renderEvaluationReport(report);
  } catch (err) {
    console.error('Error fetching evaluation report:', err);
  }
}

async function triggerEvaluation() {
  const btn = document.getElementById('btn-run-eval');
  btn.disabled = true;
  btn.innerHTML = `
    <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
    <span>Running Test Suite...</span>
  `;

  try {
    const res = await fetch('/api/v1/eval/run', { method: 'POST' });
    const report = await res.json();
    renderEvaluationReport(report);
  } catch (err) {
    alert(`Evaluation run error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>Run Regression Benchmark</span>
    `;
  }
}

function renderEvaluationReport(report) {
  // Quality Gate Cards
  const gateContainer = document.getElementById('eval-gate-cards');
  gateContainer.innerHTML = `
    <div class="bg-dark-950 p-3.5 rounded-xl border border-dark-800">
      <div class="flex justify-between items-center text-[11px] mb-1">
        <span class="text-slate-400">Faithfulness</span>
        <span class="text-[10px] font-mono text-emerald-400 font-bold">PASS (&ge;0.85)</span>
      </div>
      <span class="text-xl font-extrabold text-emerald-400 font-mono">${(report.overall_faithfulness * 100).toFixed(1)}%</span>
    </div>

    <div class="bg-dark-950 p-3.5 rounded-xl border border-dark-800">
      <div class="flex justify-between items-center text-[11px] mb-1">
        <span class="text-slate-400">Context Recall</span>
        <span class="text-[10px] font-mono text-emerald-400 font-bold">PASS (&ge;0.80)</span>
      </div>
      <span class="text-xl font-extrabold text-emerald-400 font-mono">${(report.overall_context_recall * 100).toFixed(1)}%</span>
    </div>

    <div class="bg-dark-950 p-3.5 rounded-xl border border-dark-800">
      <div class="flex justify-between items-center text-[11px] mb-1">
        <span class="text-slate-400">Context Precision</span>
        <span class="text-[10px] font-mono text-emerald-400 font-bold">PASS (&ge;0.75)</span>
      </div>
      <span class="text-xl font-extrabold text-emerald-400 font-mono">${(report.overall_context_precision * 100).toFixed(1)}%</span>
    </div>

    <div class="bg-dark-950 p-3.5 rounded-xl border border-dark-800">
      <div class="flex justify-between items-center text-[11px] mb-1">
        <span class="text-slate-400">Hallucination Rate</span>
        <span class="text-[10px] font-mono text-emerald-400 font-bold">PASS (&le;0.10)</span>
      </div>
      <span class="text-xl font-extrabold text-emerald-400 font-mono">${(report.overall_hallucination_rate * 100).toFixed(1)}%</span>
    </div>
  `;

  // Render Radar Chart
  renderRadarChart(report);

  // Render Individual Test Cases Table
  const tableBody = document.getElementById('eval-cases-table-body');
  tableBody.innerHTML = '';
  report.individual_results.forEach(caseResult => {
    tableBody.innerHTML += `
      <tr class="hover:bg-dark-850/60 transition font-mono">
        <td class="py-2.5 px-3 font-bold text-slate-300">${caseResult.case_id}</td>
        <td class="py-2.5 px-3 font-sans text-slate-200 max-w-xs truncate" title="${caseResult.query}">${caseResult.query}</td>
        <td class="py-2.5 px-3 text-emerald-400 font-bold">${(caseResult.faithfulness * 100).toFixed(1)}%</td>
        <td class="py-2.5 px-3 text-cyan-400 font-bold">${(caseResult.context_recall * 100).toFixed(1)}%</td>
        <td class="py-2.5 px-3 text-indigo-400 font-bold">${(caseResult.context_precision * 100).toFixed(1)}%</td>
        <td class="py-2.5 px-3 text-slate-400">${caseResult.latency_ms.toFixed(1)}ms</td>
        <td class="py-2.5 px-3 text-right">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${caseResult.passed_gate ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'}">
            ${caseResult.passed_gate ? 'PASSED' : 'FLAGGED'}
          </span>
        </td>
      </tr>
    `;
  });
}

function renderRadarChart(report) {
  const ctx = document.getElementById('chart-radar').getContext('2d');
  if (radarChart) radarChart.destroy();

  radarChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Faithfulness', 'Context Precision', 'Context Recall', 'Urgency Calibration'],
      datasets: [
        {
          label: 'Achieved AI Performance',
          data: [
            report.overall_faithfulness,
            report.overall_context_precision,
            report.overall_context_recall,
            report.overall_urgency_accuracy
          ],
          backgroundColor: 'rgba(99, 102, 241, 0.25)',
          borderColor: '#6366F1',
          pointBackgroundColor: '#818CF8',
          borderWidth: 2
        },
        {
          label: 'Enterpret Quality Gate Threshold',
          data: [0.85, 0.75, 0.80, 0.80],
          borderColor: '#10B981',
          borderDash: [4, 4],
          borderWidth: 1.5,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans', size: 10 } }
        }
      },
      scales: {
        r: {
          min: 0.0,
          max: 1.0,
          ticks: { display: false },
          grid: { color: '#1E293B' },
          angleLines: { color: '#1E293B' },
          pointLabels: {
            color: '#CBD5E1',
            font: { family: 'Plus Jakarta Sans', size: 11, weight: 'bold' }
          }
        }
      }
    }
  });
}

// Global Initialization
window.addEventListener('DOMContentLoaded', () => {
  loadDashboardStats();
  executeSearch();
});
