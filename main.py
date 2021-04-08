#!/usr/bin/python
import argparse
import configparser
import mwclient
import mwparserfromhell


global userName, password

argParser = argparse.ArgumentParser(description="Resolve a wiki's links \
to redirect pages")
argParser.add_argument("-c", "--config", default="mwlinkresolve.conf",
                       help="Specifies config file path containing default \
options. Defaults to \"mwlinkresolve.conf\".")
argParser.add_argument("-s", "--site",
                       help="API URL of wiki. If it doesn't end in \
\"api.php\", it will be interpreted as a fandom.com wiki name.")
argParser.add_argument("-u", "--user",
                       help="Botpassword name.")
argParser.add_argument("-p", "--password",
                       help="Botpassword token.")
argParser.add_argument("--dry", action="store_true",
                       help="Skip all edits.")
args = argParser.parse_args()

try:
    config = configparser.ConfigParser()
    config.read(args.config)
    config = config["Config"]
    if config.get("Site") is not None:
        url = config["Site"]
    if config.get("User") is not None:
        userName = config["User"]
    if config.get("Password") is not None:
        password = config["Password"]
except:
    if not (args.site and args.user and args.password):
        print("Unable to read config file, and not all necessary \
options are provided.")
        exit()
if args.site is not None:
    url = args.site
if args.user is not None:
    userName = args.user
if args.password is not None:
    password = args.password
dry = args.dry
if dry:
    print("This will be a dry run.")

if url[-7:] != "api.php":
    url += ".fandom.com/"
else:
    url = url[:-7]

pageCache = {}
redirectCache = {}
jobCache = {}

index = url.find("/")
site = mwclient.Site(url[:index], path=url[index:])
site.login(userName, password)


def getPage(title):
    if not pageCache.get(title):
        pageCache[title] = site.pages[title]
    return pageCache[title]


def cachePage(page):
    if not pageCache.get(page.name):
        pageCache[page.name] = page
    return page


def getRedirect(title):
    if not redirectCache.get(title):
        redirectCache[title] = getPage(title).redirects_to().name
    return redirectCache[title]


def addJob(linker, linked):
    if not jobCache.get(linker):
        jobCache[linker] = []
    if linked not in jobCache[linker]:
        jobCache[linker].append(linked)


def processBacklinks(title):
    page = getPage(title)
    for link in page.backlinks():
        cachePage(link)
        addJob(link.name, title)


def listPageTitles(response):
    arr = []
    pages = response["query"]["pages"]
    for page in pages:
        title = page.get("title")
        if title is not None:
            arr.append(title)
    return arr


def request(cont=None):
    params = {
        "generator": "allredirects",
        "garlimit": "300",
        "format": "json",
        "formatversion": "2"
    }
    if cont is not None:
        for p in cont:
            params[p] = cont[p]
    print("Query params:", params)
    return site.get('query', **params)


def upperfirst(x):
    return x[:1].upper() + x[1:]


cont = None
while True:
    response = request(cont)
    all_redirects = listPageTitles(response)
    print("Queried batch of redirect pages:", all_redirects)
    print("Processing batch. This might take a bit.")
    for page in all_redirects:
        processBacklinks(page)
    if response.get("continue") is None:
        break
    cont = response["continue"]

print("Job list:", jobCache)

for job in jobCache:
    changed = False
    page = getPage(job)
    pageText = mwparserfromhell.parse(page.text())
    for link in pageText.filter_wikilinks():
        title = link.title
        text = link.text
        if text is None:
            text = title
        target = str(title)
        if upperfirst(target) in jobCache[job]:
            redirect = getRedirect(target)
            print(job,
                  "-> Found link", link,
                  "Should be pointing to", redirect)
            pageText.replace(link,
                             mwparserfromhell.nodes.Wikilink(redirect, text))
            changed = True
    if changed:
        if not dry:
            try:
                page.edit(str(pageText),
                          summary="Resolve links to redirect",
                          minor=True)
            except:
                print("Unsuccesful edit")
        else:
            print("Skipping edit. (Dry run.)")
