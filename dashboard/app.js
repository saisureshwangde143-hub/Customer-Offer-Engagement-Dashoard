/* RewardsNext — Customer Offer Engagement Dashboard
   Vanilla JS, no build step, no dependencies. All aggregation runs client-side
   over the pre-built cube in data/data.js. */

(function () {
  'use strict';

  const D = window.RN_DATA;
  if (!D) { document.getElementById('page').innerHTML = '<p class="empty">data/data.js failed to load.</p>'; return; }

  /* ---------- column indexes ---------- */
  const ci = {}; D.cubeCols.forEach((c, i) => ci[c] = i);
  const cc = {}; D.custCols.forEach((c, i) => cc[c] = i);
  const ti = {}; D.txnCols.forEach((c, i) => ti[c] = i);
  const bi = {}; D.baCols.forEach((c, i) => bi[c] = i);
  const pi = {}; D.compCols.forEach((c, i) => pi[c] = i);

  const OFFERS = D.offers;
  const ALL_CHANNELS = ['email', 'mobile', 'social', 'web'];
  const OFFER_TYPES = ['bogo', 'discount', 'informational'];

  /* ---------- filter state ---------- */
  const state = {
    page: 'overview',
    offerType: new Set(),
    channel: new Set(),
    age: new Set(),
    income: new Set(),
    gender: new Set(),
    tenure: new Set(),
    completeOnly: true
  };

  /* ---------- helpers ---------- */
  const fmt = n => n.toLocaleString('en-US');
  const money = n => '$' + n.toLocaleString('en-US', { maximumFractionDigits: 0 });
  const money2 = n => '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const pct = (n, dp) => (n * 100).toFixed(dp === undefined ? 1 : dp) + '%';
  const safeDiv = (a, b) => (b ? a / b : 0);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function activeOfferIdx() {
    const set = new Set();
    OFFERS.forEach(o => {
      if (state.offerType.size && !state.offerType.has(o.offer_type)) return;
      if (state.channel.size && !o.channels.some(c => state.channel.has(c))) return;
      set.add(o.oi);
    });
    return set;
  }

  function dimOk(row, idx) {
    if (state.completeOnly && row[idx.pc] !== 1) return false;
    if (state.age.size && !state.age.has(D.dims.age[row[idx.ai]])) return false;
    if (state.income.size && !state.income.has(D.dims.income[row[idx.ii]])) return false;
    if (state.gender.size && !state.gender.has(D.dims.gender[row[idx.gi]])) return false;
    if (state.tenure.size && !state.tenure.has(D.dims.tenure[row[idx.ti]])) return false;
    return true;
  }

  /* ---------- aggregation ---------- */
  function offerRows() {
    const oidx = activeOfferIdx();
    return D.cube.filter(r => oidx.has(r[ci.oi]) && dimOk(r, ci));
  }

  function totals(rows) {
    const t = { sent: 0, viewed: 0, completed: 0, promoSent: 0, influenced: 0, unviewed: 0, rewardCost: 0, wasted: 0, htc: 0 };
    for (const r of rows) {
      const n = r[ci.n], o = OFFERS[r[ci.oi]];
      t.sent += n;
      if (r[ci.v]) t.viewed += n;
      if (r[ci.c]) {
        t.completed += n;
        t.rewardCost += n * o.reward;
        t.htc += r[ci.htc];
      }
      if (!o.is_informational) t.promoSent += n;
      t.influenced += r[ci.iv];
      t.unviewed += r[ci.uc];
      t.wasted += r[ci.uc] * o.reward;
    }
    return t;
  }

  function custRows() { return D.cust.filter(r => dimOk(r, cc)); }
  function txnRows() { return D.txn.filter(r => dimOk(r, ti)); }

  function custTotals() {
    let n = 0, spend = 0, txns = 0;
    const bySeg = {};
    for (const r of custRows()) {
      n += r[cc.n]; spend += r[cc.spend]; txns += r[cc.txns];
      const s = D.dims.segment[r[cc.si]];
      if (!bySeg[s]) bySeg[s] = { customers: 0, spend: 0, txns: 0 };
      bySeg[s].customers += r[cc.n]; bySeg[s].spend += r[cc.spend]; bySeg[s].txns += r[cc.txns];
    }
    return { customers: n, spend, txns, bySeg };
  }

  /* ---------- svg chart builders ---------- */
  const PAL = { accent: 'var(--accent)', flag: 'var(--flag)', soft: 'var(--accent-soft)', dim: 'var(--ink-soft)' };

  function hBar(items, opts) {
    opts = opts || {};
    const labelW = opts.labelW || 150, rowH = 26, gap = 8, w = 560;
    const h = items.length * (rowH + gap);
    const max = opts.max || Math.max(...items.map(i => i.value), 0.0001);
    const barW = w - labelW - 70;
    let s = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(opts.alt || 'bar chart')}">`;
    items.forEach((it, k) => {
      const y = k * (rowH + gap);
      const bw = Math.max(1, (it.value / max) * barW);
      const color = it.flag ? PAL.flag : PAL.accent;
      s += `<text class="axis" x="0" y="${y + 17}">${esc(it.label)}</text>`;
      s += `<rect x="${labelW}" y="${y + 3}" width="${bw}" height="${rowH - 6}" rx="3" fill="${color}" opacity="${it.faded ? .4 : .9}"/>`;
      s += `<text class="vlabel" x="${labelW + bw + 8}" y="${y + 17}">${esc(it.display)}</text>`;
    });
    return s + '</svg>';
  }

  function funnel(stages) {
    const w = 560, rowH = 58, gap = 10, h = stages.length * (rowH + gap);
    const max = stages[0].value || 1;
    let s = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Offer funnel">`;
    stages.forEach((st, k) => {
      const y = k * (rowH + gap);
      const bw = Math.max(2, (st.value / max) * w);
      const x = (w - bw) / 2;
      s += `<rect x="${x}" y="${y}" width="${bw}" height="${rowH}" rx="5" fill="${PAL.accent}" opacity="${0.92 - k * 0.22}"/>`;
      s += `<text class="vlabel" x="${w / 2}" y="${y + 24}" text-anchor="middle" style="font-size:14px">${esc(st.label)}</text>`;
      s += `<text class="axis" x="${w / 2}" y="${y + 43}" text-anchor="middle">${fmt(st.value)} · ${pct(safeDiv(st.value, max))}</text>`;
    });
    return s + '</svg>';
  }

  function lineChart(points, opts) {
    opts = opts || {};
    const w = 560, h = 210, pad = { l: 46, r: 10, t: 10, b: 26 };
    if (!points.length) return '<p class="empty">No data in this selection.</p>';
    const xs = points.map(p => p.x), ys = points.map(p => p.y);
    const xmin = Math.min(...xs), xmax = Math.max(...xs);
    const ymax = Math.max(...ys) * 1.08 || 1;
    const px = x => pad.l + ((x - xmin) / (xmax - xmin || 1)) * (w - pad.l - pad.r);
    const py = y => h - pad.b - (y / ymax) * (h - pad.t - pad.b);
    let s = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(opts.alt || 'line chart')}">`;
    for (let g = 0; g <= 3; g++) {
      const v = (ymax / 3) * g, y = py(v);
      s += `<line class="gridline" x1="${pad.l}" y1="${y}" x2="${w - pad.r}" y2="${y}"/>`;
      s += `<text class="axis" x="${pad.l - 6}" y="${y + 3}" text-anchor="end">${opts.money ? money(v) : Math.round(v)}</text>`;
    }
    const d = points.map((p, k) => (k ? 'L' : 'M') + px(p.x).toFixed(1) + ' ' + py(p.y).toFixed(1)).join(' ');
    const area = d + ` L${px(xmax).toFixed(1)} ${h - pad.b} L${px(xmin).toFixed(1)} ${h - pad.b} Z`;
    s += `<path d="${area}" fill="${PAL.accent}" opacity=".10"/>`;
    s += `<path d="${d}" fill="none" stroke="${PAL.accent}" stroke-width="2" stroke-linejoin="round"/>`;
    s += `<text class="axis" x="${pad.l}" y="${h - 8}">${esc(opts.xlo || xmin)}</text>`;
    s += `<text class="axis" x="${w - pad.r}" y="${h - 8}" text-anchor="end">${esc(opts.xhi || xmax)}</text>`;
    return s + '</svg>';
  }

  function multiLine(series, opts) {
    opts = opts || {};
    const w = 560, h = 210, pad = { l: 46, r: 10, t: 10, b: 26 };
    const all = series.flatMap(s => s.points);
    if (!all.length) return '<p class="empty">No data in this selection.</p>';
    const xmin = Math.min(...all.map(p => p.x)), xmax = Math.max(...all.map(p => p.x));
    const ymax = Math.max(...all.map(p => p.y)) * 1.1 || 1;
    const px = x => pad.l + ((x - xmin) / (xmax - xmin || 1)) * (w - pad.l - pad.r);
    const py = y => h - pad.b - (y / ymax) * (h - pad.t - pad.b);
    let s = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(opts.alt || 'line chart')}">`;
    for (let g = 0; g <= 3; g++) {
      const v = (ymax / 3) * g, y = py(v);
      s += `<line class="gridline" x1="${pad.l}" y1="${y}" x2="${w - pad.r}" y2="${y}"/>`;
      s += `<text class="axis" x="${pad.l - 6}" y="${y + 3}" text-anchor="end">${opts.money ? money2(v) : Math.round(v)}</text>`;
    }
    series.forEach(se => {
      if (!se.points.length) return;
      const d = se.points.map((p, k) => (k ? 'L' : 'M') + px(p.x).toFixed(1) + ' ' + py(p.y).toFixed(1)).join(' ');
      s += `<path d="${d}" fill="none" stroke="${se.color}" stroke-width="2" stroke-dasharray="${se.dash || ''}" stroke-linejoin="round"/>`;
    });
    s += `<text class="axis" x="${pad.l}" y="${h - 8}">Day ${xmin}</text>`;
    s += `<text class="axis" x="${w - pad.r}" y="${h - 8}" text-anchor="end">Day ${xmax}</text>`;
    return s + '</svg>';
  }

  function scatter(pts, opts) {
    opts = opts || {};
    const w = 560, h = 260, pad = { l: 48, r: 16, t: 14, b: 38 };
    if (!pts.length) return '<p class="empty">No data in this selection.</p>';
    const xmax = Math.max(...pts.map(p => p.x)) * 1.12 || 1;
    const ymax = Math.max(...pts.map(p => p.y)) * 1.15 || 1;
    const rmax = Math.max(...pts.map(p => p.r)) || 1;
    const px = x => pad.l + (x / xmax) * (w - pad.l - pad.r);
    const py = y => h - pad.b - (y / ymax) * (h - pad.t - pad.b);
    let s = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(opts.alt || 'scatter plot')}">`;
    for (let g = 0; g <= 3; g++) {
      const v = (ymax / 3) * g, y = py(v);
      s += `<line class="gridline" x1="${pad.l}" y1="${y}" x2="${w - pad.r}" y2="${y}"/>`;
      s += `<text class="axis" x="${pad.l - 6}" y="${y + 3}" text-anchor="end">${pct(v, 0)}</text>`;
    }
    pts.forEach(p => {
      const r = 6 + (p.r / rmax) * 12;
      s += `<circle cx="${px(p.x).toFixed(1)}" cy="${py(p.y).toFixed(1)}" r="${r.toFixed(1)}" fill="${p.color}" opacity=".75"/>`;
      s += `<title>${esc(p.title)}</title>`;
    });
    s += `<text class="axis" x="${w / 2}" y="${h - 8}" text-anchor="middle">${esc(opts.xlabel || '')}</text>`;
    return s + '</svg>';
  }

  function heatmap(rowsLabels, colLabels, values) {
    const cellW = 74, cellH = 32, labelW = 78, headH = 24;
    const w = labelW + colLabels.length * cellW;
    const h = headH + rowsLabels.length * cellH;
    const flat = values.flat().filter(v => v !== null);
    const lo = Math.min(...flat, 0), hi = Math.max(...flat, 0.0001);
    let s = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Redemption rate by age and income">`;
    colLabels.forEach((c, j) => {
      s += `<text class="axis" x="${labelW + j * cellW + cellW / 2}" y="${headH - 8}" text-anchor="middle">${esc(c)}</text>`;
    });
    rowsLabels.forEach((rl, i) => {
      s += `<text class="axis" x="${labelW - 8}" y="${headH + i * cellH + cellH / 2 + 4}" text-anchor="end">${esc(rl)}</text>`;
      colLabels.forEach((c, j) => {
        const v = values[i][j];
        const x = labelW + j * cellW, y = headH + i * cellH;
        if (v === null) {
          s += `<rect x="${x + 1}" y="${y + 1}" width="${cellW - 3}" height="${cellH - 3}" rx="3" fill="var(--panel-alt)"/>`;
          s += `<text class="axis" x="${x + cellW / 2}" y="${y + cellH / 2 + 4}" text-anchor="middle">–</text>`;
        } else {
          const t = (v - lo) / (hi - lo || 1);
          s += `<rect x="${x + 1}" y="${y + 1}" width="${cellW - 3}" height="${cellH - 3}" rx="3" fill="${PAL.accent}" opacity="${(0.12 + t * 0.8).toFixed(2)}"/>`;
          s += `<text x="${x + cellW / 2}" y="${y + cellH / 2 + 4}" text-anchor="middle" style="font-size:11px;font-weight:600;fill:${t > 0.55 ? '#fff' : 'var(--ink)'}">${pct(v, 0)}</text>`;
        }
      });
    });
    return s + '</svg>';
  }

  function barTable(rows, head) {
    const max = Math.max(...rows.map(r => r.bar), 0.0001);
    let s = `<table><thead><tr>${head.map((h, i) => `<th${i ? ' class="n"' : ''}>${esc(h)}</th>`).join('')}</tr></thead><tbody>`;
    rows.forEach(r => {
      s += '<tr>';
      s += `<td class="bar-cell"><i style="width:${((r.bar / max) * 100).toFixed(1)}%"></i><span>${esc(r.label)}</span></td>`;
      r.cells.forEach(c => { s += `<td class="n">${esc(c)}</td>`; });
      s += '</tr>';
    });
    return s + '</tbody></table>';
  }

  /* ---------- pages ---------- */
  const PAGES = [
    { id: 'overview', name: 'Overview', render: pageOverview },
    { id: 'funnel', name: 'Offer Funnel', render: pageFunnel },
    { id: 'segments', name: 'Segmentation', render: pageSegments },
    { id: 'performance', name: 'Offer Performance', render: pagePerformance },
    { id: 'spend', name: 'Transaction Behaviour', render: pageSpend }
  ];

  function kpi(num, label, flag) {
    return `<div class="kpi${flag ? ' flag' : ''}"><span class="num">${esc(num)}</span><span class="lbl">${esc(label)}</span></div>`;
  }

  function pageOverview() {
    const t = totals(offerRows());
    const ct = custTotals();
    const txs = txnRows();
    let spend = 0, n = 0;
    const byDay = new Map();
    for (const r of txs) {
      spend += r[ti.amt]; n += r[ti.n];
      const d = r[ti.day];
      byDay.set(d, (byDay.get(d) || 0) + r[ti.amt]);
    }
    const days = [...byDay.keys()].sort((a, b) => a - b).map(d => ({ x: d, y: byDay.get(d) }));

    const byType = {};
    for (const r of offerRows()) {
      const ty = OFFERS[r[ci.oi]].offer_type;
      byType[ty] = byType[ty] || { sent: 0, viewed: 0, completed: 0 };
      byType[ty].sent += r[ci.n];
      if (r[ci.v]) byType[ty].viewed += r[ci.n];
      if (r[ci.c]) byType[ty].completed += r[ci.n];
    }

    return `
      <div class="kpis">
        ${kpi(fmt(ct.customers), 'Customers in selection')}
        ${kpi(fmt(t.sent), 'Offers sent')}
        ${kpi(fmt(t.completed), 'Offers completed')}
        ${kpi(pct(safeDiv(t.completed, t.promoSent)), 'Redemption rate (excl. informational)')}
        ${kpi(n ? money2(spend / n) : '—', 'Average transaction')}
      </div>
      <div class="grid g2">
        <div class="panel">
          <h3>Spend across the window</h3>
          <p class="sub">Total transaction value per day, ${fmt(n)} transactions</p>
          ${lineChart(days, { money: true, xlo: 'Day 0', xhi: 'Day 29', alt: 'Daily spend' })}
        </div>
        <div class="panel">
          <h3>Engagement by offer type</h3>
          <p class="sub">Sent, viewed and completed</p>
          ${barTable(
            OFFER_TYPES.filter(ty => byType[ty]).map(ty => ({
              label: ty.charAt(0).toUpperCase() + ty.slice(1),
              bar: byType[ty].sent,
              cells: [fmt(byType[ty].sent), fmt(byType[ty].viewed),
                      ty === 'informational' ? '—' : fmt(byType[ty].completed),
                      ty === 'informational' ? 'n/a' : pct(safeDiv(byType[ty].completed, byType[ty].sent))]
            })),
            ['Offer type', 'Sent', 'Viewed', 'Completed', 'Redemption'])}
          <p class="note">Informational offers carry no spend threshold, so they can never be completed.
          They are excluded from every redemption denominator on this dashboard.</p>
        </div>
      </div>
      <div class="grid g2">
        <div class="callout">
          <h3>The headline denominator matters</h3>
          <p>Redemption here is <b>${pct(safeDiv(t.completed, t.promoSent))}</b> — completions over
          <b>promotional</b> offers sent. Dividing by all offers sent instead gives
          ${pct(safeDiv(t.completed, t.sent))}, which understates performance by
          ${((safeDiv(t.completed, t.promoSent) - safeDiv(t.completed, t.sent)) * 100).toFixed(1)} points.</p>
        </div>
        <div class="panel">
          <h3>Revenue concentration</h3>
          <p class="sub">Share of spend by engagement segment</p>
          ${barTable(
            Object.entries(ct.bySeg).sort((a, b) => b[1].spend - a[1].spend).map(([k, v]) => ({
              label: k, bar: v.spend,
              cells: [fmt(v.customers), money(v.spend), pct(safeDiv(v.spend, ct.spend))]
            })),
            ['Segment', 'Customers', 'Spend', 'Share'])}
        </div>
      </div>`;
  }

  function pageFunnel() {
    const rows = offerRows();
    const t = totals(rows);
    const byType = {};
    for (const r of rows) {
      const o = OFFERS[r[ci.oi]];
      if (o.is_informational) continue;
      byType[o.offer_type] = byType[o.offer_type] || { sent: 0, viewed: 0, completed: 0 };
      byType[o.offer_type].sent += r[ci.n];
      if (r[ci.v]) byType[o.offer_type].viewed += r[ci.n];
      if (r[ci.c]) byType[o.offer_type].completed += r[ci.n];
    }

    return `
      <div class="kpis">
        ${kpi(pct(safeDiv(t.viewed, t.sent)), 'View rate')}
        ${kpi(pct(safeDiv(t.completed, t.promoSent)), 'Redemption rate')}
        ${kpi(pct(safeDiv(t.influenced, t.promoSent)), 'Influenced redemption (viewed, then completed)')}
        ${kpi(pct(safeDiv(t.unviewed, t.completed)), 'Completions with no view', true)}
        ${kpi(money(t.wasted), 'Reward paid on unviewed completions', true)}
      </div>
      <div class="grid g2">
        <div class="panel">
          <h3>Received → Viewed → Completed</h3>
          <p class="sub">All offers in the current selection</p>
          ${funnel([
            { label: 'Offer received', value: t.sent },
            { label: 'Offer viewed', value: t.viewed },
            { label: 'Offer completed', value: t.completed }
          ])}
        </div>
        <div class="panel">
          <h3>Where the reward actually goes</h3>
          <p class="sub">Completions split by whether the customer ever opened the offer</p>
          ${hBar([
            { label: 'Influenced', value: t.influenced, display: fmt(t.influenced) + ' · ' + pct(safeDiv(t.influenced, t.completed)) },
            { label: 'Never viewed', value: t.unviewed, display: fmt(t.unviewed) + ' · ' + pct(safeDiv(t.unviewed, t.completed)), flag: true }
          ], { labelW: 110, alt: 'Influenced versus unviewed completions' })}
          <p class="note"><b>${pct(safeDiv(t.unviewed, t.completed))}</b> of completions came from customers
          who never opened the offer. They met the spend threshold on their own, the reward paid out, and no
          marketing influence occurred — ${money(t.wasted)} in this selection.</p>
        </div>
      </div>
      <div class="panel">
        <h3>Funnel by offer type</h3>
        <p class="sub">Promotional offers only</p>
        ${barTable(
          Object.entries(byType).map(([k, v]) => ({
            label: k.charAt(0).toUpperCase() + k.slice(1), bar: v.completed / (v.sent || 1),
            cells: [fmt(v.sent), pct(safeDiv(v.viewed, v.sent)), fmt(v.completed), pct(safeDiv(v.completed, v.sent))]
          })),
          ['Offer type', 'Sent', 'View rate', 'Completed', 'Redemption'])}
      </div>`;
  }

  function segBreak(dimKey, dimList, idxKey) {
    const rows = offerRows();
    const acc = {};
    dimList.forEach(v => acc[v] = { sent: 0, promo: 0, viewed: 0, completed: 0 });
    for (const r of rows) {
      const key = D.dims[dimKey][r[ci[idxKey]]];
      if (!acc[key]) continue;
      const o = OFFERS[r[ci.oi]];
      acc[key].sent += r[ci.n];
      if (!o.is_informational) acc[key].promo += r[ci.n];
      if (r[ci.v]) acc[key].viewed += r[ci.n];
      if (r[ci.c]) acc[key].completed += r[ci.n];
    }
    return dimList.filter(v => acc[v].sent > 0).map(v => ({
      label: v, bar: safeDiv(acc[v].completed, acc[v].promo),
      cells: [fmt(acc[v].sent), pct(safeDiv(acc[v].viewed, acc[v].sent)), pct(safeDiv(acc[v].completed, acc[v].promo))]
    }));
  }

  function pageSegments() {
    const rows = offerRows();
    const ages = D.dims.age.filter(a => a !== 'Unknown' || !state.completeOnly);
    const incs = D.dims.income.filter(i => i !== 'Unknown' || !state.completeOnly);
    const grid = ages.map(() => incs.map(() => ({ promo: 0, completed: 0 })));
    const ai = {}, ii = {};
    ages.forEach((a, k) => ai[a] = k);
    incs.forEach((i, k) => ii[i] = k);
    for (const r of rows) {
      const a = ai[D.dims.age[r[ci.ai]]], i = ii[D.dims.income[r[ci.ii]]];
      if (a === undefined || i === undefined) continue;
      if (!OFFERS[r[ci.oi]].is_informational) grid[a][i].promo += r[ci.n];
      if (r[ci.c]) grid[a][i].completed += r[ci.n];
    }
    const values = grid.map(row => row.map(c => (c.promo >= 50 ? c.completed / c.promo : null)));
    const ct = custTotals();

    return `
      <div class="grid g2">
        <div class="panel">
          <h3>Redemption rate by age and income</h3>
          <p class="sub">Cells with fewer than 50 promotional offers are left blank</p>
          ${heatmap(ages, incs, values)}
        </div>
        <div class="panel">
          <h3>By income band</h3>
          <p class="sub">Redemption rises almost monotonically with income</p>
          ${barTable(segBreak('income', D.dims.income, 'ii'), ['Income', 'Sent', 'View rate', 'Redemption'])}
        </div>
      </div>
      <div class="grid g3">
        <div class="panel">
          <h3>By tenure</h3>
          <p class="sub">Time since joining</p>
          ${barTable(segBreak('tenure', D.dims.tenure, 'ti'), ['Tenure', 'Sent', 'View', 'Redemption'])}
        </div>
        <div class="panel">
          <h3>By age group</h3>
          <p class="sub">Response rises with age</p>
          ${barTable(segBreak('age', D.dims.age, 'ai'), ['Age', 'Sent', 'View', 'Redemption'])}
        </div>
        <div class="panel">
          <h3>By gender</h3>
          <p class="sub">Self-reported</p>
          ${barTable(segBreak('gender', D.dims.gender, 'gi'), ['Gender', 'Sent', 'View', 'Redemption'])}
        </div>
      </div>
      <div class="grid g2">
        <div class="panel">
          <h3>Engagement segments</h3>
          <p class="sub">${fmt(ct.customers)} customers in the current selection</p>
          ${barTable(
            Object.entries(ct.bySeg).sort((a, b) => b[1].spend - a[1].spend).map(([k, v]) => ({
              label: k, bar: v.spend,
              cells: [fmt(v.customers), money(v.spend), v.customers ? money2(v.spend / v.customers) : '—', pct(safeDiv(v.spend, ct.spend))]
            })),
            ['Segment', 'Customers', 'Spend', 'Per customer', 'Share'])}
        </div>
        <div class="callout">
          <h3>Why "Unknown" is filtered out by default</h3>
          <p>2,175 customers have no age, gender or income recorded — the same rows in all three columns.
          They redeem at roughly 14% against 54% overall, but that reflects dormant accounts rather than any
          demographic group. Turn off <b>Complete profiles only</b> in the filter rail to see them, and read
          the charts knowing the Unknown bucket is a data artefact, not a segment.</p>
        </div>
      </div>`;
  }

  function pagePerformance() {
    const rows = offerRows();
    const oidx = activeOfferIdx();
    const acc = {};
    for (const r of rows) {
      const o = r[ci.oi];
      acc[o] = acc[o] || { sent: 0, viewed: 0, completed: 0, unviewed: 0, htc: 0 };
      acc[o].sent += r[ci.n];
      if (r[ci.v]) acc[o].viewed += r[ci.n];
      if (r[ci.c]) { acc[o].completed += r[ci.n]; acc[o].htc += r[ci.htc]; }
      acc[o].unviewed += r[ci.uc];
    }
    const promo = OFFERS.filter(o => oidx.has(o.oi) && !o.is_informational && acc[o.oi]);
    const info = OFFERS.filter(o => oidx.has(o.oi) && o.is_informational && acc[o.oi]);

    const perfRows = promo.map(o => {
      const a = acc[o.oi];
      return { o, a, rate: safeDiv(a.completed, a.sent) };
    }).sort((x, y) => y.rate - x.rate);

    const byChannel = {};
    ALL_CHANNELS.forEach(c => byChannel[c] = { sent: 0, viewed: 0, completed: 0 });
    for (const r of rows) {
      const o = OFFERS[r[ci.oi]];
      if (o.is_informational) continue;
      o.channels.forEach(c => {
        byChannel[c].sent += r[ci.n];
        if (r[ci.v]) byChannel[c].viewed += r[ci.n];
        if (r[ci.c]) byChannel[c].completed += r[ci.n];
      });
    }

    const byCombo = {};
    for (const r of rows) {
      const o = OFFERS[r[ci.oi]];
      if (o.is_informational) continue;
      const k = o.channels_text;
      byCombo[k] = byCombo[k] || { sent: 0, viewed: 0, completed: 0 };
      byCombo[k].sent += r[ci.n];
      if (r[ci.v]) byCombo[k].viewed += r[ci.n];
      if (r[ci.c]) byCombo[k].completed += r[ci.n];
    }

    if (!perfRows.length) return '<p class="empty">No promotional offers in this selection.</p>';

    return `
      <div class="grid g2">
        <div class="panel">
          <h3>Redemption rate by offer</h3>
          <p class="sub">Promotional offers, best first</p>
          ${hBar(perfRows.map(p => ({
            label: p.o.offer_label, value: p.rate, display: pct(p.rate),
            flag: p.rate < 0.45
          })), { labelW: 175, max: Math.max(...perfRows.map(p => p.rate)), alt: 'Redemption by offer' })}
          <p class="note">The best offer is also the cheapest: <b>$2 on a $10 spend</b> outperforms the
          $10 BOGO by a wide margin. Customers respond to the threshold, not the reward size.</p>
        </div>
        <div class="panel">
          <h3>Difficulty against redemption</h3>
          <p class="sub">Bubble size = offers sent · colour = type</p>
          ${scatter(perfRows.map(p => ({
            x: p.o.difficulty, y: p.rate, r: p.a.sent,
            color: p.o.offer_type === 'bogo' ? PAL.flag : PAL.accent,
            title: `${p.o.offer_label}: ${pct(p.rate)} on ${fmt(p.a.sent)} sent`
          })), { xlabel: 'Spend threshold required ($)', alt: 'Difficulty vs redemption' })}
          <div class="legend">
            <span><i class="swatch" style="background:var(--accent)"></i>Discount</span>
            <span><i class="swatch" style="background:var(--flag)"></i>BOGO</span>
          </div>
        </div>
      </div>
      <div class="panel">
        <h3>Offer detail</h3>
        <p class="sub">Every promotional offer in the current selection</p>
        <table>
          <thead><tr>
            <th>Offer</th><th>Channels</th><th class="n">Sent</th><th class="n">View rate</th>
            <th class="n">Redemption</th><th class="n">Unviewed</th><th class="n">Avg hrs to complete</th><th class="n">Reward cost</th>
          </tr></thead>
          <tbody>
          ${perfRows.map(p => `<tr>
            <td>${esc(p.o.offer_label)}</td>
            <td style="color:var(--ink-soft)">${esc(p.o.channels_text)}</td>
            <td class="n">${fmt(p.a.sent)}</td>
            <td class="n">${pct(safeDiv(p.a.viewed, p.a.sent))}</td>
            <td class="n"><b>${pct(p.rate)}</b></td>
            <td class="n">${fmt(p.a.unviewed)}</td>
            <td class="n">${p.a.completed ? (p.a.htc / p.a.completed).toFixed(1) : '—'}</td>
            <td class="n">${money(p.a.completed * p.o.reward)}</td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <div class="grid g2">
        <div class="panel">
          <h3>Channel reach</h3>
          <p class="sub">Each offer counts once per channel it uses, so these overlap</p>
          ${barTable(ALL_CHANNELS.filter(c => byChannel[c].sent).map(c => ({
            label: c, bar: safeDiv(byChannel[c].viewed, byChannel[c].sent),
            cells: [fmt(byChannel[c].sent), pct(safeDiv(byChannel[c].viewed, byChannel[c].sent)), pct(safeDiv(byChannel[c].completed, byChannel[c].sent))]
          })), ['Channel', 'Deliveries', 'View rate', 'Redemption'])}
          <p class="note">Social appears in every high-view combination. Treat the view-rate gap as solid and
          the redemption gap as suggestive — channel choice is confounded with offer design.</p>
        </div>
        <div class="panel">
          <h3>Channel combinations</h3>
          <p class="sub">The non-overlapping read</p>
          ${barTable(Object.entries(byCombo).sort((a, b) => safeDiv(b[1].viewed, b[1].sent) - safeDiv(a[1].viewed, a[1].sent)).map(([k, v]) => ({
            label: k, bar: safeDiv(v.viewed, v.sent),
            cells: [fmt(v.sent), pct(safeDiv(v.viewed, v.sent)), pct(safeDiv(v.completed, v.sent))]
          })), ['Channels', 'Deliveries', 'View rate', 'Redemption'])}
        </div>
      </div>
      ${info.length ? `<div class="panel">
        <h3>Informational offers</h3>
        <p class="sub">No threshold, no reward — measured on views alone</p>
        ${barTable(info.map(o => ({
          label: o.offer_label, bar: safeDiv(acc[o.oi].viewed, acc[o.oi].sent),
          cells: [fmt(acc[o.oi].sent), pct(safeDiv(acc[o.oi].viewed, acc[o.oi].sent))]
        })), ['Offer', 'Sent', 'View rate'])}
      </div>` : ''}`;
  }

  function pageSpend() {
    const txs = txnRows();
    const ctx = [{ n: 0, amt: 0 }, { n: 0, amt: 0 }, { n: 0, amt: 0 }];
    const dayIn = new Map(), dayOut = new Map();
    for (const r of txs) {
      const c = r[ti.ctx];
      ctx[c].n += r[ti.n]; ctx[c].amt += r[ti.amt];
      const m = c === 2 ? dayIn : dayOut, d = r[ti.day];
      const cur = m.get(d) || { n: 0, amt: 0 };
      cur.n += r[ti.n]; cur.amt += r[ti.amt];
      m.set(d, cur);
    }
    const toSeries = m => [...m.keys()].sort((a, b) => a - b)
      .map(d => ({ x: d, y: safeDiv(m.get(d).amt, m.get(d).n) }));

    const ba = [{ n: 0, amt: 0 }, { n: 0, amt: 0 }];
    for (const r of D.ba) {
      if (!dimOk(r, bi)) continue;
      ba[r[bi.after]].n += r[bi.n];
      ba[r[bi.after]].amt += r[bi.amt];
    }

    const comp = [{ n: 0, spend: 0, txns: 0 }, { n: 0, spend: 0, txns: 0 }];
    for (const r of D.comp) {
      if (!dimOk(r, pi)) continue;
      const k = r[pi.isc];
      comp[k].n += r[pi.n]; comp[k].spend += r[pi.spend]; comp[k].txns += r[pi.txns];
    }

    const avgIn = safeDiv(ctx[2].amt, ctx[2].n);
    const avgOut = safeDiv(ctx[0].amt, ctx[0].n);

    return `
      <div class="kpis">
        ${kpi(money(ctx[0].amt + ctx[1].amt + ctx[2].amt), 'Total spend in selection')}
        ${kpi(money2(avgIn), 'Avg transaction, inside a viewed offer window')}
        ${kpi(money2(avgOut), 'Avg transaction, outside any offer window')}
        ${kpi(ba[0].n ? money2(ba[0].amt / ba[0].n) : '—', 'Avg transaction before first completion')}
        ${kpi(ba[1].n ? money2(ba[1].amt / ba[1].n) : '—', 'Avg transaction after first completion')}
      </div>
      <div class="grid g2">
        <div class="panel">
          <h3>Average transaction across the window</h3>
          <p class="sub">Inside a viewed offer window against everything else</p>
          ${multiLine([
            { points: toSeries(dayIn), color: 'var(--accent)' },
            { points: toSeries(dayOut), color: 'var(--flag)', dash: '4 3' }
          ], { money: true, alt: 'Average transaction by day' })}
          <div class="legend">
            <span><i class="swatch" style="background:var(--accent)"></i>Inside a viewed offer window</span>
            <span><i class="swatch" style="background:var(--flag)"></i>Outside / unviewed</span>
          </div>
        </div>
        <div class="panel">
          <h3>Spend by offer context</h3>
          <p class="sub">Average basket size, by whether an offer was open</p>
          ${barTable([
            { label: 'Inside a viewed window', bar: safeDiv(ctx[2].amt, ctx[2].n), cells: [fmt(ctx[2].n), money(ctx[2].amt), money2(safeDiv(ctx[2].amt, ctx[2].n))] },
            { label: 'Inside an unviewed window', bar: safeDiv(ctx[1].amt, ctx[1].n), cells: [fmt(ctx[1].n), money(ctx[1].amt), money2(safeDiv(ctx[1].amt, ctx[1].n))] },
            { label: 'Outside any window', bar: safeDiv(ctx[0].amt, ctx[0].n), cells: [fmt(ctx[0].n), money(ctx[0].amt), money2(safeDiv(ctx[0].amt, ctx[0].n))] }
          ], ['Context', 'Transactions', 'Spend', 'Avg'])}
          <p class="note">Barely a difference: <b>${money2(avgIn)}</b> inside a viewed window against
          <b>${money2(avgOut)}</b> outside one. Having an offer open does not move basket size — the
          difference in this programme is between customers, not between windows.</p>
        </div>
      </div>
      <div class="grid g2">
        <div class="panel">
          <h3>Completers against non-completers</h3>
          <p class="sub">Lifetime behaviour over the window</p>
          ${barTable([
            { label: 'Completed ≥1 offer', bar: comp[1].n ? comp[1].spend / comp[1].n : 0,
              cells: [fmt(comp[1].n), comp[1].n ? money2(comp[1].spend / comp[1].n) : '—', comp[1].txns ? money2(comp[1].spend / comp[1].txns) : '—', comp[1].n ? (comp[1].txns / comp[1].n).toFixed(1) : '—'] },
            { label: 'Never completed', bar: comp[0].n ? comp[0].spend / comp[0].n : 0,
              cells: [fmt(comp[0].n), comp[0].n ? money2(comp[0].spend / comp[0].n) : '—', comp[0].txns ? money2(comp[0].spend / comp[0].txns) : '—', comp[0].n ? (comp[0].txns / comp[0].n).toFixed(1) : '—'] }
          ], ['Group', 'Customers', 'Spend per customer', 'Avg transaction', 'Transactions'])}
        </div>
        <div class="callout">
          <h3>Read the before/after gap carefully</h3>
          <p>Average transaction is ${ba[0].n ? money2(ba[0].amt / ba[0].n) : '—'} before a customer's first
          completion and ${ba[1].n ? money2(ba[1].amt / ba[1].n) : '—'} after. The same customers sit on both
          sides, so it controls for who they are — but first completions cluster early in the window, so
          "after" covers more of the natural spend ramp. Directional evidence, not a causal estimate.
          No holdout group exists in this data, so no uplift claim can be defended.</p>
        </div>
      </div>`;
  }

  /* ---------- filter rail ---------- */
  function chipGroup(title, key, values) {
    return `<div class="fgroup"><h3>${esc(title)}</h3><div class="chips">` +
      values.map(v => `<button class="chip" type="button" data-key="${key}" data-val="${esc(v)}"
        aria-pressed="${state[key].has(v)}">${esc(v)}</button>`).join('') +
      '</div></div>';
  }

  function renderRail() {
    document.getElementById('filters').innerHTML =
      chipGroup('Offer type', 'offerType', OFFER_TYPES) +
      chipGroup('Channel', 'channel', ALL_CHANNELS) +
      chipGroup('Age group', 'age', D.dims.age.filter(a => a !== 'Unknown')) +
      chipGroup('Income band', 'income', D.dims.income.filter(i => i !== 'Unknown')) +
      chipGroup('Gender', 'gender', D.dims.gender) +
      chipGroup('Tenure', 'tenure', D.dims.tenure) +
      `<div class="fgroup"><label class="switch">
         <input type="checkbox" id="pcToggle" ${state.completeOnly ? 'checked' : ''}>
         <span>Complete profiles only</span></label></div>`;

    document.getElementById('railNote').innerHTML = state.completeOnly
      ? '2,175 customers with no age, gender or income are hidden. They redeem far below average because they are dormant, not because of any demographic trait.'
      : 'Incomplete profiles are included. The "Unknown" rows are a data artefact, not a customer segment — do not read them as a finding.';
  }

  function renderScope() {
    const bits = [];
    const names = { offerType: 'offer type', channel: 'channel', age: 'age', income: 'income', gender: 'gender', tenure: 'tenure' };
    Object.keys(names).forEach(k => {
      if (state[k].size) bits.push(`<b>${esc([...state[k]].join(', '))}</b>`);
    });
    const t = totals(offerRows());
    const base = `Showing <b>${fmt(t.sent)}</b> offer deliveries to <b>${fmt(custTotals().customers)}</b> customers`;
    document.getElementById('scope').innerHTML = base +
      (bits.length ? ' · filtered to ' + bits.join(' · ') : ' · no filters applied') +
      (state.completeOnly ? ' · complete profiles only' : ' · including incomplete profiles');
  }

  function renderTabs() {
    document.getElementById('tabs').innerHTML = PAGES.map(p =>
      `<button type="button" data-page="${p.id}" aria-current="${state.page === p.id}">${esc(p.name)}</button>`
    ).join('');
  }

  function render() {
    renderTabs();
    renderScope();
    const page = PAGES.find(p => p.id === state.page);
    document.getElementById('page').innerHTML = page.render();
  }

  /* ---------- events ---------- */
  document.getElementById('tabs').addEventListener('click', e => {
    const b = e.target.closest('button[data-page]');
    if (!b) return;
    state.page = b.dataset.page;
    render();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  document.getElementById('filters').addEventListener('click', e => {
    const b = e.target.closest('.chip');
    if (!b) return;
    const set = state[b.dataset.key];
    if (set.has(b.dataset.val)) set.delete(b.dataset.val); else set.add(b.dataset.val);
    b.setAttribute('aria-pressed', set.has(b.dataset.val));
    render();
  });

  document.getElementById('filters').addEventListener('change', e => {
    if (e.target.id !== 'pcToggle') return;
    state.completeOnly = e.target.checked;
    renderRail();
    render();
  });

  document.getElementById('resetBtn').addEventListener('click', () => {
    ['offerType', 'channel', 'age', 'income', 'gender', 'tenure'].forEach(k => state[k].clear());
    state.completeOnly = true;
    renderRail();
    render();
  });

  document.getElementById('themeToggle').addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('rn-theme', next); } catch (err) { /* private mode */ }
  });

  try {
    const saved = localStorage.getItem('rn-theme');
    if (saved) document.documentElement.setAttribute('data-theme', saved);
  } catch (err) { /* private mode */ }

  renderRail();
  render();
})();
