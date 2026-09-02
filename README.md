# Auth Branding for Odoo 19

[![Odoo 19](https://img.shields.io/badge/Odoo-19.0-714B67.svg)](https://www.odoo.com/)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](LICENSE)

Auth Branding provides a visual Brand Studio for Odoo login, signup, and password-reset pages. Marketing or operations users can create a polished authentication experience without editing templates, while administrators retain safe draft publishing, rollback, import/export, and custom CSS controls.

## Highlights

- Five responsive layouts: Centered, Split, Full Bleed, Minimal, and Sidebar.
- Tabbed editor with a sticky desktop, tablet, and mobile preview.
- Instant preview updates for colors, content, links, dark mode, loading style, and CSS.
- Eight built-in themes plus company-specific custom themes.
- Three-step quick setup with automatic logo color suggestions.
- Logo, favicon, background image, typography, gradients, glass effects, and border controls.
- Separate login, signup, and password-reset titles and welcome messages.
- Styled social sign-in buttons, legal links, footer text, and customizable powered-by branding.
- Light, dark, or device-controlled appearance and reduced-motion support.
- Live WCAG contrast feedback, visible keyboard focus, responsive behavior, and RTL support.
- Draft, publish, discard, version history, and rollback workflows.
- Portable JSON packages with review-before-import and embedded image assets.
- Sanitized custom CSS for advanced local overrides.
- Multi-company record isolation and a dedicated Branding Manager group.
- Cache-aware public CSS and image routes with ETag and security headers.

## Installation

1. Copy `auth_branding` into an Odoo 19 custom add-ons directory.
2. Restart Odoo and update the Apps list.
3. Install **Auth Branding** from Apps.

The module depends on `web`, `auth_signup`, and `base_setup`. Pillow is used for logo palette extraction and is already part of a standard Odoo installation.

## Configuration

1. Open **Settings → General Settings**.
2. Find **Authentication Branding**.
3. Choose **Quick Setup** for a guided start, or **Open Brand Studio** for full control.
4. Select a theme and edit the compact Brand, Layout, Background, Content, and Advanced tabs.
5. Use the page and device controls above the sticky preview to verify every auth screen.
6. Resolve any contrast warnings shown in the collapsible **Design health** panel.
7. Save a draft as needed, then choose **Publish** when it is ready for users.

Only a published version is served on public authentication pages. **Discard Draft** restores the active published version, and **Version History** can restore and republish an older release while retaining the audit trail.

## Reusable themes

The Presets tab contains CSS-rendered previews of the built-in themes. Applying one changes only the current draft. Choose **Save Current Theme** to store the visual settings as a company-specific preset; custom presets can be deleted from the gallery, while built-in presets are protected.

Presets intentionally capture visual styling rather than company identity or page copy. Background images and safe custom CSS are included in custom visual themes.

## Import and export

Choose **Export** to download the current saved draft as a versioned JSON package. The package includes supported settings plus embedded logo, favicon, and background assets.

Choose **Import**, upload an Auth Branding JSON file, and review its source, setting count, asset count, and ignored future fields. Applying an import creates draft changes only; inspect the preview and publish separately. Files and individual assets have size limits, and field types, schema versions, and base64 data are validated.

## Custom CSS safety

The Advanced tab includes an escape hatch for experienced administrators. Custom CSS is versioned and appended after generated theme rules. To keep authentication pages safe, the module rejects:

- HTML tags and control characters;
- `@import`, `@charset`, and `@namespace` rules;
- `url()`, external protocols, and data URLs;
- JavaScript/VBScript, `expression()`, `behavior`, and legacy bindings;
- CSS escapes, unclosed comments, and payloads over 50 KB.

Use local selectors and declarations only. Bootstrap utility classes may require a more specific selector or `!important` for the small number of properties Odoo itself marks important.

## Access and multi-company behavior

System administrators inherit the **Authentication Branding Manager** group. Configuration, preset, and version records are isolated to allowed companies. Public users receive read-only access required to render the current company's published authentication theme; public routes cannot select an unrelated company configuration.

## Development and verification

Run the Odoo test suite from an Odoo 19 source checkout:

```bash
./odoo-bin --test-enable --stop-after-init -d auth_branding_test -i auth_branding
```

For an upgrade test against an existing database:

```bash
./odoo-bin --test-enable --stop-after-init -d your_database -u auth_branding
```

Manual browser checks should cover login, signup, and reset pages in every layout; mobile and RTL display; automatic dark mode; image caching; draft isolation; rollback; and OAuth providers installed in the target database.

## Changelog

### 19.0.2.0.0

- Rebuilt configuration as a tabbed Brand Studio with a responsive sticky preview.
- Added presets, guided setup, logo color extraction, five layouts, dark mode, social styles, metadata, and loading states.
- Added drafts, explicit publishing, version rollback, portable packages, safe CSS, and accessibility feedback.
- Hardened multi-company access, input validation, public routes, caching, and automated coverage.

## License and author

Licensed under [LGPL-3](LICENSE). Maintained by [Trishan Fernando](https://trishanfernando.com).
