"""Build the Fieldnotes archive, articles, home feature and RSS using the Python standard library."""
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://almahfooz.github.io"
KL = timezone(timedelta(hours=8))
E = lambda value: escape(str(value), quote=True)

def read_issues():
    current = datetime.now(KL).strftime("%Y-%m")
    items = []
    slugs = set()
    for path in sorted((ROOT / "fieldnotes").glob("*.json"), reverse=True):
        issue = json.loads(path.read_text(encoding="utf-8"))
        month = issue["month"]
        if not re.fullmatch(r"20\d\d-(0[1-9]|1[0-2])", month) or path.stem != month:
            raise ValueError(f"{path.name} must match the issue month YYYY-MM.")
        if month > current:
            raise ValueError(f"Keep {month} outside the public repository until its release month.")
        slug = issue["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in slugs:
            raise ValueError(f"Each issue needs a unique URL slug: {slug}")
        for name in ("title", "summary", "category"):
            if not isinstance(issue.get(name), str) or not issue[name].strip():
                raise ValueError(f"Missing {name} in {path.name}")
        if not issue["sections"]:
            raise ValueError(f"Missing article sections in {path.name}")
        for section in issue["sections"]:
            if not section["title"] or not section["paragraphs"] or not all(isinstance(p,str) and p.strip() for p in section["paragraphs"]):
                raise ValueError(f"Invalid article section in {path.name}")
        for source in issue.get("sources", []):
            u=urlsplit(source["url"])
            if not source["label"] or u.scheme != "https" or not u.hostname:
                raise ValueError(f"Each source needs a label and HTTPS URL in {path.name}")
        slugs.add(slug)
        items.append(issue)
    if not items:
        raise ValueError("Add a published issue to fieldnotes/ first.")
    return items

def month_text(issue):
    return datetime.strptime(issue["month"], "%Y-%m").strftime("%B %Y")

def article_path(issue):
    return "/blog/" + issue["slug"] + "/"

def article_html(issue):
    title, category, summary = (E(issue[k]) for k in ("title","category","summary"))
    words = sum(len(p.split()) for s in issue["sections"] for p in s["paragraphs"])
    reading = max(1, (words + 199) // 200)
    sections = "".join("<section><h2>"+E(s["title"])+"</h2>"+ "".join("<p>"+E(p)+"</p>" for p in s["paragraphs"])+"</section>" for s in issue["sections"])
    sources = "".join('<a href="'+E(s["url"])+'">'+E(s["label"])+'</a>' for s in issue.get("sources",[]))
    if sources:
        sections += '<section class="sources"><h2>Further reading</h2>'+sources+'</section>'
    if issue["slug"] == "before-you-submit-your-thesis":
        sections += '<a class="article-resource" href="/resources/thesis-checklist/">Open the thesis submission checklist →</a>'
    body = f'<main id="main"><header class="article-head"><div class="reading-shell"><a class="back" href="/blog/">← Fieldnotes monthly blog</a><p class="eyebrow"><span></span>{category} · {month_text(issue)}</p><h1>{title}<em>.</em></h1><p class="intro-copy">{summary}</p><div class="byline"><img src="/assets/images/mahfooz-outdoors.webp" alt=""><span>Dr. Mahfooz Ahmed</span><i></i>{reading} min read</div></div></header><article class="reading-shell article-body">{sections}<a class="inline-link" href="/blog/">← All monthly issues</a></article></main>'
    layout=(ROOT/"_templates/fieldnotes-article.html").read_text(encoding="utf-8")
    return layout.replace("@@SLUG@@",issue["slug"]).replace("@@TITLE@@",title+" | Fieldnotes").replace("@@SUMMARY@@",summary).replace("@@ARTICLE@@",body)

def replace_block(document, name, body):
    before, start, rest = document.partition("<!-- FIELDNOTES-"+name+" -->")
    old, end, after = rest.partition("<!-- END-FIELDNOTES-"+name+" -->")
    if not start or not end:
        raise ValueError(f"Missing Fieldnotes publishing markers for {name}")
    return before+start+body+end+after

def feature(issue, home):
    cover = (ROOT/"_templates/fieldnotes-cover.html").read_text(encoding="utf-8").replace("@@MONTH@@",month_text(issue))
    href = article_path(issue)
    archive = '<a class="inline-link feature-archive" href="/blog/">Monthly blog archive →</a>' if home else ""
    label = "Fieldnotes · Monthly blog" if home else "Latest issue"
    content = f'{cover}<div class="feature-copy"><p class="eyebrow"><span></span>{label}</p><span class="article-meta">{month_text(issue)} <i></i> {E(issue["category"])}</span><h2><a href="{href}">{E(issue["title"])}</a></h2><p>{E(issue["summary"])}</p><a class="action" href="{href}">Read this issue →</a>{archive}</div>'
    if home:
        return '<section class="journal-section"><div class="shell feature-grid">'+content+'</div></section>'
    return '<section class="shell journal-feature">'+content+'</section>'

def rss(issues):
    feed=ET.Element("rss",version="2.0")
    channel=ET.SubElement(feed,"channel")
    for k,v in {"title":"Fieldnotes · Dr. Mahfooz Ahmed","link":ORIGIN+"/blog/","description":"Monthly notes on academic writing, open science and research methods."}.items():
        ET.SubElement(channel,k).text=v
    for issue in issues:
        link=ORIGIN+article_path(issue)
        # The November 2026 issue launched on the 9th.
        day="09" if issue["month"]=="2026-11" else "01"
        date=datetime.fromisoformat(issue["month"]+"-"+day+"T09:00:00+08:00")
        item=ET.SubElement(channel,"item")
        for k,v in {"title":issue["title"],"link":link,"guid":link,"description":issue["summary"],"pubDate":format_datetime(date)}.items():
            ET.SubElement(item,k).text=v
    ET.indent(feed)
    return ET.tostring(feed,encoding="utf-8",xml_declaration=True)

def main():
    issues = read_issues()
    home = ROOT/"index.html"
    archive = ROOT/"blog/index.html"
    rows = "".join(f'<a class="archive-row" href="{article_path(i)}"><span>{month_text(i)}</span><div><small>{E(i["category"])}</small><h3>{E(i["title"])}</h3></div><span aria-hidden="true">→</span></a>' for i in issues)
    archive_text = replace_block(archive.read_text(encoding="utf-8"),"FEATURE",feature(issues[0],False))
    archive_text = replace_block(archive_text,"ARCHIVE",rows)
    outputs = {home:replace_block(home.read_text(encoding="utf-8"),"HOME",feature(issues[0],True)),archive:archive_text}
    for issue in issues:
        outputs[ROOT/"blog"/issue["slug"]/"index.html"] = article_html(issue)
    feed = rss(issues)
    for path,content in outputs.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(content,encoding="utf-8")
    (ROOT/"feed.xml").write_bytes(feed)
    print(f"Published {len(issues)} Fieldnotes issue(s); latest: {issues[0]['month']}.")

if __name__ == "__main__":
    main()
