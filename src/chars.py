#!/usr/bin/env python3

from bs4 import BeautifulSoup

log_file = open("src/chars.txt", "w")


def log(*values):
    print(*values)
    print(*values, file=log_file, flush=True)


total = 0

with open("docs/index.html", "r") as file:
    html = file.read()

soup = BeautifulSoup(html, "html.parser")
for li in soup.find_all("li"):
    a = li.a
    href = a["href"]
    if not href.startswith("files/") or not href.endswith(".html"):
        continue

    with open(f"docs/{href}", "r") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    chars = len(text)
    total += chars

    log(f"{chars}\t{soup.title.string}")
log(f"{total}\tTOTAL")
