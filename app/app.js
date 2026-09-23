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

  function renderStats() {
    var stats = DATA.stats || {};
    var cards = [
      ["scanned", "Articles scanned"],
      ["in_scope", "Matched sector + stage"],
      ["needs_review", "Needs review (ambiguous stage)"],
      ["new_today", "New today (not seen before)"],
      ["excluded_sector", "Excluded, wrong sector"],
      ["excluded_stage", "Excluded, wrong stage"],
      ["excluded_debt_or_ma", "Excluded, debt or M&A"],
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
    var meta = DATA.meta || {};
    var rows = (DATA.gaps || []).map(function (g) {
      return '<div class="gap-row"><span class="name">' + escapeHtml(g.name) +
        '</span> <span class="tag status-' + slug(g.status) + '">' + escapeHtml(g.status) +
        "</span><div>" + escapeHtml(g.why) + "</div></div>";
    });
    var liveSources = (meta.sources || []).join(", ");
    if (liveSources) {
      rows.unshift(
        '<div class="gap-row"><span class="name">RSS feeds</span> ' +
        '<span class="tag">live, fetched ' + escapeHtml(meta.run_date || "") + "</span><div>" +
        escapeHtml(liveSources) + "</div></div>"
      );
    }
    if (meta.fetch_errors && meta.fetch_errors.length) {
      rows.push(
        '<div class="gap-row"><span class="name">Fetch errors this run</span>' +
        "<div>" + meta.fetch_errors.map(function (e) { return escapeHtml(e.source); }).join(", ") + "</div></div>"
      );
    }
    document.getElementById("gaps").innerHTML = rows.join("") || '<div class="empty-state">No source info recorded.</div>';
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
    var sourceNames = {};
    (DATA.deals || []).forEach(function (d) {
      (d.sectors || []).forEach(function (s) { sectors[s] = true; });
      if (d.source) sourceNames[d.source] = true;
    });
    var sel = document.getElementById("sectorFilter");
    Object.keys(sectors).sort().forEach(function (s) {
      var opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      sel.appendChild(opt);
    });
    sel.addEventListener("change", renderDeals);

    var srcSel = document.getElementById("sourceFilter");
    Object.keys(sourceNames).sort().forEach(function (s) {
      var opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      srcSel.appendChild(opt);
    });
    srcSel.addEventListener("change", renderDeals);
  }

  function dealCardHtml(deal) {
    var decision = decisions[deal.id];
    var cls = decision === "like" ? "liked" : decision === "dislike" ? "disliked" : "";
    var sectorTags = (deal.sectors || []).map(function (s) {
      return '<span class="tag">' + escapeHtml(s) + "</span>";
    }).join("");
    return (
      '<div class="deal-card ' + cls + '" data-id="' + escapeHtml(deal.id) + '">' +
      '<span class="source-tag">' + escapeHtml(deal.source || "unknown source") + "</span>" +
      '<div class="title"><a href="' + escapeHtml(deal.link) + '" target="_blank" rel="noopener">' +
      escapeHtml(deal.title) + "</a></div>" +
      '<div class="deal-meta">' +
      (deal.amount_usd_approx ? "~$" + deal.amount_usd_approx + "M &middot; " : "amount unknown &middot; ") +
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

  function renderList(containerId, decisionValue, emptyText) {
    var filter = document.getElementById("sectorFilter").value;
    var sourceFilter = document.getElementById("sourceFilter").value;
    var deals = (DATA.deals || []).filter(function (d) {
      var matchesDecision = decisionValue ? d.decision === decisionValue
        : d.decision !== "needs_review";
      var matchesSector = !filter || (d.sectors || []).indexOf(filter) !== -1;
      var matchesSource = !sourceFilter || d.source === sourceFilter;
      return matchesDecision && matchesSector && matchesSource;
    });
    // Biggest known round first, so a large deal never gets buried by
    // arriving late in feed order; unknown amounts sort last, not as 0.
    deals.sort(function (a, b) {
      var av = a.amount_usd_approx, bv = b.amount_usd_approx;
      if (av == null && bv == null) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;
      return bv - av;
    });
    var container = document.getElementById(containerId);
    if (!deals.length) {
      container.innerHTML = '<div class="empty-state">' + emptyText + "</div>";
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

  function renderDeals() {
    renderList("dealList", "in_scope", "No new in-scope deals in this run.");
    renderList("reviewList", "needs_review", "Nothing ambiguous this run.");
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

  renderStats();
  renderGaps();
  populateSectorFilter();
  renderDeals();
})();
