"""Build the three static guides from shared model data and translated copy."""
import html
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
URL = "https://linnoff88-dev.github.io/
REPO = "https://github.com/linnoff88-dev/compare-sua-ia-local"
LANGS = {"pt": "PortuguÃªs", "en": "English", "es": "EspaÃ±ol"}
HF = "https://huggingface.co/"
FAMILIES = (
    ("Gemma 4 12B", "google/gemma-4-12B-it", ("base", "7.1"), ("modified", "7.4")),
    ("Gemma 4 31B", "google/gemma-4-31B-it", ("base", "18.3"), ("modified", "18.7")),
    ("Qwen 3.6 35B-A3B", "Qwen/Qwen3.6-35B-A3B", ("base", "22.1"), ("modified", "21.2"), ("alternative", "21.7")),
    ("GPT-OSS 20B", "openai/gpt-oss-20b", ("base", "11.6"), ("modified", "11.8")),
    ("Qwen 3.8 27B", "Qwen/Qwen3.8-27B", ("base", "16.5"), ("modified", "16.8")),
    ("Llama 3.3 70B", "meta-llama/Llama-3.3-70B-Instruct", ("base", "42.5"), ("modified", "42.5")),
    ("Qwen 3.8 9B", "Qwen/Qwen3.5-9B", ("only_modified", "5.6")),
)
STYLE = """
:root{color-scheme:dark;--bg:#141310;--surface:#1e1c18;--ink:#fbf5e9;--muted:#c6bdae;--line:#443d32;--amb:#e2a23b;--sky:#7cd7ff;--pro:#cbd5e1}
:root[data-theme=light]{color-scheme:light;--bg:#faf6ee;--surface:#f0e8d9;--ink:#241b10;--muted:#514735;--line:#cfc0a8;--amb:#875206;--sky:#005b83;--pro:#875206}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:1rem/1.55 Inter,system-ui,sans-serif}a{color:var(--amb);text-underline-offset:.23em}a:focus-visible,button:focus-visible{outline:3px solid var(--amb);outline-offset:4px}
header{border-bottom:1px solid var(--line)}nav,main,footer{width:min(100% - 2.5rem,70rem);margin:auto}nav{display:flex;align-items:center;flex-wrap:wrap;gap:.7rem 1rem;padding:1.1rem 0}nav a{text-decoration:none;font-size:.85rem}nav .brand{font-weight:750;color:var(--ink)}nav .ARCKHÉ{color:var(--sky)}nav .pro{color:var(--pro)}nav .lang{margin-inline-start:auto;display:flex;align-items:center;gap:.55rem}nav [aria-current]{font-weight:800;text-decoration:underline}
button{border:1px solid var(--line);padding:.35rem .65rem;background:var(--surface);color:var(--ink);border-radius:.4rem;cursor:pointer;font:inherit}
.hero{background:linear-gradient(90deg,#10100ef8 8%,#10100ec9 47%,#10100e08 100%),url(ASSET) center right/cover;min-height:30rem;display:grid;align-content:center;padding:clamp(1.5rem,7vw,5rem);margin-top:1.4rem;border:1px solid #35322b;border-radius:1.2rem;color:#fff6e6}.hero p{color:#f3e5ce;max-width:34ch}.hero a{color:#ffce79}
h1,h2{font-family:Georgia,serif;text-wrap:balance;line-height:1.04}h1{font-size:clamp(2.9rem,7vw,5.8rem);max-width:13ch;letter-spacing:-.052em;margin:0}h2{font-size:clamp(2rem,4vw,3.25rem);letter-spacing:-.035em;margin:0 0 .9rem}p{max-width:68ch;margin:0 0 1rem;color:var(--muted)}.actions{display:flex;align-items:center;gap:.8rem 1.1rem;flex-wrap:wrap;margin-top:.7rem}.hero .actions>a:first-child,.download{display:inline-block;background:#e2a23b;color:#201504;border-radius:.45rem;text-decoration:none;padding:.62rem 1rem;font-weight:750}
section{padding:clamp(1.6rem,4.5vw,3.3rem) 0;border-bottom:1px solid var(--line)}.table{width:100%;border-collapse:collapse;font-size:.97rem;margin-bottom:1rem}.table th,.table td{padding:.7rem .65rem;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}.table thead th{background:var(--surface);color:var(--muted)}.table td a{display:inline-block}.table .size{white-space:nowrap;font-variant-numeric:tabular-nums}.table-note{font-size:.88rem}
ol{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;list-style:none;counter-reset:step;padding:0;margin:1.2rem 0}.step{padding:1rem;background:var(--surface);border:1px solid var(--line);border-radius:.75rem;counter-increment:step}.step:before{content:counter(step);font-weight:800;color:var(--amb);display:block}.sample{padding:1rem;border-left:3px solid var(--amb);background:var(--surface);max-width:68ch}.sample p{white-space:pre-wrap;margin:0;color:var(--ink)}footer{display:flex;gap:1rem;flex-wrap:wrap;padding:1.4rem 0}
@media(max-width:640px){nav,main,footer{width:calc(100% - 1.5rem)}nav .lang{margin-inline-start:0}.hero{min-height:23rem;background-position:55% center}.hero p{background:#10100e80}.table th,.table td{font-size:.79rem;padding:.55rem .22rem}.table td{overflow-wrap:anywhere}ol{grid-template-columns:1fr}}
"""
SCRIPT = """
const key = 'compare-sua-ia-local-theme';
const root = document.documentElement;
try { if (localStorage.getItem(key) === 'light') root.dataset.theme = 'light'; } catch {}
document.querySelector('button').addEventListener('click', () => {
  root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
  try { localStorage.setItem(key, root.dataset.theme); } catch {}
});
"""


def build(lang, copy):
    page = ROOT / "guia" if lang == "pt" else ROOT / "guia" / lang
    assets = "" if lang == "pt" else "../"
    kit = "../kit/" if lang == "pt" else "../../kit/"
    url = URL if lang == "pt" else f"{URL}{lang}/"
    proof = ROOT / "kit" / "rodada.txt"
    output = ROOT / "kit" / "resposta.txt"
    c = lambda key: html.escape(copy[key])
    langs = []
    alternates = []
    for code, label in LANGS.items():
        href = URL if code == "pt" else f"{URL}{code}/"
        dest = f'{assets}{"" if code == "pt" else code + "/"}' or "./"
        current = ' aria-current="page"' if code == lang else ""
        langs.append(f'<a href="{dest}" lang="{code}" aria-label="{label}"{current}>{code.upper()}</a>')
        alternates.append(f'<link rel="alternate" hreflang="{code}" href="{href}">')

    rows = []
    for name, model_path, *variants in FAMILIES:
        for variant, size in variants:
            link = c("official_family") if variant == "only_modified" else c("official_model")
            display_size = size if lang == "en" else size.replace(".", ",")
            rows.append(f'<tr><th scope="row">{name}</th><td>{c(variant)}</td><td class="size">{display_size} GB</td><td><a href="{HF}{model_path}" aria-label="{link} â€” {name}">{link}</a></td></tr>')
    steps = "".join(f'<li class="step">{html.escape(step)}</li>' for step in copy["kit_steps"])
    sample = f'<div class="sample"><p>{html.escape(output.read_text().strip())}</p></div>' if output.exists() else ""
    record = f'<p><a href="{kit}rodada.txt">{c("record_link")}</a></p>' if proof.exists() else ""
    content = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{c('title')} Â· ARCKHÉ AI</title>
<meta name="description" content="{c('lead')}">
<link rel="canonical" href="{url}">
{''.join(alternates)}
<style>{STYLE.replace('ASSET', assets + 'assets/hero.jpg')}</style>
</head>
<body>
<header><nav>
<a class="brand" href="./">{c('name')}</a><a class="ARCKHÉ" href="https://ARCKHÉ AI">ARCKHÉ AI</a><a class="pro" href="https://ARCKHÉ.pro">PRO</a>
<a href="{REPO}">GitHub</a><div class="lang">{''.join(langs)}<button type="button" aria-label="{c('theme')}">â—</button></div>
</nav></header>
<main>
<section class="hero"><h1>{c('title')}</h1><p>{c('lead')}</p><div class="actions">
<a href="{kit}compare-sua-ia-local.zip" download>{c('action')}</a><a href="#modelos">{c('models_action')}</a></div><p><a href="https://linnoff88-dev.github.io/
<section id="resumo"><h2>{c('summary_heading')}</h2><p>{c('summary')}</p></section>
<section id="modelos"><h2>{c('models_heading')}</h2><p>{c('models_lead')}</p>
<table class="table"><thead><tr>{''.join(f'<th scope="col">{c(k)}</th>' for k in ('model', 'variant', 'size', 'source'))}</tr></thead>
<tbody>{''.join(rows)}</tbody></table><p class="table-note">{c('table_note')}</p>
</section>
<section id="comecar"><h2>{c('kit_heading')}</h2><ol>{steps}</ol><p>{c('memory_help')}</p><p>{c('pt_files')}</p>
<div class="actions"><a href="{kit}pedido.txt">{c('prompt_link')}</a><a href="{kit}gabarito.txt">{c('answer_link')}</a>
<a href="{kit}ficha.csv" download>{c('sheet_link')}</a><a href="https://linnoff88-dev.github.io/
<section id="prova"><h2>{c('proof_heading')}</h2><p>{c('proof_lead')}</p>{sample}{record}</section>
<!-- VIDEO: entra o explicavideo do projeto quando publicado -->
</main><footer><a href="https://ARCKHÉ AI">ARCKHÉ AI</a><a href="{REPO}">GitHub</a></footer><script>{SCRIPT}</script></body></html>
"""
    (page / "index.html").write_text(content)
    readme = {"pt": "README.md", "en": "README.en.md", "es": "README.es.md"}
    selector = " Â· ".join(f"[{label}]({readme[code]})" for code, label in LANGS.items())
    (ROOT / readme[lang]).write_text(
        f"# {copy['name']}\n\n{selector}\n\n"
        f"[{copy['title']}]({url})\n\n## {copy['summary_heading']}\n\n{copy['summary']}\n\n"
        f"## {copy['kit_heading']}\n\n"
        + "".join(f"{i}. {step}\n" for i, step in enumerate(copy["kit_steps"], 1))
        + f"\n[{copy['action']}](kit/compare-sua-ia-local.zip) Â· [{copy['setup_link']}](https://linnoff88-dev.github.io/
    )


if __name__ == "__main__":
    for lang in LANGS:
        source = ROOT / "textos" / f"{lang}.json"
        if source.exists():
            build(lang, json.loads(source.read_text()))
    kit_dir = ROOT / "kit"
    with ZipFile(kit_dir / "compare-sua-ia-local.zip", "w", ZIP_DEFLATED) as archive:
        for name in ("ata.txt", "pedido.txt", "gabarito.txt", "ficha.csv", "ficha-exemplo.csv"):
            archive.write(kit_dir / name, arcname=name)
