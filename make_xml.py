#!/usr/bin/env python3
import sys
import datetime
import argparse
from jinja2 import Template
import os
from test_trans import test_trans

template = r"""
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE supplementalData SYSTEM "../../common/dtd/ldmlSupplemental.dtd">
<!-- Copyright © 1991-{{year}} Unicode, Inc.
CLDR data files are interpreted according to the LDML specification (http://unicode.org/reports/tr35/)
For terms of use, see http://www.unicode.org/copyright.html -->
<supplementalData>
	<version number="" />
	<transforms>
		<transform source="{{lang_code}}" target="{{lang_code}}_FONIPA" direction="forward" draft="contributed" alias="{{bcp47}}">
			<tRule><![CDATA[
{{rbt_rules}}
            ]]></tRule>
        </transform>
    </transforms>
</supplementalData>
"""
def alias_fix(lang_code):
    return lang_code.replace("_", "-").lower()

def bare_lang_code(lang_code):
    return lang_code.split("_")[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("rulefile")
    parser.add_argument("lang_code")
    parser.add_argument("uid")
    parser.add_argument("-i", "--include", default=r"")
    parser.add_argument("-e", "--exclude", default=r"^$")
    args = parser.parse_args()
    uid = args.uid
    lang_code = args.lang_code
    directory = "output/" + lang_code + "/"
    os.makedirs(directory, exist_ok=True)
    xml_filename = directory + "{0}-{0}_FONIPA.xml".format(lang_code)
    rbt_rules = open(args.rulefile).read()
    bcp47 = "{}-fonipa-t-{}".format(bare_lang_code(lang_code), alias_fix(lang_code))
    test_trans(sys.argv[1], uid, directory + bcp47 + ".txt", include=args.include, exclude=args.exclude)
    with open(xml_filename, "w") as file:
        t = Template(template)
        t.globals["alias_fix"] = alias_fix
        t.globals["bare_lang_code"] = bare_lang_code
        file.write(t.render(year=datetime.datetime.now().year, lang_code=lang_code, rbt_rules=rbt_rules, bcp47=bcp47))
