#!/usr/bin/env python3
"""Generate 30 industry PSEO pages for llmo-check.de"""
import json, os, glob

TEMPLATE_PATH = "template.html"
OUTPUT_DIR = "branchen"
DATA_DIR = "data"

def make_analysis_card(title, desc):
    return f'''<div class="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:border-violet-200 hover:shadow-md transition">
    <div class="w-12 h-12 bg-violet-100 rounded-xl flex items-center justify-center mb-5">
        <svg class="w-6 h-6 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
    </div>
    <h3 class="text-xl font-bold mb-3 text-gray-900">{title}</h3>
    <p class="text-gray-600 leading-relaxed">{desc}</p>
</div>'''

def make_prompt_item(prompt):
    return f'''<div class="bg-violet-50 border border-violet-200 rounded-xl px-6 py-4">
    <p class="text-violet-900 font-medium">💬 „{prompt}"</p>
</div>'''

def make_faq_item(q, a, is_open=False):
    op = " open" if is_open else ""
    return f'''<details class="bg-white rounded-xl border border-gray-200 group"{op}>
    <summary class="px-6 py-5 cursor-pointer font-semibold text-gray-900 flex justify-between items-center">
        {q}
        <svg class="w-5 h-5 text-violet-500 transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
    </summary>
    <div class="px-6 pb-5 text-gray-600 leading-relaxed">{a}</div>
</details>'''

def make_faq_jsonld(faqs):
    entities = []
    for q, a in faqs:
        entities.append(f'{{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}')
    return f'{{"@type":"FAQPage","mainEntity":[{",".join(entities)}]}}'

def make_related_links(all_industries, current_slug):
    links = []
    for ind in all_industries:
        if ind["slug"] == current_slug:
            continue
        links.append(f'<a href="/branchen/{ind["slug"]}.html" class="bg-violet-100 text-violet-800 text-sm font-semibold px-4 py-2 rounded-full border border-violet-200 hover:bg-violet-200 transition">{ind["name"]}</a>')
    return "\n".join(links)

def generate_page(ind, all_industries, template):
    cards = "\n".join(make_analysis_card(t, d) for t, d in ind["analysis"])
    prompts = "\n".join(make_prompt_item(p) for p in ind["prompts"])
    faq_html = "\n".join(make_faq_item(q, a, i == 0) for i, (q, a) in enumerate(ind["faq"]))
    faq_jsonld = make_faq_jsonld(ind["faq"])
    related = make_related_links(all_industries, ind["slug"])
    problem_html = "\n".join(f"<p>{p}</p>" for p in ind["problem_paragraphs"])
    actions_html = "\n".join(f"<p>{p}</p>" for p in ind["action_paragraphs"])

    replacements = {
        "{{TITLE}}": ind["title"],
        "{{META_DESCRIPTION}}": ind["meta_description"],
        "{{KEYWORDS}}": ind["keywords"],
        "{{SLUG}}": ind["slug"],
        "{{NAME}}": ind["name"],
        "{{H1}}": ind["h1"],
        "{{HERO_TEXT}}": ind["hero_text"],
        "{{PROBLEM_H2}}": ind["problem_h2"],
        "{{PROBLEM_CONTENT}}": problem_html,
        "{{ANALYSIS_H2}}": ind["analysis_h2"],
        "{{ANALYSIS_INTRO}}": ind["analysis_intro"],
        "{{ANALYSIS_CARDS}}": cards,
        "{{PROMPTS_H2}}": ind["prompts_h2"],
        "{{PROMPTS_INTRO}}": ind["prompts_intro"],
        "{{PROMPT_ITEMS}}": prompts,
        "{{ACTIONS_H2}}": ind["actions_h2"],
        "{{ACTIONS_CONTENT}}": actions_html,
        "{{FAQ_JSONLD}}": faq_jsonld,
        "{{FAQ_ITEMS}}": faq_html,
        "{{RELATED_LINKS}}": related,
    }
    html = template
    for k, v in replacements.items():
        html = html.replace(k, v)
    return html

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(TEMPLATE_PATH, "r") as f:
        template = f.read()

    all_industries = []
    for fp in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
        with open(fp, "r") as f:
            all_industries.extend(json.load(f))

    print(f"Loaded {len(all_industries)} industries")

    for ind in all_industries:
        html = generate_page(ind, all_industries, template)
        out_path = os.path.join(OUTPUT_DIR, f'{ind["slug"]}.html')
        with open(out_path, "w") as f:
            f.write(html)
        print(f"  ✓ {out_path}")

    # Generate sitemap
    urls = ['  <url>\n    <loc>https://llmo-check.de/</loc>\n    <priority>1.0</priority>\n    <changefreq>weekly</changefreq>\n  </url>']
    for ind in all_industries:
        urls.append(f'  <url>\n    <loc>https://llmo-check.de/branchen/{ind["slug"]}.html</loc>\n    <priority>0.8</priority>\n    <changefreq>monthly</changefreq>\n  </url>')
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>"
    with open("sitemap.xml", "w") as f:
        f.write(sitemap)
    print("  ✓ sitemap.xml")

    with open("robots.txt", "w") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: https://llmo-check.de/sitemap.xml\n")
    print("  ✓ robots.txt")

    print(f"\nDone! Generated {len(all_industries)} pages + sitemap + robots.txt")

if __name__ == "__main__":
    main()
