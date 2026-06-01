(function(global) {
  "use strict";

  /**
   * Binds Bootstrap Tab behaviour to every element matching `selector`.
   * Prevents the default anchor navigation so only the tab switch fires.
   *
   * @param {string} selector - CSS selector that targets one or more tab trigger elements.
   */
  function initBootstrapTab(selector) {
    var tabs = [].slice.call(document.querySelectorAll(selector));
    tabs.forEach(function(triggerEl) {
      var tabTrigger = new bootstrap.Tab(triggerEl);
      triggerEl.addEventListener("click", function(event) {
        event.preventDefault();
        tabTrigger.show();
      });
    });
  }

  /**
   * Initialises Bootstrap Tooltips for every element that carries the
   * `data-bs-toggle="tooltip"` attribute.  The tooltip is anchored to
   * `<body>` so it is never clipped by overflow-hidden parents.
   */
  function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
      var _ = new bootstrap.Tooltip(tooltipTriggerEl, { container: "body" });
    });
  }

  /**
   * Initialises Bootstrap Popovers for every element that carries the
   * `data-bs-toggle="popover"` attribute.  HTML content is sanitised
   * with DOMPurify when it is available.
   */
  function initPopovers() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.forEach(function(popoverTriggerEl) {
      var _ = new bootstrap.Popover(popoverTriggerEl, {
        sanitizeFn: function(content) {
          if (global.DOMPurify && typeof global.DOMPurify.sanitize === "function") {
            return global.DOMPurify.sanitize(content);
          }
          return content;
        },
        container: "body",
      });
    });
  }

  /**
   * Listens for Bootstrap `shown.bs.tab` events and forces DataTables to
   * recalculate column widths after a hidden tab becomes visible.
   * This fixes misaligned column headers that can occur when a DataTable
   * is rendered inside a tab that was not visible on initial paint.
   * Requires jQuery and DataTables to be loaded.
   */
  function initTabDataTableResize() {
    if (!global.$ || !$.fn || !$.fn.dataTable) {
      return;
    }
    $('a[data-bs-toggle="tab"]')
      .off("shown.bs.tab.scoutTables")
      .on("shown.bs.tab.scoutTables", function() {
        $($.fn.dataTable.tables(true)).DataTable().columns.adjust().draw();
      });
  }

  /**
   * Applies `selectpicker` styling (bootstrap-select) to every
   * `<select multiple>` element on the page.
   * Requires jQuery and bootstrap-select to be loaded.
   */
  function initSelectPickers() {
    if (!global.$ || !$.fn || !$.fn.selectpicker) {
      return;
    }
    $("select[multiple]").selectpicker({ width: "100%" });
  }

  /**
   * Copies `text` to the clipboard using `execCommand('copy')` with a
   * fallback to `window.prompt`.  Updates the element's tooltip title
   * temporarily to confirm success.
   * Requires jQuery (for `el.attr`).
   *
   * @param {string} text - The text to copy.
   * @param {jQuery} el   - The jQuery-wrapped trigger element whose tooltip
   *                        title is temporarily updated.
   */
  function copyToClipboard(text, el) {
    var copyTest = document.queryCommandSupported("copy");
    var elOriginalText = el.attr("data-original-title");

    if (copyTest === true) {
      var copyTextArea = document.createElement("textarea");
      copyTextArea.value = text;
      document.body.appendChild(copyTextArea);
      copyTextArea.select();
      try {
        var successful = document.execCommand("copy");
        var msg = successful ? "Copied!" : "Whoops, not copied!";
        el.attr("data-original-title", msg).tooltip("show");
      } catch (err) {
        console.warn("Unable to copy text to clipboard", err);
      }
      document.body.removeChild(copyTextArea);
      el.attr("data-original-title", elOriginalText);
    } else {
      global.prompt("Copy to clipboard: Ctrl+C or Command+C, Enter", text);
    }
  }

  /**
   * Attaches a click handler to every `.js-copy` button that reads the
   * `data-copy` attribute and passes it to `copyToClipboard`.
   * Requires jQuery.
   */
  function bindCopyButtons() {
    if (!global.$) {
      return;
    }
    $(".js-copy")
      .off("click.scoutCopy")
      .on("click.scoutCopy", function() {
        var text = $(this).attr("data-copy");
        var el = $(this);
        copyToClipboard(text, el);
      });
  }

  /**
   * Converts a plain HTML table into a scrollable DataTable when the
   * table has more than 5 rows.  The table is left as-is for smaller
   * data sets so the page does not load DataTables unnecessarily.
   * Requires jQuery and DataTables.
   *
   * @param {string} tableId - The `id` attribute of the `<table>` element.
   */
  function setScrollyTable(tableId) {
    if (!global.$ || !$.fn || !$.fn.DataTable) {
      return;
    }
    var table = document.getElementById(tableId);
    if (!table || !table.rows || table.rows.length <= 5) {
      return;
    }
    $("#" + tableId).DataTable({
      scrollY: 350,
      stripeClasses: [],
      scrollCollapse: true,
      paging: false,
      searching: false,
      ordering: true,
      info: false,
    });
  }

  /**
   * Replaces the tooltip on `element` with a new one showing `tooltipText`.
   * Any existing Bootstrap Tooltip instance is disposed before the new one
   * is created to avoid duplicate tooltips.
   *
   * @param {HTMLElement} element     - The DOM element to attach the tooltip to.
   * @param {string}      tooltipText - Text to display in the new tooltip.
   * @returns {bootstrap.Tooltip} The newly created Tooltip instance.
   */
  function setTooltipContent(element, tooltipText) {
    var existingTooltip = bootstrap.Tooltip.getInstance(element);
    if (existingTooltip) {
      existingTooltip.dispose();
    }
    element.title = tooltipText;
    element.dataset.bsTitle = tooltipText;
    element.dataset.bsToggle = "tooltip";
    return new bootstrap.Tooltip(element, { container: "body" });
  }

  /**
   * Hides all elements with the class `complete-coverage-indicator` by
   * setting their `display` style to `"none"`.  Called when the coverage
   * API returns no data or when the request fails.
   */
  function hideCoverageIndicators() {
    var elements = document.getElementsByClassName("complete-coverage-indicator");
    for (var i = 0; i < elements.length; i += 1) {
      elements[i].style.display = "none";
    }
  }

  /**
   * Fetches Chanjo2 gene coverage data from `coverageUrl` and updates the
   * per-gene coverage indicator buttons on the page.
   *
   * Each gene is expected to have three DOM elements following the naming
   * convention `coverage-indicator-<hgncId>-{button,icon,text}`.
   *
   * - If coverage is complete the button turns green with a check icon.
   * - If coverage is incomplete the button turns yellow with a warning icon.
   * - If the API returns no data or the request fails, all indicators are hidden.
   *
   * Requires jQuery for `$.getJSON`.
   *
   * @param {string} coverageUrl - The URL of the Scout gene coverage API endpoint,
   *                               rendered by Jinja `url_for(...)` in the template.
   */
  function updateGeneHasFullCoverage(coverageUrl) {
    if (!global.$ || !coverageUrl) {
      return;
    }
    $.getJSON(coverageUrl, function(data) {
      var coverageByGene = data && data.gene_has_full_coverage ? data.gene_has_full_coverage : {};
      if ($.isEmptyObject(coverageByGene)) {
        hideCoverageIndicators();
        return;
      }

      Object.entries(coverageByGene).forEach(function(entry) {
        var hgncId = entry[0];
        var hasCompleteCoverage = entry[1];

        var coverageIndicatorButton = document.getElementById("coverage-indicator-" + hgncId + "-button");
        var coverageIndicatorIcon = document.getElementById("coverage-indicator-" + hgncId + "-icon");
        var coverageIndicatorText = document.getElementById("coverage-indicator-" + hgncId + "-text");

        if (!coverageIndicatorButton || !coverageIndicatorIcon || !coverageIndicatorText) {
          return;
        }

        coverageIndicatorButton.classList.remove("btn-info", "btn-success", "btn-warning");
        coverageIndicatorIcon.classList.remove(
          "blink_me",
          "fa-circle-question",
          "fa-circle-check",
          "fa-triangle-exclamation"
        );

        if (hasCompleteCoverage) {
          coverageIndicatorButton.classList.add("btn-success");
          coverageIndicatorButton.setAttribute(
            "data-bs-original-title",
            "Chanjo2 coverage is at 100% completeness."
          );
          coverageIndicatorIcon.classList.add("fa-circle-check");
          coverageIndicatorText.textContent = "Complete";
          return;
        }

        coverageIndicatorButton.classList.add("btn-warning");
        coverageIndicatorButton.setAttribute(
          "data-bs-original-title",
          "Note that Chanjo2 coverage is below 100% completeness."
        );
        coverageIndicatorIcon.classList.add("fa-triangle-exclamation");
        coverageIndicatorText.textContent = "Incomplete";
      });
    }).fail(function() {
      hideCoverageIndicators();
    });
  }

  /**
   * Wires up collapse/expand chevron rotation for the "Matching variants"
   * Bootstrap collapse panel.
   *
   * Listens for `show.bs.collapse` and `hide.bs.collapse` on the element
   * identified by `collapseId` and rotates the `.matching-variants-chevron`
   * icon inside the nearest `.card` ancestor accordingly.
   *
   * @param {string} [collapseId="matchingVariantsCollapse"] - The `id` of
   *   the Bootstrap collapse element to observe.
   */
  function initMatchingVariantsChevron(collapseId) {
    var collapseElement = document.getElementById(collapseId || "matchingVariantsCollapse");
    if (!collapseElement) {
      return;
    }

    collapseElement.addEventListener("show.bs.collapse", function() {
      var chevron = collapseElement.closest(".card").querySelector(".matching-variants-chevron");
      if (chevron) {
        chevron.style.transform = "rotate(180deg)";
      }
    });

    collapseElement.addEventListener("hide.bs.collapse", function() {
      var chevron = collapseElement.closest(".card").querySelector(".matching-variants-chevron");
      if (chevron) {
        chevron.style.transform = "rotate(0deg)";
      }
    });
  }

  /**
   * Toggles the Font Awesome angle icon inside a collapsible panel heading
   * between `fa-angle-down` (collapsed) and `fa-angle-up` (expanded).
   * Intended to be called from an `onclick` attribute on the heading element.
   *
   * Looks for a child element with class `rotate-icon` first; falls back to
   * `firstElementChild` if that class is not present.
   *
   * @param {HTMLElement} element - The panel heading element that was clicked.
   */
  function flipArrowIcon(element) {
    if (!element) {
      return;
    }
    var icon = element.querySelector(".rotate-icon") || element.firstElementChild;
    if (!icon) {
      return;
    }

    if (element.classList.contains("collapsed")) {
      icon.classList.replace("fa-angle-down", "fa-angle-up");
      return;
    }
    icon.classList.replace("fa-angle-up", "fa-angle-down");
  }

  /**
   * Master initialiser for a variant detail page.  Runs all standard
   * Bootstrap and UI setup tasks in one call.
   *
   * Tab selectors can be overridden via `options.tabSelectors` so pages
   * that only show a subset of tabs (e.g. SV variants without a Proteins
   * tab) still work correctly.
   *
   * @param {Object}   [options]              - Optional configuration object.
   * @param {string[]} [options.tabSelectors] - Array of CSS selectors for
   *   tab trigger elements to activate.  Defaults to genes and transcripts
   *   tabs: `["#nav-genes-tab", "#nav-transcripts-tab"]`.
   */
  function initVariantScripts(options) {
    var opts = options || {};
    var tabSelectors = opts.tabSelectors || ["#nav-genes-tab", "#nav-transcripts-tab"];

    tabSelectors.forEach(function(tabSelector) {
      initBootstrapTab(tabSelector);
    });

    initTooltips();
    initPopovers();
    initTabDataTableResize();
    initSelectPickers();
    bindCopyButtons();
    initMatchingVariantsChevron();
  }

  global.init_variant_scripts = initVariantScripts;
  global.init_bootstrap_tab = initBootstrapTab;
  global.copyToClipboard = copyToClipboard;
  global.set_scrolly_table = setScrollyTable;
  global.set_tooltip_content = setTooltipContent;
  global.update_gene_has_full_coverage = updateGeneHasFullCoverage;
  global.init_matching_variants_chevron = initMatchingVariantsChevron;
  global.flipArrowIcon = flipArrowIcon;
})(globalThis);

