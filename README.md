# Scita for Odoo 20: app store page

**Live preview:** https://biztechdesign.github.io/scita-v20-app-page/

Rebuilt from the client's *Theme Scita: Feature Updates* doc and the *AJ Scita Infographic Mockup*.

## What to upload

`odoo_description/` holds the finished page:

- `odoo_description/index.html`: goes to `theme_scita/static/description/index.html`.
- `odoo_description/images/`: goes to `theme_scita/static/description/images/`. It holds the 9 JPGs, 1 GIF and the support illustration.
- `odoo_description/preview.html`: the same page with Bootstrap loaded, for opening locally in a browser. Don't upload it.

## Page order

| # | Image | Section |
|---|-------|---------|
| 01 | `01-hero.jpg` | Hero (teal #0F5C61), Why Scita, Live Preview strip |
| 02 | `02-image-hotspot.gif` | Image Hotspot with 3D & AR View (animated) |
| 03 | `03-ai-companion.jpg` | AI-Powered Shopping Companion |
| 04 | `04-stay-ahead.jpg` | "Stay Ahead" heading, Price Drop Alerts, Free Shipping Progress Bar |
| 05 | `05-pwa-speed.jpg` | PWA + Google PageSpeed score |
| 06 | `06-predictive-search.jpg` | Divider + Predictive Search |
| 07 | `07-b2b.jpg` | B2B (now with Request a Quote + Hide Price & Disable Cart) |
| 08 | `08-industry.jpg` | Industry + collage (84 snippets, AI & AR tile) |
| 09 | `09-comparison.jpg` | Scita vs Other Odoo Themes |
| 10 | `10-essential-features.jpg` | Essential Features (8 items) + upgrade note |
| HTML | in `index.html` | FAQs (fixed), Changelog, Support |

## Editing and regenerating

Every image is generated from HTML, so text, colours and visuals can be changed without design software.

- Sections: `folds/NN-*.html`. Shared colours, type and components: `folds/scita.css`.
- Re-export images: `python tools/render.py` (all) or `python tools/render.py 03-ai` (one).
  - `export/NN-*.jpg`: 1600px, page-ready.
  - `export/png/`: 2x masters.
- Rebuild the hotspot GIF: `python tools/make_gif.py`. The frame timeline is in `seq()` in that file.
- Rebuild the page: `python tools/build_page.py`. FAQ text comes from `tools/faq_source.json` plus the fixes in the script.
- Swapping a visual: replace the file in `assets/` and re-run the render. For example, put a real product photo in place of `assets/renders/sofa_34.png`, or a real store recording in place of the GIF.
- 3D renders: `blender/scene.py` (procedural room + sofa, Blender 5.2, Cycles). Re-run them with `blender/render_all.sh`.
- **Hero Live Preview laptops:** the supplied hi-res transparent artwork `assets/source_extra/scita_v19_supplied.png` (4025x2538), resized to `assets/renders/live_laptops.png` (2480px wide). To update it, replace that file and re-run `python tools/render.py 01-hero`. `tools/knockout_laptops.py` (white-background cutout) is no longer needed.
- **Blender version of the laptops (not used):** `blender/paper_laptop.py` renders the same idea.
  - Textures come from `python tools/capture_long.py`, which writes `assets/shots/*_tex.png`.
  - Render with `blender/render_laptops.sh`, then trim with `python tools/trim_renders.py`.
- QA checks:
  - `python tools/test_faq.py`: the FAQ arrow flips.
  - `python tools/test_responsive.py`: no overflow or clipping at 320, 375, 768 and 1300px.

## Image sources (all high resolution)

- **Store screenshots:** captured from the live Scita demo stores at 2x with `python tools/capture_demos.py` and `python tools/capture_more.py`, saved in `assets/shots/`. The collage tiles are cut from these by `tools/crop_shots.py`.
- **Product photos:** 500px originals downloaded from the grocery demo, in `assets/products/`.
- **QR codes:** generated as SVG in `assets/qr/`, so they stay sharp at any size. They link to the **v19** demo stores (electronics, grocery, furniture, w2p). Swap them for the v20 demo URLs when those are public; `theme-scita-v20.appjetty.com` currently only redirects to the Odoo login.
- **Exported JPGs:** 2000px wide, quality 92, 4:4:4 colour, so coloured text stays crisp.
- `assets/crops/` holds the old low-res cut-outs from the v19 images. They are no longer used.

## Placeholders to replace when real material exists

- **3D room and sofa** (hero, hotspot GIF, price drop widget, AI & AR tile) are Blender renders, not real store screenshots.
- **Hotspot GIF** is a rendered UI simulation. Per the mockup, the final art should be a recording of the real Scita hotspot → 3D → AR flow.
- **AI cards** (chat, photo search, comparison) and the Price Drop / Free Shipping widgets are illustrative UI.
- **"View in Your Room" QR** links to the Furniture demo, since there is no AR-specific link.

## Additions beyond the doc (for review)

- **Odoo 20 wording:**
  - Hero subheading says "An Odoo 20 Theme That Offers".
  - FAQ compatibility answers say "v17, v18, v19, and v20".
  - The closing note says "Scita 20 introduces…".
- **Small labels added:**
  - Hero: "Scita for Odoo 20" pill above the headline.
  - AI fold: "New in Scita 20" tag.
- **Live Preview strip:** follows the original composition. The pill, arrows and 3 QR codes (Web to Print, Grocery, Furniture) are crisp HTML and SVG. The laptops are the supplied hi-res artwork. The Electronics QR was removed on request.
- **Hero visual:** the "Why Scita" point "3D Product Preview Powered by AR" is visually highlighted.
- **Free Shipping fold:** two pills, "Set in Delivery Method" and "Smart Suggestions", taken from the doc's own copy.
- **AI fold sample UI:** uses real demo products. The comparison card shows "Choco Milk · 250 ml / Family Pack" instead of "Juice A / Juice B", and the chat asks "Crunchy snacks under $10?" and suggests Pringles. The comparison summary was reworded to match.
- **Price Drop widget:** shows an email toast ("Good news! The price just dropped").
- **Mockup defaults kept:** the "Built to Convert" eyebrow and the divider title "Built on the Features That Made Scita Popular".
- **Changelog:** rebuilt as "Version 20.0" with 4 release-note bullets. There is no release date; add one.
- **FAQ, Changelog and Support headings:** now HTML text in teal. The old pink and purple heading images and the pink support background are gone.
- **FAQ markup:** now uses Bootstrap 5's accordion, whose arrow flips on every open and close. Tested.

## Still worth checking

- **"Partially" values:** the "Partially" entries for AI Shopping Assistant and Request a Quote in the comparison table. The mockup flagged them to verify.
- **Bento UI wording in the FAQ:** "What makes Scita different…" still says "first theme with Bento UI" (unchanged, since it isn't in the doc), while Bento UI is now a one-liner.
