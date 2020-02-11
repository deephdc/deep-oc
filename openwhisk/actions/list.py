# -*- coding: utf-8 -*-

# Copyright 2020 Spanish National Research Council (CSIC)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import urllib.parse

import requests


def do(args):
    ow_host = os.environ.get("__OW_API_HOST")
    ow_namespace = os.environ.get("__OW_NAMESPACE")
    api_url = urllib.parse.urljoin(
        ow_host,
        "/api/v1/namespaces/%s/actions/" % ow_namespace
    )

    ow_auth = args["api_key"]

    api_auth = tuple(ow_auth.split(":"))

    try:
        resp = requests.get(api_url, auth=api_auth)
    except Exception as e:
        return {
            "error": "Could not connect to the API: %s" % e
        }

    actions = resp.json()

    actions_json = []
    actions_html = []

    web_url = "/api/v1/web"

    for action in actions:
        web = False
        for ann in action.get("annotations", []):
            if ann["key"] == "web-export" and ann["value"]:
                web = True
        if not web:
            continue

        action_name = action["name"]
        if action_name == "list_actions":
            continue

        aux = action["namespace"].split("/", maxsplit=1)
        action_namespace = aux.pop(0)
        if aux:
            action_package = aux.pop(0)
        else:
            action_package = "default"

        action_fragment = "{}/{}/{}/{}".format(web_url,
                                               action_namespace,
                                               action_package,
                                               action_name)
        action_url = urllib.parse.urljoin(ow_host,
                                          action_fragment)

        d = {
            "name": action_name,
            "href": action_url,
            "rel": "service"
        }
        actions_json.append(d)
        html = "<li><a href='{}' rel='service'>{}</a></li>".format(action_url,
                                                                   action_name)
        actions_html.append(html)

    actions_text = "\n".join(
        [
            "{}: {}".format(
                a["name"],
                a["href"]
            ) for a in actions_json
        ]
    )
    actions_html = "<html><body><ul>{}</ul></body></html>".format(
        "".join(actions_html)
    )
    return {
        "json": actions_json,
        "text": actions_text,
        "html": actions_html,
    }


def main(args):
    try:
        return do(args)
    except Exception as e:
        return {
            "error": "Error happened: %s" % e
        }
