// Client-side filtering for the Goerwitz oddball report (goerwitz.html).
//
// Each verse is a <section class="goerwitz-verse"> tagged with data-category
// ("msp" = missing sof pasuq, "msl" = missing silluq, "zwhim" = zarqa whim,
// "other"). A group of
// checkboxes (.gf-category) shows/hides verses by category, and .gf-count
// reports how many are currently visible.
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
    var categories = checkedValues("input.gf-category");
    var verses = document.querySelectorAll("section.goerwitz-verse");
    var shown = 0;

    verses.forEach(function (verse) {
      var visible = categories.has(verse.dataset.category);
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
    var inputs = document.querySelectorAll("input.gf-category");
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
