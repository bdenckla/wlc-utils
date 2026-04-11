# wlc-utils
Westminster Leningrad Codex utilities

All tracked Python now lives under `py/`.

Current top-level Python buckets are:

- `py/python_modules/` for the older WLC-processing modules
- `py/pycmn/` for modules that match or nearly match the shared `pycmn` layer used in sibling repos
- `py/py_hebrew/` for Hebrew/Unicode helpers built on top of `pycmn`
- `py/py_html/` for shared HTML/presentation helpers split out of `py_misc`
- `py/py_uxlc/` for UXLC-specific parsing, location, and metadata helpers
- `py/py_wlc/` for shared WLC/Tanakh helpers used across multiple WLC-specific packages
- `py/py_wlc_a_notes/` for the WLC a-notes family
- `py/py_word_diffs_420422/` for the WLC 4.20/4.22 word-diffs family

The old transitional `py/py_misc/` compatibility layer has been removed.

Run the WLC JSON/Unicode workflow from the repo root with:

```powershell
.venv\Scripts\python.exe py\main_wlc_json_and_unicode.py
```

Additional WLC-focused entry scripts now live here as well:

```powershell
.venv\Scripts\python.exe py\main_wlc_a_notes.py
.venv\Scripts\python.exe py\main_word_diffs_420422.py
```

## GitHub Pages

The static site content for this repository lives under `gh-pages/` and is deployed by the GitHub Actions workflow in `.github/workflows/pages.yml`.

Once GitHub Pages is enabled for this repository with the GitHub Actions source, the expected published URLs are:

- `https://bdenckla.github.io/wlc-utils/`
- `https://bdenckla.github.io/wlc-utils/420422/`
- `https://bdenckla.github.io/wlc-utils/wlc-a-notes/`

The site root is `gh-pages/index.html`, which links to the two current published sections under `gh-pages/420422/` and `gh-pages/wlc-a-notes/`.
