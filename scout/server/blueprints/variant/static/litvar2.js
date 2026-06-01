(function(global) {
  "use strict";

  /**
   * Disposes any existing Bootstrap Tooltip on `element`, then creates and
   * attaches a new tooltip with `tooltipText`.  Delegates to
   * `global.set_tooltip_content` (from `variant_scripts.js`) when available
   * so the implementation is not duplicated.
   *
   * @param {HTMLElement} element     - The DOM element to attach the tooltip to.
   * @param {string}      tooltipText - Text to show in the new tooltip.
   * @returns {bootstrap.Tooltip} The newly created Tooltip instance.
   */
  function setTooltipContent(element, tooltipText) {
    if (typeof global.set_tooltip_content === "function") {
      return global.set_tooltip_content(element, tooltipText);
    }
    let existingTooltip = bootstrap.Tooltip.getInstance(element);
    if (existingTooltip) {
      existingTooltip.dispose();
    }
    element.title = tooltipText;
    element.dataset.bsTitle = tooltipText;
    element.dataset.bsToggle = "tooltip";
    return new bootstrap.Tooltip(element, { container: "body" });
  }

  /**
   * Disposes any existing Bootstrap Tooltip on `link` and removes the
   * element from the DOM.  Used when the LitVar API confirms that a
   * variant or gene has no corresponding LitVar record.
   *
   * @param {HTMLElement} link - The anchor element to dispose and remove.
   */
  function removeLinkWithTooltip(link) {
    let existingTooltip = bootstrap.Tooltip.getInstance(link);
    if (existingTooltip) {
      existingTooltip.dispose();
    }
    link.remove();
  }

  /**
   * Converts a Fetch `Response` to the `{ ok, data }` shape used by the
   * LitVar handlers.
   *
   * @param {Response} response - The HTTP response returned by `fetch()`.
   * @returns {Promise<{ok: boolean, data: Object}>} Parsed response payload.
   */
  function toResult(response) {
    return response.json().then(function(data) {
      return { ok: response.ok, data: data };
    });
  }

  /**
   * Applies the LitVar SNP verification result to the matching anchor.
   *
   * @param {Object} result - Parsed API result object.
   * @param {HTMLElement} link - Anchor element being updated.
   * @param {string} rsid - The rsID being verified.
   */
  function handleLitvarSnpResult(result, link, rsid) {
    if (result.ok && result.data.rsid && result.data.link) {
      const tooltipText =
        "Click to view " +
        rsid +
        " on LitVar2 (" +
        result.data.pmids_count +
        " articles)";
      link.href = result.data.link;
      setTooltipContent(link, tooltipText);
      return;
    }

    if (result.ok && !result.data.rsid) {
      removeLinkWithTooltip(link);
      return;
    }

    console.warn("Could not verify LitVar ID " + rsid + ", keeping fallback link.");
  }

  /**
   * Applies the LitVar gene verification result to the matching anchor.
   *
   * @param {Object} result - Parsed API result object.
   * @param {HTMLElement} link - Anchor element being updated.
   * @param {string} query - Gene query string being verified.
   */
  function handleLitvarGeneResult(result, link, query) {
    if (result.ok && result.data.rsid && result.data.link) {
      const tooltipText =
        "Open LitVar2 for " + query + " (first hit: " + result.data.rsid + ")";
      link.href = result.data.link;
      link.classList.remove("disabled");
      link.ariaDisabled = "false";
      setTooltipContent(link, tooltipText);
      return;
    }

    if (result.ok && !result.data.rsid) {
      removeLinkWithTooltip(link);
      return;
    }

    console.warn("Could not resolve LitVar gene link for query: " + query);
  }

  /**
   * Verifies every `.litvar-snp-link[data-litvar-rsid]` element on the
   * page against the Scout LitVar sensor API.
   *
   * For each link the rsID is extracted from the `data-litvar-rsid`
   * attribute and sent to the sensor endpoint (rendered via Jinja's
   * `url_for` and passed in as `sensorUrlTemplate`).  The placeholder
   * `__RSID__` in the template string is replaced at runtime.
   *
   * - If the API returns a valid record the link's `href` is updated
   *   and its tooltip is set to show the article count.
   * - If the API confirms no record exists the link is removed from
   *   the DOM.
   * - On network errors the link is left unchanged with a console warning.
   *
   * @param {string} sensorUrlTemplate - URL template string containing
   *   the literal placeholder `__RSID__`, e.g.
   *   `"/variant/litvar/sensor/__RSID__"`.
   *   Rendered by Jinja `url_for("variant.litvar_sensor", rsid="__RSID__")`
   *   in the template.
   */
  function verifyLitvarSnpIds(sensorUrlTemplate) {
    if (!sensorUrlTemplate) {
      return;
    }

    let snpLinks = document.querySelectorAll(".litvar-snp-link[data-litvar-rsid]");
    snpLinks.forEach(function(link) {
      let rsid = link.dataset.litvarRsid;
      if (!rsid) {
        return;
      }

      let litvarApiUrl = sensorUrlTemplate.replace("__RSID__", encodeURIComponent(rsid));
      fetch(litvarApiUrl)
        .then(toResult)
        .then(function(result) {
          handleLitvarSnpResult(result, link, rsid);
        })
        .catch(function(error) {
          console.warn("Could not verify LitVar ID " + rsid + ", keeping fallback link.", error);
        });
    });
  }

  /**
   * Resolves every `.litvar-gene-link[data-litvar-gene-query]` element on
   * the page by querying the Scout LitVar autocomplete API.
   *
   * For each link the gene symbol is read from `data-litvar-gene-query`
   * and appended to `autocompleteUrl` as the `query` parameter.
   *
   * - If the API returns a first-hit record the link is enabled (`.disabled`
   *   class removed, `aria-disabled` set to `"false"`), its `href` is updated,
   *   and a tooltip showing the gene name and matched rsID is attached.
   * - If the API confirms no record exists the link is removed from the DOM.
   * - On network errors the link is left unchanged with a console warning.
   *
   * @param {string} autocompleteUrl - Base URL of the Scout LitVar autocomplete
   *   endpoint (without query string), rendered by Jinja
   *   `url_for("variant.litvar_autocomplete")` in the template.
   */
  function verifyLitvarGeneLinks(autocompleteUrl) {
    if (!autocompleteUrl) {
      return;
    }

    const geneLinks = document.querySelectorAll(".litvar-gene-link[data-litvar-gene-query]");
    geneLinks.forEach(function(link) {
      let query = link.dataset.litvarGeneQuery;
      if (!query) {
        return;
      }

      fetch(autocompleteUrl + "?query=" + encodeURIComponent(query))
        .then(toResult)
        .then(function(result) {
          handleLitvarGeneResult(result, link, query);
        })
        .catch(function(error) {
          console.warn("Could not resolve LitVar gene link for query: " + query, error);
        });
    });
  }

  /**
   * Master initialiser for LitVar2 integration on a variant page.
   * Calls `verifyLitvarSnpIds` and `verifyLitvarGeneLinks` with the
   * Jinja-rendered Scout API URLs supplied through `options`.
   *
   * Designed to be called from a small inline `<script>` block in the
   * Jinja template that provides the URL values:
   *
   * ```html
   * {{ litvar2_scripts() }}
   * ```
   *
   * which expands to:
   *
   * ```html
   * <script src=".../litvar2.js"></script>
   * <script>
   *   init_litvar2({
   *     sensorUrlTemplate: '/variant/litvar/sensor/__RSID__',
   *     autocompleteUrl:   '/variant/litvar/autocomplete'
   *   });
   * </script>
   * ```
   *
   * @param {Object} [options]                    - Configuration object.
   * @param {string} [options.sensorUrlTemplate]  - URL template for the per-rsID
   *   sensor endpoint; must contain the literal string `__RSID__` as placeholder.
   * @param {string} [options.autocompleteUrl]    - Base URL for the gene
   *   autocomplete endpoint (query string appended at runtime).
   */
  function initLitvar2(options) {
    let opts = options || {};
    verifyLitvarSnpIds(opts.sensorUrlTemplate);
    verifyLitvarGeneLinks(opts.autocompleteUrl);
  }

  global.verify_litvar_snp_ids = verifyLitvarSnpIds;
  global.verify_litvar_gene_links = verifyLitvarGeneLinks;
  global.init_litvar2 = initLitvar2;
})(globalThis);

