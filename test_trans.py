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

def getexprs(uid, include=r"", exclude=r"^$", replace=[]):
    r = panlex.query("/expr", {"uid": uid, "include": "expr_score", "sort": "expr_score desc"})
    exprs = [ex["txt"] for ex in r["result"]]
    return exprs

def prep_exprs(exprs, include=r"", exclude=r"^$", replace=[]):
    output = [ex for ex in exprs if re.search(include, ex) and not re.search(exclude, ex)]
    if replace:
        for re_from, replacement in replace:
            output = [re.sub(re_from, replacement, ex) for ex in output]
    return output

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

def test_trans(rulefile, uid, result_filename, with_html=False, include=r"", exclude=r"^$", replace=[]):
    os.makedirs("tests/results/html", exist_ok=True)
    try:
        raw_exprs = open("tests/" + uid + ".txt").read().split("\n")
        exprs = prep_exprs(raw_exprs, include=include, exclude=exclude, replace=replace)
    except FileNotFoundError:
        raw_exprs = getexprs(uid)
        with open("tests/" + uid + ".txt", "w") as file:
            for expr in raw_exprs:
                file.write(expr + "\n")
        exprs = prep_exprs(raw_exprs, include=include, exclude=exclude, replace=replace)
    t = make_trans(rulefile)
    test_results = [(expr, t.transliterate(expr)) for expr in exprs]
    with open(result_filename, "w") as file:
        for ex_r in test_results:
            file.write("\t".join(ex_r) + "\n")
    if with_html:
        with open("tests/results/html/" + os.path.basename(result_filename) + ".html", "w") as file:
            file.write(gen_webpage(test_results))

def extract_replacements(replace_file):
    with open(replace_file) as file:
        lines = [line for line in file.readlines() if line.strip() and not line.startswith("#")]
        return [line.split("\t") for line in lines if line.split("\t")]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("rulefile")
    parser.add_argument("uid")
    parser.add_argument("-i", "--include")
    parser.add_argument("-e", "--exclude")
    parser.add_argument("-r", "--replace")
    args = parser.parse_args()
    rulefile = args.rulefile
    uid = args.uid
    if args.include:
        include = open(args.include).read().strip()
    else:
        try:
            include = open("test_data_fixes/{}_include".format(uid)).read().strip()
        except FileNotFoundError:
            include = r""
    if args.exclude:
        exclude = open(args.exclude).read().strip()
    else:
        try:
            exclude = open("test_data_fixes/{}_exclude".format(uid)).read().strip()
        except FileNotFoundError:
            exclude = r"^$"
    if args.replace:
        replace = extract_replacements(args.replace)
    else:
        try:
            replace = extract_replacements("test_data_fixes/{}_replace".format(uid))
        except FileNotFoundError:
            replace = []
    os.makedirs("tests/results/html", exist_ok=True)
    result_filename = "tests/results/" + os.path.basename(rulefile) + ".result"
    test_trans(rulefile, uid, result_filename, with_html=True, include=include, exclude=exclude, replace=replace)
