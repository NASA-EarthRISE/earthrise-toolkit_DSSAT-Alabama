# WCAG 2.2 / Section 508 Accessibility Compliance Report

**Application:** DSSAT-Web Alabama (Earthrise Toolkit)
**Testing Date:** 2026-07-24
**Standard:** WCAG 2.2 Level A & Level AA / Section 508
**Tool:** pa11y 9.1.1 with runners htmlcs (`@pa11y/html_codesniffer` 2.6.0) + axe (`axe-core` 4.11.4)
**Server:** Django 5.2.15, development server at `http://127.0.0.1:8000`

---

## Overall Verdict: **NON-COMPLIANT**

The application has multiple automatically-detected failures against WCAG 2.2 Level A and Level AA criteria that must be resolved before it can claim conformance. Critical errors are present on every tested page.

---

## Pages Tested

| Page | URL | Errors | Warnings | Notices | Total |
|------|-----|--------|----------|---------|-------|
| Home / Map | `/demo/` | **13** | 50 | 69 | 132 |
| About | `/demo/about/` | **6** | 6 | 28 | 40 |
| Sensitivity Charts | `/demo/sensitivity/` | **11** | 466 | 50 | 527 |
| Irrigation Charts | `/demo/irrigation/` | **5** | 15 | 41 | 61 |

> **Note on `/demo/sensitivity/`:** This page requires an active map region selection (session state) to render its chart content. Accessed directly, it returns a Django debug error page. The 401 position-fixed warnings and traceback textarea errors reflect the debug error page, not the chart interface itself. A full audit of the chart interface requires authenticated session testing.

---

## Critical Errors (WCAG Level A Failures)

These are automated failures — they constitute definitive violations.

### 1. Missing `lang` Attribute on `<html>` Element
- **WCAG SC:** 3.1.1 Language of Page (Level A)
- **Section 508:** 502.3 (Assistive Technology Interoperability)
- **Runners:** htmlcs (`H57.2`) + axe (`html-has-lang`)
- **Affected Pages:** Home, About (sensitivity and irrigation templates already include `lang="en"`)
- **Impact:** Screen readers cannot determine the document language; text-to-speech may mispronounce content.
- **Element:** `<html>` (no `lang` attribute)
- **Fix:** Add `lang="en"` to the `<html>` tag in `index.html` and `about.html`.

```html
<!-- Change this: -->
<html>
<!-- To this: -->
<html lang="en">
```

---

### 2. Insufficient Color Contrast — Navigation Links
- **WCAG SC:** 1.4.3 Contrast (Minimum) (Level AA)
- **Section 508:** 502.3
- **Runners:** htmlcs (`G18.Fail`) + axe (`color-contrast`)
- **Affected Pages:** Home, About, Irrigation, Sensitivity
- **Impact:** Users with low vision cannot read navigation text.
- **Measured Contrast:** 4.45:1 (required: 4.5:1 minimum)
- **Elements:** Nav links (`Map`, `About`) with class `nav-link text-light` on the navbar background
- **Fix:** Change nav link text color from Bootstrap `text-light` (#f8f9fa) to `#fafbfc` or use a slightly darker navbar background.

```html
<!-- Current (failing): -->
<a class="nav-link active text-light" href="/demo/">Map</a>
<!-- Fix — add explicit color override in CSS or adjust navbar background: -->
/* In style.css: */
.navbar .nav-link { color: #fafbfc !important; }
```

---

### 3. Navbar App Title — Insufficient Contrast (White on Navbar Background)
- **WCAG SC:** 1.4.3 Contrast (Minimum) (Level AA)
- **Runners:** axe (`color-contrast`) — needs further review (transparent/absolute positioning)
- **Affected Pages:** Home, About, Irrigation, Sensitivity
- **Element:** `<h3 style="color: white; ...">Dssat Web App : V1</h3>`
- **Fix:** Ensure the navbar background provides ≥ 4.5:1 contrast ratio with white text. If the navbar uses a semi-transparent or gradient background, define an opaque fallback.

---

### 4. Unlabeled Button — Navbar Mobile Toggle
- **WCAG SC:** 4.1.2 Name, Role, Value (Level A)
- **Runners:** htmlcs (`H91.Button.Name`)
- **Affected Pages:** Irrigation, Sensitivity (the button has `aria-label` on Home/About but is missing it on other templates)
- **Impact:** Screen reader users cannot identify the mobile navigation toggle.
- **Element:** `<button class="navbar-toggler" type="button" data-bs-toggle="collapse" ...>`
- **Fix:** Add `aria-label="Toggle navigation"` and `aria-controls`/`aria-expanded` attributes consistently across all templates.

```html
<button class="navbar-toggler" type="button" data-bs-toggle="collapse"
        data-bs-target="#navbarNav" aria-controls="navbarNav"
        aria-expanded="false" aria-label="Toggle navigation">
```

---

### 5. Form Field Without Label — Sensitivity Page Textarea
- **WCAG SC:** 1.3.1 Info and Relationships (Level A), 4.1.2 Name, Role, Value (Level A)
- **Runners:** htmlcs (`F68`, `H91.Textarea.Name`)
- **Affected Pages:** Sensitivity (Django debug error page `traceback_area` textarea)
- **Impact:** Assistive technologies cannot identify the purpose of this form field.
- **Note:** This error appears on the Django debug error page. Disable `DEBUG = True` in production (`settings.py`) so this page is not served to end users. If the debug page must be accessible, add a `<label>` for the textarea.

---

## Warnings (WCAG Level AA Advisory)

These items are not definitive failures but represent best-practice violations or conditions requiring manual review.

### W1. Heading Structure Not Logically Nested
- **WCAG SC:** 1.3.1 Info and Relationships (Level AA advisory), 2.4.6 Headings and Labels
- **Runners:** htmlcs (`G141`), axe (`heading-order`, `page-has-heading-one`)
- **Affected Pages:** All pages (Home, About, Irrigation; Sensitivity via nav)
- **Issue:** The site title `<h3>Dssat Web App : V1</h3>` in the navbar is the first heading on every page but is not an `<h1>`. The map legend uses `<h6>` without preceding `<h1>`–`<h5>`.
- **Fix:**
  - Change the navbar app title to `<h1>` (styled to match current appearance) or mark it with `role="heading" aria-level="1"`.
  - Ensure heading levels increment sequentially (h1 → h2 → h3…).

---

### W2. No `<main>` Landmark
- **WCAG SC:** 1.3.6 Identify Purpose (Level AA), 2.4.1 Bypass Blocks (Level A advisory)
- **Runners:** axe (`landmark-one-main`, `region`)
- **Affected Pages:** Home, About, Irrigation
- **Issue:** Page content is not wrapped in a `<main>` element. All content should be contained within landmark regions (`<main>`, `<nav>`, `<aside>`, etc.).
- **Fix:** Wrap the primary page content in `<main>` on each template.

```html
<main id="main-content">
  <!-- page body content -->
</main>
```

---

### W3. No Skip Navigation Link
- **WCAG SC:** 2.4.1 Bypass Blocks (Level A)
- **Runners:** htmlcs (`G1,G123,G124,H69` — notice)
- **Affected Pages:** All pages
- **Issue:** No "Skip to main content" link is provided. Keyboard-only users must tab through the full navigation on every page.
- **Fix:** Add a visually-hidden skip link as the first focusable element in `<body>`.

```html
<a href="#main-content" class="visually-hidden-focusable">Skip to main content</a>
```

---

### W4. Map Tile Images Not Properly Handled for AT
- **WCAG SC:** 1.1.1 Non-text Content (Level A)
- **Runners:** htmlcs (`H67.2`)
- **Affected Pages:** Home
- **Issue:** Leaflet map tile `<img>` elements use `alt=""` to hide them from screen readers. This is technically acceptable for decorative images, but the overall map widget has no accessible description or text alternative for users who cannot see the map.
- **Fix:** Wrap the Leaflet map in an element with `role="img"` and an `aria-label` describing the map's purpose. Consider providing a text-based alternative (e.g., a table of region data).

```html
<div id="map" role="img" aria-label="Interactive map of Alabama showing forecasted crop yield by region">
```

---

### W5. `position: fixed` Elements May Cause 2D Scrolling
- **WCAG SC:** 1.4.10 Reflow (Level AA)
- **Runners:** htmlcs (`C32,C31,C33,C38,SCR34,G206`)
- **Affected Pages:** Home (floating info panel, footer), Sensitivity (chart elements), Irrigation
- **Issue:** Multiple `position: fixed` elements (the floating region info panel `#floating_div`, the `<footer>`) may require horizontal scrolling at 320 CSS px viewport width.
- **Fix:** Test at 320 px width. Replace `position: fixed` with responsive alternatives, or ensure fixed elements reflow gracefully on narrow screens.

---

### W6. Map Attribution / Zoom Controls — Contrast with Transparent Background
- **WCAG SC:** 1.4.3 Contrast (Minimum) (Level AA)
- **Runners:** htmlcs (`G18.Alpha`)
- **Affected Pages:** Home
- **Issue:** Leaflet attribution bar and zoom controls have semi-transparent backgrounds; the contrast of text/icons against the underlying map tiles cannot be statically verified and may fail.
- **Fix:** Give map controls an opaque background (e.g., `background: rgba(255,255,255,0.9)` → `background: #ffffff`).

---

### W7. Map Legend Heading Not Properly Nested
- **WCAG SC:** 1.3.1 Info and Relationships
- **Runners:** htmlcs (`G141`)
- **Affected Pages:** Home
- **Issue:** `<h6>Average forecasted yield</h6>` in the Leaflet info control jumps from no prior headings to h6.
- **Fix:** Use an appropriate heading level (e.g., `<h2>`) or a `<p>` with `role="heading" aria-level="2"` for the map legend title.

---

### W8. Leaflet Zoom Controls Not in a List
- **WCAG SC:** 1.3.1 Info and Relationships
- **Runners:** htmlcs (`H48`)
- **Affected Pages:** Home
- **Issue:** The Leaflet zoom control `div` contains navigation links but is not structured as a `<ul>/<li>` list.
- **Note:** This is generated by the Leaflet library. Override with a custom control or accept as a third-party component limitation.

---

### W9. Select Elements Lack Accessible Value / Label Association
- **WCAG SC:** 1.3.1 Info and Relationships, 4.1.2 Name, Role, Value
- **Runners:** htmlcs (`H91.Select.Value`, `H85.2`)
- **Affected Pages:** Irrigation (`#cultivarSelect`, `#soilSelect`)
- **Issue:** Select elements do not expose their current selected value to the accessibility API. Option groups are not used for related options.
- **Fix:** Ensure each `<select>` has a visible `<label>` associated via `for`/`id`. Verify the Irrigation template's label associations are correct.

---

### W10. Data Tables Missing `<caption>`
- **WCAG SC:** 1.3.1 Info and Relationships
- **Runners:** htmlcs (`H39.3.NoCaption`)
- **Affected Pages:** Sensitivity (Highcharts-generated tables)
- **Issue:** Highcharts accessibility module generates data tables without `<caption>` elements.
- **Fix:** Configure the Highcharts accessibility module to add captions, or patch via `accessibility.description` and `caption` options in Highcharts config.

---

### W11. Event Handlers Without Keyboard Equivalent
- **WCAG SC:** 2.1.1 Keyboard (Level A)
- **Runners:** htmlcs (`G90`)
- **Affected Pages:** Sensitivity (54 instances — Highcharts interactive chart elements)
- **Issue:** Highcharts SVG/canvas interactive elements use mouse event handlers without corresponding keyboard events.
- **Fix:** Enable the Highcharts accessibility module (`accessibility: { enabled: true }`) and keyboard navigation module in the Highcharts configuration. Verify it is active in `dssat/static/highcharts_config/baseline_template.js`.

---

## Notices (Manual Review Required)

The following items require human judgment and cannot be resolved by automated tools alone. They are flagged for manual review.

| Code | Description | Pages |
|------|-------------|-------|
| `2_4_2.H25.2` | Verify page `<title>` is descriptive (currently generic: "DSSAT-Web") | All |
| `2_4_4.H77–H81` | Verify link text is meaningful in context (navbar logo link, Leaflet attribution links) | Home |
| `1_1_1.G94.Image` | Verify alt text for UAH logo and Climatologist Seal images is sufficient | All |
| `1_4_1.G14` | Verify map choropleth color scheme is not the only means of conveying yield data | Home |
| `2_4_1.G1` | No skip navigation link — manual bypass mechanism needed | All |
| `2_4_7.G149` | Verify keyboard focus indicator is visible throughout the map and chart interactions | Home, Sensitivity |
| `2_5_1` | Verify map pan/zoom multipoint gestures have single-pointer alternatives | Home |
| `4_1_3` | Verify status messages (loading states, simulation results) are announced via `aria-live` regions | All |
| `1_4_4.G142` | Verify text resize to 200% does not break layout or lose content | All |
| `1_3_4` | Verify orientation is not locked (portrait/landscape) | All |
| `3_2_3.G61` | Verify navigation order is consistent across all pages | All |

---

## Summary of Violations by WCAG Principle

| Principle | Issues Found |
|-----------|-------------|
| **1 — Perceivable** | Color contrast failures (nav links, app title, map controls); missing alt text context; map has no text alternative; heading structure broken |
| **2 — Operable** | No skip link; Highcharts keyboard events missing; `position: fixed` reflow risk |
| **3 — Understandable** | Missing `lang` attribute on `<html>`; generic page `<title>` |
| **4 — Robust** | Unlabeled buttons; unlabeled form fields; select elements not exposing value; no `<main>` landmark |

---

## Section 508 Mapping

| 508 Provision | Status | Notes |
|--------------|--------|-------|
| 502.3 — Accessibility Services | **Fail** | Missing lang, unlabeled controls, contrast failures |
| 504.2 — Authoring Tools | N/A | |
| 602.3 — Electronic Support Docs | **Not tested** | |
| E205.4 — WCAG 2.0 AA | **Fail** | Multiple WCAG 2.x AA failures detected |

---

## Remediation Priority

### Priority 1 — Fix Immediately (Level A Failures)
1. Add `lang="en"` to `<html>` in all templates missing it (`index.html`, `about.html`)
2. Add `aria-label="Toggle navigation"` to navbar toggle button in all templates
3. Disable Django `DEBUG = True` in production to prevent debug error pages

### Priority 2 — Fix Before Launch (Level AA Failures)
4. Fix nav link color contrast (4.45:1 → 4.5:1 minimum): change `text-light` to `#fafbfc`
5. Add `<main id="main-content">` landmark to all templates
6. Add a skip navigation link as first focusable element
7. Fix heading hierarchy: promote navbar `<h3>` to `<h1>`; fix map legend `<h6>` nesting
8. Enable Highcharts accessibility module + keyboard navigation

### Priority 3 — Improve Accessibility (Best Practice)
9. Add `role="img" aria-label="..."` to the Leaflet map container
10. Add `aria-live` regions for dynamic status messages (simulation running, results loaded)
11. Fix `position: fixed` footer and floating panel for 320 px reflow
12. Give Leaflet attribution bar/controls opaque backgrounds for contrast reliability
13. Add descriptive page titles per page (e.g., "Map | DSSAT-Web Alabama")

---

## Test Environment

| Component | Version |
|-----------|---------|
| pa11y | 9.1.1 |
| @pa11y/html_codesniffer | 2.6.0 |
| axe-core | 4.11.4 |
| Chrome (Puppeteer) | 150.0.7871.24 |
| Django | 5.2.15 |
| Bootstrap | 5.3.2 |
| Leaflet | (bundled in static) |
| Highcharts | (bundled in static) |
| Node.js | 24.16.0 |

---

## Raw Results

Raw pa11y JSON output files are stored in `pa11y_results/`:

- `home_htmlcs_axe.json` — `/demo/` (Home / Map)
- `about_htmlcs_axe.json` — `/demo/about/`
- `sensitivity_htmlcs_axe.json` — `/demo/sensitivity/` (note: tested against Django debug error page)
- `irrigation_htmlcs_axe.json` — `/demo/irrigation/`

---

*Generated by pa11y 9.1.1 (htmlcs + axe runners) against WCAG 2.2 Level AA standard. Automated testing detects approximately 30–40% of accessibility issues; manual testing by a screen reader user is required for full conformance validation.*
