import requests
import mwclient
import mwparserfromhell


pageCache = {}
redirectCache = {}
jobCache = {}
site = mwclient.Site("oxygennotincluded.gamepedia.com", path="/")
userName = "dummy"
password = "thicc"
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
    url = "https://oxygennotincluded.gamepedia.com/api.php"
    params = {
        "action": "query",
        "generator": "allredirects",
        "garlimit": "300",
        "format": "json",
        "formatversion": "2"
    }
    if cont is not None:
        for p in cont:
            params[p] = cont[p]
    print("Query params:", params)
    return requests.get(url, params).json()


def upperfirst(x):
    return x[:1].upper() + x[1:]


cont = None
while True:
    response = request(cont)
    all_redirects = listPageTitles(response)
    print("Queried batch of redirect pages:", all_redirects)
    for page in all_redirects:
        processBacklinks(page)
    if response.get("continue") is None:
        break
    cont = response["continue"]

print("Job list:", jobCache)

for job in jobCache:
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
    try:
        page.edit(str(pageText),
                  summary="Resolve links to redirect",
                  minor=True)
    except:
        print("Unsuccesful edit")
