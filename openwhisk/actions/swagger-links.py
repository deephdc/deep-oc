import json


def main(args):
    modules = args["json"]
    ret = []
    for m in modules:
        ret.append(
            '<li>'
            '<a href="/swagger/index.html?url={}/swagger.json" target="_blank">'
            'Swagger UI for "{}"'
            '</a>'
#            ' | '
#            '<a href="https://marketplace.deep-hybrid-datacloud.eu/modules/{}.html" target="_blank">'
#            'Marketplace entry'
#            '</a>'
            '</li>'.format(m["href"], m["name"], m["name"])
        )
    ret.insert(0, "<ul>")
    ret.append("</ul>")

    return {
        "text": "\n".join(ret),
    }
