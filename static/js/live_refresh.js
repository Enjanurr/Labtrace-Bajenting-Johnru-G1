document.addEventListener("DOMContentLoaded", function () {
  var $root = $("#central-dashboard");
  if (!$root.length) { return; }

  var url = $root.data("live-url");
  var interval = parseInt($root.data("interval"), 10) || 15000;
  var inflight = false;

  function td(text, cls) {
    return $("<td>").addClass("px-4 py-2 " + (cls || ""))
      .text(text === null || text === undefined ? "" : text);
  }

  function fill($body, rows, cols, emptyText, build) {
    $body.empty();
    if (!rows || !rows.length) {
      $body.append($("<tr>").append(
        $("<td>").attr("colspan", cols)
          .addClass("px-4 py-6 text-center text-slate-400").text(emptyText)));
      return;
    }
    $.each(rows, function (_, row) { $body.append(build(row)); });
  }

  function setText(id, value) {
    $("#" + id).text(value === null || value === undefined ? "—" : value);
  }

  function fmtMinutes(m) {
    if (m === null || m === undefined) { return "—"; }
    var h = Math.floor(m / 60), mm = m % 60;
    return h ? h + "h " + mm + "m" : mm + "m";
  }

  function countRow(label, count) {
    return $("<tr>").append(td(label)).append(td(count, "text-right font-semibold"));
  }

  function render(d) {
    var eq = d.equipment;
    setText("total-inside", d.total_inside);
    setText("labs-in-use", d.occupancy.length);
    setText("items-borrowed", eq.active_loans);
    setText("unresolved-count", d.unresolved);
    setText("incident-reported", d.incidents.reported);
    setText("incident-investigation", d.incidents.investigation);
    setText("stat-total-assets", eq.total_assets);
    setText("stat-borrowed-today", eq.borrowed_today);
    setText("stat-returned-today", eq.returned_today);
    $("#stat-avg-loan").text(fmtMinutes(eq.avg_loan_minutes));

    fill($("#occupancy-body"), d.occupancy, 2, "Nobody is checked in.",
      function (r) { return countRow(r.lab, r.count); });
    fill($("#asset-body"), eq.assets, 2, "No assets registered.",
      function (r) { return countRow(r.label, r.count); });
    fill($("#cond-loan-body"), eq.on_loan_condition, 2, "Nothing on loan.",
      function (r) { return countRow(r.label, r.count); });
    fill($("#cond-return-body"), eq.returned_condition, 2, "No recent returns.",
      function (r) { return countRow(r.label, r.count); });
    fill($("#top-assets-body"), eq.top_assets, 2, "No borrowing yet.",
      function (r) { return countRow(r.name, r.count); });
    fill($("#visits-body"), d.visits, 4, "No active visits.", function (r) {
      return $("<tr>").append(td(r.user)).append(td(r.lab)).append(td(r.purpose))
        .append(td(r.since_display, "text-slate-500"));
    });
    fill($("#borrowers-body"), d.borrowers, 4, "Nothing is currently borrowed.", function (r) {
      return $("<tr>").append(td(r.asset, "font-medium")).append(td(r.borrower))
        .append(td(r.lab)).append(td(r.since_display, "text-slate-500"));
    });
  }

  function setStatus(ok) {
    $("#live-status")
      .text(ok ? "Live" : "Connection lost, retrying…")
      .toggleClass("text-green-600", ok)
      .toggleClass("text-red-600", !ok);
  }

  function refresh() {
    if (inflight || document.hidden) { return; }
    inflight = true;
    $.ajax({ url: url, dataType: "json", cache: false })
      .done(function (d) {
        render(d);
        $("#last-updated").text(new Date().toLocaleTimeString());
        setStatus(true);
      })
      .fail(function () { setStatus(false); })
      .always(function () { inflight = false; });
  }

  setInterval(refresh, interval);
  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) { refresh(); }
  });
});     