(function () {
  "use strict";

  var DATA = window.EURO_SOURCING_DATA || { meta: {}, stats: {}, gaps: [], deals: [] };
  var STORAGE_KEY = "euro_sourcing_decisions";

  function loadDecisions() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function saveDecisions(decisions) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(decisions));
    } catch (e) {
      // localStorage unavailable (e.g. file:// in some browsers); decisions
      // just won't persist across reloads. Not fatal.
    }
  }

  var decisions = loadDecisions();

  function renderBanner() {
    var meta = DATA.meta || {};
    var sources = (meta.sources || []).join(", ");
    var el = document.getElementById("banner");
    var errNote = "";
    if (meta.fetch_errors && meta.fetch_errors.length) {
      errNote = " " + meta.fetch_errors.length + " source(s) failed to fetch this run: " +
        meta.fetch_errors.map(function (e) { return e.source; }).join(", ") + ".";
    }
    el.innerHTML = "<b>Real data.</b> Fetched live from " + (sources || "no sources") +
      " on " + (meta.run_date || "unknown date") + "." + errNote +
      " Pitchbook, Crunchbase and LinkedIn are not connected, see the gaps panel below.";
  }

  function renderStats() {
    var stats = DATA.stats || {};
    var cards = [
      ["scanned", "Articles scanned"],
      ["in_scope", "Matched sector + stage"],
      ["new_today", "New today (not seen before)"],
      ["excluded_sector", "Excluded, wrong sector"],
      ["excluded_stage", "Excluded, wrong stage"],
    ];
    var html = cards.map(function (c) {
      var n = stats[c[0]];
      return '<div class="stat-card"><div class="n">' + (n === undefined ? "?" : n) +
        '</div><div class="label">' + c[1] + "</div></div>";
    }).join("");
    document.getElementById("stats").innerHTML = html;
  }

  function slug(s) {
    return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-");
  }

  function renderGaps() {
    var html = (DATA.gaps || []).map(function (g) {
      return '<div class="gap-row"><span class="name">' + escapeHtml(g.name) +
        '</span> <span class="tag status-' + slug(g.status) + '">' + escapeHtml(g.status) +
        "</span><div>" + escapeHtml(g.why) + "</div></div>";
    }).join("");
    document.getElementById("gaps").innerHTML = html || '<div class="empty-state">No known gaps recorded.</div>';
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function populateSectorFilter() {
    var sectors = {};
    (DATA.deals || []).forEach(function (d) {
      (d.sectors || []).forEach(function (s) { sectors[s] = true; });
    });
    var sel = document.getElementById("sectorFilter");
    Object.keys(sectors).sort().forEach(function (s) {
      var opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      sel.appendChild(opt);
    });
    sel.addEventListener("change", renderDeals);
  }

  function dealCardHtml(deal) {
    var decision = decisions[deal.id];
    var cls = decision === "like" ? "liked" : decision === "dislike" ? "disliked" : "";
    var sectorTags = (deal.sectors || []).map(function (s) {
      return '<span class="tag">' + escapeHtml(s) + "</span>";
    }).join("");
    return (
      '<div class="deal-card ' + cls + '" data-id="' + escapeHtml(deal.id) + '">' +
      '<div class="title"><a href="' + escapeHtml(deal.link) + '" target="_blank" rel="noopener">' +
      escapeHtml(deal.title) + "</a></div>" +
      '<div class="deal-meta">' + escapeHtml(deal.source) + " &middot; " +
      escapeHtml(deal.published || "date unknown") + " &middot; " +
      escapeHtml(deal.country) + " &middot; stage: " + escapeHtml(deal.stage) + "</div>" +
      '<div class="deal-snippet">' + escapeHtml(deal.summary) + "</div>" +
      "<div>" + sectorTags + "</div>" +
      '<div class="deal-actions" style="margin-top:8px">' +
      '<button class="like' + (decision === "like" ? " active" : "") + '" data-action="like">Like</button>' +
      '<button class="dislike' + (decision === "dislike" ? " active" : "") + '" data-action="dislike">Dislike</button>' +
      "</div></div>"
    );
  }

  function renderDeals() {
    var filter = document.getElementById("sectorFilter").value;
    var deals = (DATA.deals || []).filter(function (d) {
      return !filter || (d.sectors || []).indexOf(filter) !== -1;
    });
    var container = document.getElementById("dealList");
    if (!deals.length) {
      container.innerHTML = '<div class="empty-state">No new in-scope deals in this run.</div>';
      return;
    }
    container.innerHTML = deals.map(dealCardHtml).join("");
    container.querySelectorAll(".deal-actions button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var card = btn.closest(".deal-card");
        var id = card.getAttribute("data-id");
        var action = btn.getAttribute("data-action");
        decisions[id] = decisions[id] === action ? undefined : action;
        if (decisions[id] === undefined) delete decisions[id];
        saveDecisions(decisions);
        renderDeals();
      });
    });
  }

  function exportApproved() {
    var liked = (DATA.deals || []).filter(function (d) { return decisions[d.id] === "like"; });
    var blob = new Blob([JSON.stringify(liked, null, 2)], { type: "application/json" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "euro-sourcing-approved-" + (DATA.meta.run_date || "export") + ".json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  document.getElementById("exportApproved").addEventListener("click", exportApproved);
  document.getElementById("resetDecisions").addEventListener("click", function () {
    decisions = {};
    saveDecisions(decisions);
    renderDeals();
  });

  renderBanner();
  renderStats();
  renderGaps();
  populateSectorFilter();
  renderDeals();
})();
