#!/usr/bin/env python3

"""
this builds the homepage for https://kevbot.xyz
"""


import os
import requests
from io import StringIO
import csv


def alphanumeric_only(s: str) -> str:
    return "".join([c for c in s if c.isalnum() or c in " .-,()"])

# make dump generated file here
# content dir is one directory up
CONTENTS_LR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content", "contents.lr")
IMAGE_404 = "https://cdn.kevbot.xyz/file/kevbot-cdn/screenshots/404.png"
CSV_DL_PATH = "https://docs.google.com/spreadsheets/d/1MVghM465zjbMGB89CwvH-GwfwyLXqHqfY1emM7Mp-uA/export?format=csv"
TEMPLATE = """
title: Kevin's Homepage
---
body:
## [back to my visual portfolio here](https://kevinleutzinger.com)

This is all the projects I've made in condensed view ordered by recency.  
New stuff pops up at the top periodically.  
Hover over an info icon for more details, click a screenshot for a better view.  

MARKDOWN
---
alt_note: alt note
"""

"""
| Syntax | Description |
| --- | ----------- |
| Header | Title |
| Paragraph | Text |
"""


def get_projects() -> list:
    resp = requests.get(CSV_DL_PATH)
    scsv = resp.text

    f = StringIO(scsv)
    reader = csv.reader(f, delimiter=",")
    # convert csv to list of dicts
    headers = next(reader)
    rows = []
    for row in reader:
        row_dict = {}
        for i, header in enumerate(headers):
            if row[i]:
                row_dict[header] = row[i]
        rows.append(row_dict)
    return rows


def main():
    global TEMPLATE
    # get json from endpoint
    projects = get_projects()
    projects.sort(reverse=True, key=lambda x: x.get("date_created", "0"))
    used_fields = ["date_created", "title/link", "info","screenshot_url", "source code"]
    piped = "|".join(["<!-- -->" for _ in used_fields])
    headers = f"|{piped}|"
    spacer = f"|{'---|'*len(used_fields)}"
    output_string = f"{headers}\n{spacer}\n"

    def modify_project(project):
        title = project.get("title", "title")
        title_link = None
        if "demo_url" in project:
            title_link = project["demo_url"]
        if "repo_url" in project:
            project["source code"] = f"[source_code]({project['repo_url']})"
            title_link = title_link or project["repo_url"]
        if "readme_url" in project:
            title_link = title_link or project["readme_url"]
        if "star_rating" in project:
            full_star = "★"
            star_rating = project["star_rating"]
            project["stars"] = full_star * int(float(star_rating))
        if "web_description" in project:
            project["info"] = project["web_description"]
        title_link = title_link or "#"
        project["title/link"] = f"[{title}]({title_link})"

        return project

    for project in map(modify_project, projects):
        if "kb" in project.get("omit_from", []):
            continue
        piped = ""
        for field in used_fields:
            val = project.get(field, "")
            if field == "screenshot_url":
                if val:
                    val = f'<a href="{val}"><img class=small_img src="{val}"></img></a>'
                else:
                    val = f'<img class=small_img src="{IMAGE_404}">'
            elif field == "info":
                if val:
                    # show a circled info i with alt text with the val
                    val = f'<span class="info" title="{alphanumeric_only(val)}">🛈</span>'
                else:
                    val = ""
            piped += f"{val}|"
        vals = f"|{piped}|\n"
        output_string += vals

    markdown_output = TEMPLATE.replace("MARKDOWN", output_string)
    with open(CONTENTS_LR, "w") as f:
        f.write(markdown_output)
    print(f"wrote to {len(markdown_output)} bytes to {CONTENTS_LR}")


if __name__ == "__main__":
    main()
