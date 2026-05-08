import os
from html.parser import HTMLParser


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title, self.current_title = False, ""

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True

    def handle_data(self, data):
        if self.in_title:
            self.current_title += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False


parser = TitleParser()


def build_tree(path):
    tree = {
        "name": os.path.basename(path) or path,
        "path": path,
        "files": [],
        "dirs": [],
    }

    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        return None

    for item in items:
        full_path = os.path.join(path, item)

        if os.path.isdir(full_path):
            subtree = build_tree(full_path)
            if subtree and (subtree["files"] or subtree["dirs"]):
                tree["dirs"].append(subtree)

        elif item.endswith(".html") and item != "404.html" and not item.startswith("."):
            tree["files"].append(item)

    return tree


def get_title(full_file_path):
    with open(full_file_path, "r", encoding="utf-8", errors="ignore") as f:
        parser.current_title = ""
        parser.feed(f.read())
        return parser.current_title.strip()


def generate_html_list(tree, web_root):
    html = "<ul>\n"

    for file in tree["files"]:
        full_file_path = os.path.join(tree["path"], file)
        relative_to_root = os.path.relpath(full_file_path, web_root)
        absolute_url = "/" + relative_to_root.replace(os.sep, "/")
        html += f'  <li class="file"><a href="{absolute_url}">{file} ∙ {get_title(full_file_path)}</a></li>\n'

    for subdir in tree["dirs"]:
        html += f'  <li class="folder">{subdir["name"]}/\n'
        html += generate_html_list(subdir, web_root)
        html += "  </li>\n"

    html += "</ul>\n"
    return html


if __name__ == "__main__":
    raw_data = build_tree(".")
    content = generate_html_list(raw_data, ".")

    html_output = f"""
			<!DOCTYPE html>
			<html lang="en">
			<head>
					<meta charset="utf-8" />
					<meta name="viewport" content="width=device-width" />
					<meta name="color-scheme" content="light dark" />
					<title>test.sidvishnoi.com - all tests</title>
					<style>
							body {{ line-height: 1.5; }}
							ul {{ list-style: none; margin: 0; padding-left: 0.5em; border-left: 1px solid light-dark(#111, #eee); }}
					</style>
			</head>
			<body>
					<h1>Site Contents</h1>
					{content}
			</body>
			</html>
		"""

    with open("404.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    print("Done! 404.html created.")
