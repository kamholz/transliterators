#!/usr/bin/env python3
import sys
import os
import argparse
from hashlib import md5
import icu
import panlex
import regex as re
from jinja2 import Template

template = r"""
<html>
    <head>
        <meta charset="utf-8"/>
        <style>
            .row {
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                border-block-end: 1px black solid;
                font-size: larger;
            }
        </style>
    </head>
    <body style="display: flex; justify-content: center">
        <div style="max-inline-size: 640px; min-inline-size: 360px;">
            {% for expr, result in test_results %}
            <div class="row">
                <div>
                {%- for c in expr -%}
                    <span style="color: {{get_color(c)}}">{{c}}</span>
                {%- endfor -%}
                </div>
                <div>
                {%- for c in result -%}
                    <span style="color: {{get_color(c)}}">{{c}}</span>
                {%- endfor -%}
                </div>
            </div>
            {% endfor %}
        </div>
    </body>
</html>
"""

color_dict = {
    "Zyyy": "black",
    "Zinh": "gray",
    "Latn": "navy",
    "Cyrl": "maroon",
    "Geor": "purple",
    "Grek": "green",
    "Armn": "olive",
}

def getexprs(uid, include=r"", exclude=r"^$"):
    r = panlex.query("/expr", {"uid": uid, "include": "expr_score", "sort": "expr_score desc"})
    return [ex["txt"] for ex in r["result"] if re.search(include, ex["txt"]) and not re.search(exclude, ex["txt"])]

def make_trans(rulefile):
    trans_name = os.path.splitext(os.path.basename(rulefile))[0]
    return icu.Transliterator.createFromRules(trans_name, open(rulefile).read(), icu.UTransDirection.FORWARD)

def gen_webpage(test_results):
    t = Template(template)
    t.globals['get_color'] = get_color
    return t.render(test_results=test_results)

def get_script(char):
    return icu.Script.getScript(char).getShortName()

def get_color(char):
    script = get_script(char)
    try:
        return color_dict[script]
    except KeyError:
        return md5(script.encode("UTF-8")).hexdigest()[-6:]

def test_trans(rulefile, uid, result_filename, with_html=False, include=r"", exclude=r"^$"):
    os.makedirs("tests/results/html", exist_ok=True)
    try:
        exprs = open("tests/" + uid + ".txt").read().split("\n")
    except FileNotFoundError:
        exprs = getexprs(uid, include=include, exclude=exclude)
        with open("tests/" + uid + ".txt", "w") as file:
            for expr in exprs:
                file.write(expr + "\n")
    t = make_trans(rulefile)
    test_results = [(expr, t.transliterate(expr)) for expr in exprs]
    with open(result_filename, "w") as file:
        for ex_r in test_results:
            file.write("\t".join(ex_r) + "\n")
    if with_html:
        with open("tests/results/html/" + os.path.basename(result_filename) + ".html", "w") as file:
            file.write(gen_webpage(test_results))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("rulefile")
    parser.add_argument("uid")
    parser.add_argument("-i", "--include", default=r"")
    parser.add_argument("-e", "--exclude", default=r"^$")
    args = parser.parse_args()
    uid = args.uid
    rulefile = args.rulefile
    os.makedirs("tests/results/html", exist_ok=True)
    result_filename = "tests/results/" + os.path.basename(rulefile) + ".result"
    test_trans(rulefile, uid, result_filename, with_html=True, include=args.include, exclude=args.exclude)
