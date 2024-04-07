#!/usr/bin/env python3

import os

from bs4 import BeautifulSoup

log_file = open(os.path.join("src", "chars.txt"), "w")


def log(*values):
    print(*values)
    print(*values, file=log_file, flush=True)


total = 0
path = os.path.join("docs", "files")
for file_name in os.listdir(path):
    if not file_name.endswith(".html"):
        continue

    with open(os.path.join(path, file_name), "r") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    chars = len(text)
    total += chars

    log(f"{chars}\t{file_name}")
log(f"{total}\tTOTAL")
