// Client-side filtering for the Goerwitz oddball report (goerwitz.html).
//
// Each verse is a <section class="goerwitz-verse"> tagged with data-category
// ("msp" = missing sof pasuq, "msl" = missing silluq, "zwhim" = zarqa whim,
// "other") plus two boolean flags, data-uchange and data-wnote ("1"/"0"), for
// whether the verse has a UXLC change and a WLC bracket-note.
//
// The category checkboxes (.gf-category) select which categories show. Two
// tri-state radio groups (.gf-uchange, .gf-wnote) further constrain the list,
// ANDed with the category: each is "yes" (has), "no" (doesn't have), or "any"
// (don't care). .gf-count reports how many verses are currently visible.
//
// Each tri-state option's "(N)" count is recomputed live (faceted): it counts
// the verses that pass every OTHER filter, so the number reflects how many
// would show if that option were chosen. A facet's own selection never affects
// its own counts. The spans the Python writes are the no-JS fallback.
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

  function radioValue(name) {
    var checked = document.querySelector(
      'input[name="' + name + '"]:checked'
    );
    return checked ? checked.value : "any";
  }

  // want: "yes" | "no" | "any"; flag: the verse's "1"/"0" data attribute.
  function flagMatches(want, flag) {
    if (want === "yes") {
      return flag === "1";
    }
    if (want === "no") {
      return flag === "0";
    }
    return true;
  }

  function setCount(className, value) {
    var el = document.querySelector("." + className);
    if (el) {
      el.textContent = String(value);
    }
  }

  // Recompute one tri-state group's counts over the verses passing `others`
  // (every filter except this group), then write them into its count spans.
  function updateFacetCounts(group, verses, others) {
    var has = 0;
    var no = 0;
    verses.forEach(function (verse) {
      if (!others(verse)) {
        return;
      }
      if (verse.dataset[group.dataKey] === "1") {
        has += 1;
      } else {
        no += 1;
      }
    });
    setCount(group.name + "-has-count", has);
    setCount(group.name + "-no-count", no);
  }

  function applyFilters() {
    var categories = checkedValues("input.gf-category");
    var wantUchange = radioValue("gf-uchange");
    var wantWnote = radioValue("gf-wnote");
    var verses = document.querySelectorAll("section.goerwitz-verse");

    function passesCategory(verse) {
      return categories.has(verse.dataset.category);
    }
    function passesUchange(verse) {
      return flagMatches(wantUchange, verse.dataset.uchange);
    }
    function passesWnote(verse) {
      return flagMatches(wantWnote, verse.dataset.wnote);
    }

    var shown = 0;
    verses.forEach(function (verse) {
      var visible =
        passesCategory(verse) && passesUchange(verse) && passesWnote(verse);
      verse.style.display = visible ? "" : "none";
      if (visible) {
        shown += 1;
      }
    });

    // Faceted: each group's counts honor the category and the OTHER group.
    updateFacetCounts(
      { name: "gf-uchange", dataKey: "uchange" },
      verses,
      function (verse) {
        return passesCategory(verse) && passesWnote(verse);
      }
    );
    updateFacetCounts(
      { name: "gf-wnote", dataKey: "wnote" },
      verses,
      function (verse) {
        return passesCategory(verse) && passesUchange(verse);
      }
    );

    var countEl = document.querySelector(".gf-count");
    if (countEl) {
      countEl.textContent =
        "Showing " + shown + " of " + verses.length + " verses";
    }
  }

  function init() {
    var inputs = document.querySelectorAll(
      "input.gf-category, input.gf-uchange, input.gf-wnote"
    );
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
