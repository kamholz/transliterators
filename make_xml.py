#!/usr/bin/env python3
import sys
from jinja2 import Template
import os
from test_trans import test_trans

template = r"""
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE supplementalData SYSTEM "../../common/dtd/ldmlSupplemental.dtd">
<!-- Copyright © 1991-2013 Unicode, Inc.
CLDR data files are interpreted according to the LDML specification (http://unicode.org/reports/tr35/)
For terms of use, see http://www.unicode.org/copyright.html -->
<supplementalData>
	<version number="" />
	<transforms>
		<transform source="{{lang_code}}" target="{{lang_code}}_FONIPA" direction="forward" draft="contributed" alias="{{bare_lang_code(lang_code)}}-fonipa-t-{{alias_fix(lang_code)}}">
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
    uid = sys.argv[3]
    lang_code = sys.argv[2]
    os.makedirs("output/" + lang_code, exist_ok=True)
    xml_filename = "output/{0}/{0}-{0}_FONIPA.xml".format(lang_code)
    rbt_rules = open(sys.argv[1]).read()
    test_trans(sys.argv[1], uid, xml_filename + ".tests")
    with open(xml_filename, "w") as file:
        t = Template(template)
        t.globals["alias_fix"] = alias_fix
        t.globals["bare_lang_code"] = bare_lang_code
        file.write(t.render(lang_code=lang_code, rbt_rules=rbt_rules))
