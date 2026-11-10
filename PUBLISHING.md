# Publish the research website

The public site lives in `almahfooz/almahfooz.github.io`. Its default branch is `master`.
The GitHub Pages source is the repository root. The public CV is at `/cv/`, the PDF at
`/downloads/Mahfooz-Ahmed-CV.pdf`, and Fieldnotes at `/blog/`.

## Run it on your PC

From the folder containing `index.html`, run:

```powershell
py -m http.server 8000 --bind 127.0.0.1
```

Open http://127.0.0.1:8000/ in your browser. Use Ctrl+C to stop the server.
On macOS or Linux use `python3` in place of `py`.

## Publish from GitHub

Merge the research website changes into `master`. Under **Settings → Pages**,
choose **Deploy from a branch**, **master**, and **/ (root)**, then save.
Check the **Actions** tab for the completed Pages deployment.
The public address is https://almahfooz.github.io/.

The public contact form opens an email draft in the visitor’s email app.
The original hosted editor and its private enquiries inbox are separate from this edition.

## Add the next Fieldnotes issue

1. In `fieldnotes/`, copy `2026-11.json` to the new issue month, for example `2026-12.json`.
2. Edit the month, URL slug, title, category, summary, sections and source links.
   Use this directory for issues ready for public release. Keep the slug stable after publication.
3. From the repository root, regenerate the public pages and RSS feed:

```powershell
py tools/publish_fieldnotes.py
```

4. Open the local homepage and `/blog/`, review the new issue, then publish:

```powershell
git add -- fieldnotes blog index.html feed.xml
git commit -m "Publish the next Fieldnotes issue"
git push origin master
```

The blog link stays the same each month. Articles prepared in the private journal
can be copied here when they are ready for publication.
