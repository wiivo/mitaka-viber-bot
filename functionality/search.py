import urllib.request


def getSearch(search, searchNum=10, stopAt="&"):
    """Gets the first searchNum (defualts at 10) google searches\n
    Optionally, stop searching when a link containing stopAt is found"""
    headers = {}
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    url = "".join(["https://www.google.com/search?q=", search])
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req).readlines()

    links = []
    for l in resp:
        line = l.decode()
        if "egMi0 kCrYT" in line:
            left = line.find("url=http")
            line = line[left:]
            while left != -1 and len(links) < searchNum:
                right = line.find("&")
                links.append(line[4:right])
                if stopAt in links[-1]:
                    break
                line = line[right:]
                left = line.find("url=http")
                line = line[left:]
    return links
