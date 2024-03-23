#!/usr/bin/env python3

import requests, os, re
web = requests.Session()

archive_dir_name = "docs"
files_dir_name = "files"
os.makedirs(os.path.join(archive_dir_name, files_dir_name), exist_ok=True)

site_url = "http://samlib.ru"
index_url = f"{site_url}/r/ryzhkow_w_a/"
index_image_file_name = "vlad.jpg"
author_name = "Владимир Рыжков"

log_file = open(os.path.join("src", "log.txt"), "w")

def log(*values):
    print(*values)
    print(*values, file=log_file, flush=True)

header_lines = [
    '<!DOCTYPE html>',
    '<meta charset="utf-8" />',
    '<meta name="viewport" content="width=device-width, initial-scale=1" />',
    '<style>',
    'html, body {font-size: 140%}',
    '</style>',
]

index_lines = header_lines + [
    f'<title>{author_name}</title>',
    f'<h1 style="font-size: 1.5em">{author_name}</h1>',
    f'<img src="{index_image_file_name}" alt="" />',
]
initial_index_lines_length = len(index_lines)

sections = 0
documents = 0
images = 0
image_file_names = set()

section_re = re.compile(r'([^>]+):\s*(?:</font></a>)?<gr0>')
assert section_re.search('</small><p><font size=+1><b><a name=gr1>В строке, тебя достойной:<gr0></b></font><br>').group(1) == 'В строке, тебя достойной'
assert section_re.search('</small><p><font size=+1><b><a name=gr0><a href=/type/index_type_13-1.shtml><font color=#393939>Эссе:</font></a><gr0></b></font><br>').group(1) == 'Эссе'

document_re = re.compile(r'<DL><DT><li>.*?<A HREF=([^>]+)><b>\s*(.+?)\s*</b></A>')
assert document_re.search('<DL><DT><li><A HREF=10zavet.shtml><b>Был завет мне: "Позови...</b></A> &nbsp; <b>0k</b> &nbsp; <small> Поэзия  <A HREF="/comment/r/ryzhkow_w_a/10zavet">Комментарии: 28 (31/12/2022)</A> </small><br></DL>').groups() == ('10zavet.shtml', 'Был завет мне: "Позови...')
assert document_re.search('<DL><DT><li><font color=red size=-2>Upd</font><A HREF=060pogremusha.shtml><b>Погремушка к "Постебушкам"</b></A> &nbsp; <b>0k</b> &nbsp; <small> Поэзия  <A HREF="/comment/r/ryzhkow_w_a/060pogremusha">Комментарии: 1 (04/11/2008)</A> </small><br></DL>').groups() == ('060pogremusha.shtml', 'Погремушка к "Постебушкам"')
assert document_re.search('<DL><DT><li> <b>Рыжков В.А. </b> <A HREF=1_haiam.shtml><b> Подражание Хайяму</b></A> &nbsp; <b>33k</b> &nbsp; <small> Поэзия  <A HREF="/comment/r/ryzhkow_w_a/1_haiam">Комментарии: 12 (21/03/2011)</A> </small><br><DD><font color="#555555">Все иллюстрации  - в тексте.</font><DD><small><a href=/img/r/ryzhkow_w_a/1_haiam/index.shtml>Иллюстрации/приложения: 31 шт.</a></small></DL>').groups() == ('1_haiam.shtml', 'Подражание Хайяму')

image_re = re.compile(r'<img src="?([^">]+)/([^/">]+)"?(.*?)>')
full_groups = lambda matched: (matched.group(0), ) + matched.groups("")
assert full_groups(image_re.search('<img src="/img/r/ryzhkow_w_a/1_haiam/01.jpg" width="300" alt=" []" height="300" > foo<b>')) == ('<img src="/img/r/ryzhkow_w_a/1_haiam/01.jpg" width="300" alt=" []" height="300" >', '/img/r/ryzhkow_w_a/1_haiam', '01.jpg', ' width="300" alt=" []" height="300" ')
assert full_groups(image_re.search('ХХХ  <img src="/img/r/ryzhkow_w_a/1_haiam/09.gif" width="385" alt=" []" height="307" > bar <b>')) == ('<img src="/img/r/ryzhkow_w_a/1_haiam/09.gif" width="385" alt=" []" height="307" >', '/img/r/ryzhkow_w_a/1_haiam', '09.gif', ' width="385" alt=" []" height="307" ')
assert full_groups(image_re.search('<img src=http://denis.ryzhkov.org/img/dont-do.gif> baz<b>')) == ('<img src=http://denis.ryzhkov.org/img/dont-do.gif>', 'http://denis.ryzhkov.org/img', 'dont-do.gif', '')

def download_image(image_url, image_file_name):
    with open(image_file_name, "wb") as image_file:
        image_file.write(web.get(image_url).content)

download_image(
    index_url + ".photo1.jpg",
    os.path.join(archive_dir_name, index_image_file_name),
)

def assert_safe_file_name(file_name):
    for bad in "..", "/":
        assert bad not in file_name, file_name

def close_ul_if_needed():
    if len(index_lines) > initial_index_lines_length:
        index_lines.append('</ul>')

index_text = web.get(index_url).text
for line in index_text.split("\n"):

    matched = section_re.search(line)
    if matched:
        section_title = matched.group(1)
        log(f"\nsection: {section_title}")
        sections += 1

        close_ul_if_needed()
        index_lines.extend([
            '',
            f'<h2 style="font-size: 1em">{section_title}</h2>',
            '<ul>'
        ])
        continue

    matched = document_re.search(line)
    if not matched:
        continue

    document_url, document_title = matched.groups()
    log(f"document: {document_url}")
    documents += 1
    assert_safe_file_name(document_url)

    document_lines = header_lines + [
        f'<title>{document_title}</title>',
        # Vlad asked to delete: f'<div style="text-align: right">{author_name}</div>',
        f'<h1 style="font-size: 1em">{document_title}</h2>',
        '',
    ]

    document_text = web.get(index_url + document_url).text
    document_url = document_url.replace(".shtml", ".html")
    index_lines.append(f'<li><a href="{files_dir_name}/{document_url}">{document_title}</a></li>')

    end_to_find = None
    for line in document_text.split("\n"):
        if not end_to_find:
            if '<pre>' in line:
                end_to_find = '</pre>'
            elif '<dd>' in line:
                end_to_find = '<!-- --'
            else:
                continue

        matched = image_re.search(line)
        if matched:
            image_tag = matched.group(0)
            image_path, image_file_name, image_tail = matched.groups()
            image_url = (site_url if image_path.startswith("/") else "") + f"{image_path}/{image_file_name}"

            log(f"image: {image_url}")
            images += 1
            assert_safe_file_name(image_file_name)
            assert image_file_name not in image_file_names, image_file_name
            image_file_names.add(image_file_name)
            download_image(image_url, os.path.join(archive_dir_name, files_dir_name, image_file_name))
            line = line.replace(image_tag, f'<img src="{image_file_name}"{image_tail}>')

        document_lines.append(line)

        if end_to_find in line:
            break

    with open(os.path.join(archive_dir_name, files_dir_name, document_url), "w") as document_file:
        document_file.write("\n".join(document_lines))

close_ul_if_needed()

index_lines.extend([
    '',
    '<h2 style="font-size: 1em">Стихи и проза</h2>',
    '<ul>',
    '<li><a href="http://samlib.ru/r/ryzhkow_w_a/">Журнал "Самиздат". Рыжков Владимир. Подорожная</a></li>',
    '<li><a href="https://stihi.ru/avtor/ryzhkov">Владимир Рыжков / Стихи.ру</a></li>',
    '<li><a href="https://proza.ru/avtor/vryzhkov">Владимир Рыжков / Проза.ру</a></li>',
    '</ul>',
])

with open(os.path.join(archive_dir_name, "index.html"), "w") as index_file:
    index_file.write("\n".join(index_lines))

log()
log("sections:", sections)
log("documents:", documents)
log("images:", images)
