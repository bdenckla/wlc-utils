// Client-side filtering for the combined Goerwitz report (goerwitz.html).
//
// Each verse is a <section class="goerwitz-verse"> tagged with data-kind
// ("ob"/"tm") and data-msp ("y"/"n"). Two groups of checkboxes (.gf-kind and
// .gf-msp) show/hide verses along those two dimensions, and .gf-count reports
// how many are currently visible.
(function () {
  "use strict";

  function checkedValues(selector) {
    var values = new Set();
    document.querySelectorAll(selector).forEach(function (input) {
      if (input.checked) {
        values.add(input.value);
      }
    });
    return values;
  }

  function applyFilters() {
    var kinds = checkedValues("input.gf-kind");
    var msps = checkedValues("input.gf-msp");
    var verses = document.querySelectorAll("section.goerwitz-verse");
    var shown = 0;

    verses.forEach(function (verse) {
      var visible =
        kinds.has(verse.dataset.kind) && msps.has(verse.dataset.msp);
      verse.style.display = visible ? "" : "none";
      if (visible) {
        shown += 1;
      }
    });

    var countEl = document.querySelector(".gf-count");
    if (countEl) {
      countEl.textContent =
        "Showing " + shown + " of " + verses.length + " verses";
    }
  }

  function init() {
    var inputs = document.querySelectorAll("input.gf-kind, input.gf-msp");
    inputs.forEach(function (input) {
      input.addEventListener("change", applyFilters);
    });
    applyFilters();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
