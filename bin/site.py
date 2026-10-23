#!/usr/bin/env python3
"""
Build the GitHub Pages site for the book into docs/.

Only the table of contents (toc.md), the abstracts (abstracts/*.md) and
the bios (bios/*.md) are published; nothing else in the repo is copied.
Chapter order comes from order.txt, which must match the entries in toc.md.

Usage: bin/site.py          (then commit docs/ and push)
Needs pandoc on the PATH.
"""

import html
import re
import shutil
import subprocess
from pathlib import Path

TOP = Path(__file__).resolve().parent.parent
OUT = TOP / "docs"
ASSETS = TOP / "site"

SITE_TITLE = "Justifying the State"
EDITORS = ["callahan", "komolafe"]

CREDITS = {
    "leviathan.jpg": 'Abraham Bosse, frontispiece to Hobbes\'s <em>Leviathan</em>, '
                     '1651. <a href="https://commons.wikimedia.org/wiki/'
                     'File:Leviathan_frontispiece_cropped_British_Library.jpg">'
                     'British Library, public domain, via Wikimedia Commons</a>.',
    "good-government.jpg": 'Ambrogio Lorenzetti, <em>Allegory of Good Government</em>, '
                           '1338&ndash;39, Palazzo Pubblico, Siena. '
                           '<a href="https://commons.wikimedia.org/wiki/'
                           'File:Ambrogio_Lorenzetti_-_Allegory_of_Good_Government_-'
                           '_Google_Art_Project.jpg">Public domain, via Wikimedia '
                           'Commons</a>.',
    "good-city.jpg": 'Ambrogio Lorenzetti, <em>Effects of Good Government in the '
                     'City</em>, 1338&ndash;39, Palazzo Pubblico, Siena. '
                     '<a href="https://commons.wikimedia.org/wiki/'
                     'File:Ambrogio_Lorenzetti_-_Effects_of_Good_Government_in_the_city_-'
                     '_Google_Art_Project.jpg">Public domain, via Wikimedia Commons</a>.',
}

FONTS = ("https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700"
         "&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500"
         "&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap")


def md_to_html(text: str) -> str:
    return subprocess.run(["pandoc", "-f", "markdown", "-t", "html5",
                           "--wrap=none"],
                          input=text, capture_output=True, text=True,
                          check=True).stdout


def inline(text: str) -> str:
    """Escape a one-line string, keeping *emphasis*."""
    return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", html.escape(text.strip()))


def strip_rules(text: str) -> str:
    """Drop separator lines (==== or ****) the source files use."""
    return "\n".join(line for line in text.splitlines()
                     if not re.fullmatch(r"\s*[=*]{3,}\s*", line))


def paragraphs(text: str) -> list:
    return [p for p in re.split(r"\n\s*\n", strip_rules(text).strip()) if p.strip()]


def abstract_body(path: Path) -> str:
    """The abstract without its header: paragraph 1 is the title and
    paragraph 2 the author block (which may hold an email address)."""
    return "\n\n".join(paragraphs(path.read_text(encoding="utf-8"))[2:])


def slug_for(name: str) -> str:
    return name.split()[-1].lower()


def parse_toc():
    """Return the list of entries in toc.md."""
    lines = (TOP / "toc.md").read_text(encoding="utf-8").splitlines()
    raw = []
    for line in lines[lines.index("## Table of Contents") + 1:]:
        if re.match(r"\d+\. ", line):
            raw.append([line.split(". ", 1)[1].strip()])
        elif line.strip() and raw:
            raw[-1].append(line.strip())
    order = [l.strip() for l in (TOP / "order.txt").read_text().splitlines()
             if l.strip()]
    if len(order) != len(raw):
        raise SystemExit(f"order.txt has {len(order)} names but toc.md has "
                         f"{len(raw)} entries")
    known = {l.strip() for l in (TOP / "authors.txt").read_text().splitlines()
             if l.strip()}
    entries = []
    for num, (slug, parts) in enumerate(zip(order, raw), start=1):
        if len(parts) == 1:          # "Introduction, Gene Callahan and ..."
            title, byline = parts[0].split(", ", 1)
            affil = ""
        else:
            title = parts[0].rstrip(",")
            byline, _, affil = parts[1].partition(", ")
        authors = [(n.strip(), slug_for(n)) for n in byline.split(" and ")]
        for name, s in authors:
            if s not in known:
                raise SystemExit(f"toc.md author {name!r} not in authors.txt")
        has_abstract = (TOP / "abstracts" / f"{slug}.md").exists()
        if slug != "intro" and slug not in [s for _, s in authors]:
            raise SystemExit(f"order.txt {slug!r} doesn't match toc.md "
                             f"entry {num}: {byline}")
        entries.append(dict(num=num, slug=slug, title=title, authors=authors,
                            affil=affil, abstract=has_abstract))
    return entries


def page(title: str, body: str, root: str, kind: str, credit: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{SITE_TITLE}: an edited volume on recent justifications of state authority.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{root}style.css">
</head>
<body class="{kind}">
<header class="masthead">
<a class="book" href="{root}index.html">{SITE_TITLE}</a>
<span class="sub">Edited by Gene Callahan &amp; Leye Komolafe</span>
</header>
{body}
<footer>
<p><a href="{root}index.html">Contents</a></p>
<p class="credit">{credit}</p>
</footer>
</body>
</html>
"""


def author_links(authors, root: str) -> str:
    return " and ".join(f'<a href="{root}bios/{s}.html">{html.escape(n)}</a>'
                        for n, s in authors)


def build_index(entries) -> str:
    items = []
    for e in entries:
        title = inline(e["title"])
        if e["abstract"]:
            title = f'<a href="abstracts/{e["slug"]}.html">{title}</a>'
        affil = f'<span class="affil">{html.escape(e["affil"])}</span>' \
            if e["affil"] else ""
        items.append(f"""<li>
<span class="num">{e["num"]}</span>
<div><span class="title">{title}</span>
<span class="byline">{author_links(e["authors"], "")}{affil}</span></div>
</li>""")
    editors = "\n".join(f"""<a class="editor" href="bios/{s}.html">
<img src="images/{s}.jpg" alt="{n}">
<span class="name">{n}</span>
<span class="role">{r}</span>
</a>""" for s, n, r in [("callahan", "Gene Callahan", "New York University"),
                         ("komolafe", "Leye Komolafe",
                          "University of South Carolina")])
    body = f"""<section class="hero">
<div class="hero-text">
<p class="kicker">An edited volume in political philosophy</p>
<h1>{SITE_TITLE}</h1>
<p class="lede">Is there a duty to obey the state? Fifteen scholars
examine the most important modern attempts to justify state authority, from
Bosanquet, Gentile, Schmitt and Heidegger to Oakeshott, Rawls, Habermas, Raz,
Gaus and Finnis, along with challenges to the very question.</p>
<p class="cta"><a href="#contents">Table of contents &darr;</a></p>
</div>
<figure class="hero-art"><img src="images/leviathan.jpg"
alt="The frontispiece of Hobbes's Leviathan: a crowned giant, made of
many people, rising over the land with sword and crozier"></figure>
</section>
<section class="editors">
<h2>The Editors</h2>
<div class="editor-row">
{editors}
</div>
</section>
<main id="contents">
<h2>Contents</h2>
<ol class="toc">
{chr(10).join(items)}
</ol>
<p class="hint">Follow a chapter title to read its abstract, or a contributor's
name to read their biography.</p>
</main>"""
    return page(SITE_TITLE, body, "", "home", CREDITS["leviathan.jpg"])


def build_abstract(e, prev, nxt) -> str:
    nav = ['<nav class="chapnav">']
    nav.append(f'<a class="prev" href="{prev["slug"]}.html">&larr; '
               f'{inline(prev["title"])}</a>' if prev else "<span></span>")
    nav.append('<a class="contents" href="../index.html#contents">Contents</a>')
    nav.append(f'<a class="next" href="{nxt["slug"]}.html">'
               f'{inline(nxt["title"])} &rarr;</a>' if nxt else "<span></span>")
    nav.append("</nav>")
    affil = f'<span class="affil">{html.escape(e["affil"])}</span>' \
        if e["affil"] else ""
    body = f"""<div class="banner"></div>
<main class="paper">
<p class="kicker">Chapter {e["num"]} &middot; Abstract</p>
<h1>{inline(e["title"])}</h1>
<p class="byline">{author_links(e["authors"], "../")}{affil}</p>
<div class="text">
{md_to_html(abstract_body(TOP / "abstracts" / f"{e['slug']}.md"))}
</div>
{chr(10).join(nav)}
</main>"""
    plain = re.sub(r"\*", "", e["title"])
    return page(f"{html.escape(plain)} · {SITE_TITLE}", body, "../",
                "abstract", CREDITS["good-government.jpg"])


def build_bio(slug, name, affil, chapters) -> str:
    photo = f'<img class="portrait" src="../images/{slug}.jpg" alt="{name}">' \
        if slug in EDITORS else ""
    role = '<p class="kicker">Co-editor</p>' if slug in EDITORS \
        else '<p class="kicker">Contributor</p>'
    text = md_to_html(strip_rules((TOP / "bios" / f"{slug}.md")
                                  .read_text(encoding="utf-8")))
    links = []
    for e in chapters:
        t = inline(e["title"])
        if e["abstract"]:
            t = f'<a href="../abstracts/{e["slug"]}.html">{t}</a>'
        links.append(f'<li><span class="num">Chapter {e["num"]}</span> {t}</li>')
    body = f"""<div class="banner"></div>
<main class="paper">
{role}
<div class="bio-head">{photo}
<div><h1>{html.escape(name)}</h1>
{f'<p class="byline"><span class="affil">{html.escape(affil)}</span></p>' if affil else ""}
</div></div>
<div class="text">
{text}
</div>
<h2>In this volume</h2>
<ul class="chapters">
{chr(10).join(links)}
</ul>
</main>"""
    return page(f"{html.escape(name)} · {SITE_TITLE}", body, "../", "bio",
                CREDITS["good-city.jpg"])


def main():
    entries = parse_toc()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "abstracts").mkdir(parents=True)
    (OUT / "bios").mkdir()
    shutil.copytree(ASSETS / "images", OUT / "images")
    shutil.copy(ASSETS / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").touch()

    (OUT / "index.html").write_text(build_index(entries))

    chaps = [e for e in entries if e["abstract"]]
    for i, e in enumerate(chaps):
        prev = chaps[i - 1] if i > 0 else None
        nxt = chaps[i + 1] if i + 1 < len(chaps) else None
        (OUT / "abstracts" / f"{e['slug']}.html").write_text(
            build_abstract(e, prev, nxt))

    people = {}         # slug -> (name, affiliation, [entries])
    for e in entries:
        for name, slug in e["authors"]:
            n, a, chs = people.get(slug, (name, "", []))
            people[slug] = (n, a or e["affil"], chs + [e])
    for slug, (name, affil, chs) in people.items():
        (OUT / "bios" / f"{slug}.html").write_text(
            build_bio(slug, name, affil, chs))
    print(f"site: built {OUT} ({len(chaps)} abstracts, {len(people)} bios)")


if __name__ == "__main__":
    main()
