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

COMMONS = "https://commons.wikimedia.org/wiki/File:"

# Banner art for each abstract page: slug -> (vertical focal point of the
# crop, credit).  Images live in site/images/abstracts/<slug>.jpg; a slug
# missing here falls back to good-government.jpg.
BANNERS = {
    "intro": ("40%", 'Jacques-Louis David, <em>The Death of Socrates</em>, 1787, '
              'Metropolitan Museum of Art, New York.',
              "Jacques-Louis_David_-_The_Death_of_Socrates_-_Google_Art_Project.jpg"),
    "callahan": ("35%", 'Ford Madox Brown, <em>Work</em>, 1863, Birmingham '
                 'Museum and Art Gallery.',
                 "Ford_Madox_Brown_-_Work_-_Google_Art_Project.jpg"),
    "pupo": ("35%", 'Vittore Carpaccio, <em>The Vision of St Augustine</em>, '
             '1502, Scuola di San Giorgio degli Schiavoni, Venice.',
             "Vittore_Carpaccio_026.jpg"),
    "karakasis": ("75%", 'Peter Paul Rubens and Frans Snyders, <em>Prometheus '
                  'Bound</em>, c. 1610&ndash;18, Philadelphia Museum of Art.',
                  "Peter_Paul_Rubens,_Flemish_(active_Italy,_Antwerp,_and_"
                  "England)_-_Prometheus_Bound_-_Google_Art_Project.jpg"),
    "green": ("50%", 'Leo von Klenze, <em>The Acropolis at Athens</em>, 1846, '
              'Neue Pinakothek, Munich.',
              "Akropolis_by_Leo_von_Klenze.jpg"),
    "coats": ("42%", 'Diego Vel&aacute;zquez, <em>The Surrender of Breda</em>, '
              'c. 1635, Museo del Prado, Madrid.',
              "Velazquez-The_Surrender_of_Breda.jpg"),
    "craig": ("55%", 'Gerard ter Borch, <em>The Ratification of the Treaty of '
              'M&uuml;nster</em>, 1648, National Gallery, London.',
              "Westfaelischer_Friede_in_Muenster_(Gerard_Terborch_1648).jpg"),
    "ferrell": ("42%", 'Gustave Dor&eacute;, <em>The Empyrean</em>, illustration '
                'to Dante&rsquo;s <em>Paradiso</em>, Canto 31, 1868.',
                "Paradiso_Canto_31_(no_caption).jpg"),
    "komolafe": ("50%", 'George Caleb Bingham, <em>The County Election</em>, '
                 '1851&ndash;52, Saint Louis Art Museum.',
                 "George_Caleb_Bingham_-_The_County_Election_-_44-2001_-_"
                 "Saint_Louis_Art_Museum.jpg"),
    "chimphambano": ("55%", 'Anicet-Charles-Gabriel Lemonnier, <em>In the Salon '
                     'of Madame Geoffrin in 1755</em>, 1812, '
                     'Ch&acirc;teau de Malmaison.',
                     "Anicet-Charles-Gabriel_Lemonnier_-_In_the_Salon_of_"
                     "Madame_Geoffrin_in_1755_-_WGA12652.jpg"),
    "dharamsi": ("45%", 'Luke Fildes, <em>The Doctor</em>, 1891, Tate, London.',
                 "The_Doctor_Luke_Fildes_crop.jpg"),
    "vallier": ("50%", 'Pieter Bruegel the Elder, <em>Netherlandish '
                'Proverbs</em>, 1559, Gem&auml;ldegalerie, Berlin.',
                "Pieter_Brueghel_the_Elder_-_The_Dutch_Proverbs_-_"
                "Google_Art_Project.jpg"),
    "carroll": ("35%", 'Jean Leon Gerome Ferris, <em>The Mayflower Compact, '
                '1620</em>, private collection; reproduction from the '
                'Library of Congress.',
                "The_Mayflower_Compact_1620_cph.3g07155.jpg"),
    "okwenna": ("46%", 'Rembrandt van Rijn, <em>The Night Watch</em>, 1642, '
                'Rijksmuseum, Amsterdam.',
                "The_Nightwatch_by_Rembrandt_-_Rijksmuseum.jpg"),
    "moschella": ("42%", 'Benozzo Gozzoli, <em>The Triumph of St Thomas '
                  'Aquinas</em> (detail), c. 1470&ndash;75, Mus&eacute;e du '
                  'Louvre, Paris.',
                  "Benozzo_Gozzoli_005.jpg"),
    "klein": ("60%", 'Alexander Nasmyth, <em>Princes Street with the '
              'Commencement of the Building of the Royal Institution</em>, '
              '1825, National Galleries of Scotland, Edinburgh.',
              "Alexander_Nasmyth_-_Princes_Street_with_the_Commencement_of_"
              "the_Building_of_the_Royal_Institution_-_Google_Art_Project.jpg"),
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


def abstract_path(slug: str) -> Path:
    """The introduction's abstract is intro.md at the top of the repo."""
    return TOP / "intro.md" if slug == "intro" \
        else TOP / "abstracts" / f"{slug}.md"


def abstract_body(slug: str) -> str:
    """The abstract without its header: paragraph 1 is the title and
    paragraph 2 the author block (which may hold an email address).
    intro.md has a title but no author block."""
    skip = 1 if slug == "intro" else 2
    return "\n\n".join(paragraphs(abstract_path(slug)
                                  .read_text(encoding="utf-8"))[skip:])


def banner(slug: str) -> tuple:
    """The banner div for an abstract page and its footer credit."""
    if slug not in BANNERS:
        return '<div class="banner"></div>', CREDITS["good-government.jpg"]
    focus, credit, commons = BANNERS[slug]
    div = (f'<div class="banner" style="background-image: url(\'../images/'
           f'abstracts/{slug}.jpg\'); background-position: center {focus};">'
           f'</div>')
    return div, (f'{credit} <a href="{COMMONS}{commons}">Public domain, via '
                 f'Wikimedia Commons</a>.')


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
        has_abstract = abstract_path(slug).exists()
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
    art, credit = banner(e["slug"])
    body = f"""{art}
<main class="paper">
<p class="kicker">Chapter {e["num"]} &middot; Abstract</p>
<h1>{inline(e["title"])}</h1>
<p class="byline">{author_links(e["authors"], "../")}{affil}</p>
<div class="text">
{md_to_html(abstract_body(e["slug"]))}
</div>
{chr(10).join(nav)}
</main>"""
    plain = re.sub(r"\*", "", e["title"])
    return page(f"{html.escape(plain)} · {SITE_TITLE}", body, "../",
                "abstract", credit)


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
