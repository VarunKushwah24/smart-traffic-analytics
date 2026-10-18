# -*- coding: utf-8 -*-
"""Converts docs/project_report_milestone_1.md to print-ready HTML with pagination."""
import os, sys, re

DOCS_DIR = os.path.dirname(__file__)
MD_FILE = os.path.join(DOCS_DIR, "project_report_milestone_1.md")
HTML_FILE = os.path.join(DOCS_DIR, "project_report_milestone_1.html")

def md_to_html():
    if not os.path.exists(MD_FILE):
        print(f"File not found: {MD_FILE}")
        return

    with open(MD_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # Simple Markdown to HTML formatter with academic styling
    html_body = []
    lines = text.split("\n")
    in_code_block = False
    in_table = False

    for line in lines:
        if line.strip() == "\\newpage":
            html_body.append('<div style="page-break-after: always;"></div>')
            continue

        if line.startswith("```"):
            if in_code_block:
                html_body.append("</pre>")
                in_code_block = False
            else:
                html_body.append("<pre class='ascii-box'>")
                in_code_block = True
            continue

        if in_code_block:
            html_body.append(line)
            continue

        if line.startswith("# "):
            html_body.append(f"<h1 class='title'>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_body.append(f"<h2 class='subtitle'>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_body.append(f"<h3 class='subheading'>{line[4:]}</h3>")
        elif line.startswith("#### "):
            html_body.append(f"<h4>{line[5:]}</h4>")
        elif line.startswith("* ") or line.startswith("- "):
            html_body.append(f"<li>{line[2:]}</li>")
        elif line.strip() == "---":
            html_body.append("<hr>")
        elif line.strip() == "":
            html_body.append("<br>")
        else:
            html_body.append(f"<p>{line}</p>")

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Milestone 1 Project Report - Varun Kushwah</title>
<style>
    @page {{
        size: A4;
        margin: 25mm 20mm 25mm 20mm;
    }}
    body {{
        font-family: 'Times New Roman', Times, serif;
        font-size: 12pt;
        line-height: 1.6;
        color: #111;
        margin: 40px auto;
        max-width: 850px;
        background: #fff;
    }}
    h1.title {{
        text-align: center;
        font-size: 20pt;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }}
    h2.subtitle {{
        font-size: 15pt;
        font-weight: bold;
        border-bottom: 2px solid #333;
        padding-bottom: 5px;
        margin-top: 40px;
    }}
    h3.subheading {{
        font-size: 13pt;
        font-weight: bold;
        margin-top: 25px;
        color: #222;
    }}
    p {{
        text-align: justify;
        text-justify: inter-word;
        margin-bottom: 12px;
    }}
    pre.ascii-box {{
        background: #f8f9fa;
        border: 1px solid #ccc;
        padding: 12px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 9.5pt;
        line-height: 1.3;
        overflow-x: auto;
        border-radius: 4px;
        margin: 15px 0;
    }}
    li {{
        margin-left: 20px;
        margin-bottom: 6px;
    }}
    hr {{
        border: none;
        border-top: 1px solid #ccc;
        margin: 30px 0;
    }}
</style>
</head>
<body>
{"".join(html_body)}
</body>
</html>"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Generated printable report at: {HTML_FILE}")

if __name__ == "__main__":
    md_to_html()
