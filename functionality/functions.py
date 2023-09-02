import urllib.request
import datetime
from . import search
from .shunting_yard import shuntingYardAlgo
from string import digits
from random import choice
import re
import os


class Functions:
    def __init__(self):
        # init for getWikiSummary
        self.cleanr = re.compile("<.*?>|&#[0-9]{1,6};\d+&#[0-9]{1,6};|&#[0-9]{1,6};")

        # init for tellJoke
        file = open(os.path.join(os.path.dirname(__file__), "bad_jokes.txt"), "r")
        self.jokes = file.read().split("*")
        file.close()

        # init for getFirstResult
        self.lastLinks = []
        self.lastSearchQuery = ""
        self.queryNum = 0

    def getWeather(self, place):
        if place == "":
            place = "Sofia"
        url = search.getSearch(
            "+".join(["sinoptik", urllib.parse.quote(place)]), stopAt="10-days"
        )[-1][:-8]
        if "sinoptik" not in url:
            return "Съжалявам, не можах да открия информация за това място."

        webpage = urllib.request.urlopen(url).readlines()
        for l in webpage:
            line = l.decode()
            if '<meta name="description" content=' in line:
                lft = line.find("Времето")
                rght = line.find("Подробна")
                weather = line[lft:rght]
                return weather + "_За повече информация посети:_ " + url

    def getWikiSummary(self, query):
        if query == "":
            return None
        links = search.getSearch(
            "+".join(
                [
                    "site%3Abg.wikipedia.org",
                    urllib.parse.quote(query),
                ]
            ),
            stopAt="bg.wikipedia",
        )

        if not links:
            return (
                "Съжалявам, не можах да открия информация за това. _Потърси в:_ "
                + "".join(["https://www.google.com/search?q=", query])
            )
        # not sure why unquoting fixes this
        links[-1] = urllib.parse.unquote(links[-1])
        webpage = urllib.request.urlopen(links[-1]).readlines()
        imageFound = False
        image = ""
        for l in webpage:
            line = l.decode()
            if "tbody" in line and imageFound != True:
                image = line[line.find("srcset") : line.find("2x")]
                image = image[image.rfind("//upload.wikimedia.org") :]
                image = "https:" + image
                imageFound = True
            if "<p>" in line:
                summary = line[line.find("<p>") + 3 : line.find("</p>")]

                # replace html tags with markdown
                summary = summary.replace("<br />", "\n")
                summary = summary.replace("<i>", "_")
                summary = summary.replace("</i>", "_")
                summary = summary.replace("<b>", "*")
                summary = summary.replace("</b>", "*")

                # get rid of the rest of the html tags and '&' entities using RegEx
                summary = re.sub(self.cleanr, "", summary)
                answerEnd = " _За повече информация посети:_ " + links[-1]
                if len(summary + answerEnd) > 768:
                    summary = summary[: 760 - len(answerEnd)]
                    summary = summary[: summary.rfind(" ")] + "... "
                if imageFound:
                    return (
                        image,
                        summary + answerEnd,
                    )
                else:
                    return summary + answerEnd

    def getDay(self, empty):
        days = (
            "понеделник",
            "вторник",
            "сряда",
            "четвъртък",
            "петък",
            "събота",
            "неделя",
        )
        months = (
            "януари",
            "февруари",
            "март",
            "април",
            "май",
            "юни",
            "юли",
            "август",
            "септември",
            "октомври",
            "ноември",
            "декември",
        )
        x = datetime.date.today()
        return (
            "Датата днес е "
            + repr(x.day)
            + " "
            + months[x.month - 1]
            + " "
            + repr(x.year)
            + ". Днес се пада "
            + days[x.weekday()]
            + "."
        )

    def getWordMeaning(self, word):
        if word == "":
            return None
        links = search.getSearch(
            "+".join(
                [
                    "site%3Aonlinerechnik.com",
                    urllib.parse.quote(word),
                ]
            ),
            stopAt="talkoven.onlinerechnik.com/duma",
        )

        if not links:
            return (
                "Съжалявам, не можах да открия информация за тази дума. Потърси в "
                + "".join(["https://www.google.com/search?q=", word])
            )
        links[-1] = urllib.parse.unquote(links[-1])
        webpage = urllib.request.urlopen(links[-1]).read()
        webpage = webpage.decode()
        meaning = webpage[webpage.find('<span class="dumaintext">') + 25 :]
        word = meaning[: meaning.find("</span>")]
        meaning = meaning[meaning.find("<p>") + 3 : meaning.find("</p>")]

        meaning = meaning.replace("<br />", "\n")
        meaning = meaning.replace("<i>", "_")
        meaning = meaning.replace("</i>", "_")
        meaning = meaning.replace("<b>", "*")
        meaning = meaning.replace("</b>", "*")

        return "*" + word + "*\n" + meaning.strip()

    def getFirstResult(self, query):
        if query == "":
            return None
        if query == self.lastSearchQuery:
            self.queryNum += 1
            if self.queryNum > 9:
                return "Повече не мога да търся това."
            return self.lastLinks[self.queryNum]

        self.lastLinks = search.getSearch(urllib.parse.quote(query))
        self.queryNum = 0
        self.lastSearchQuery = query

        if len(self.lastLinks) == 0:
            return "Съжалявам, не можах да открия нищо за това."
        return self.lastLinks[0]

    def doMath(self, expression):
        if expression == "":
            return None
        cleanExpression = expression.replace(" ", "")
        try:
            rpExpression = shuntingYardAlgo(cleanExpression)
        except ValueError:
            return "Не мога да сметна това което сте въвели."
        stack = []
        # print(rpExpression)
        i = 0
        try:
            while i < len(rpExpression):
                if rpExpression[i] == "+":
                    x = float(stack.pop())
                    x = float(stack.pop()) + x
                    stack.append(x)
                    i += 1
                elif rpExpression[i] == "-":
                    x = float(stack.pop())
                    x = float(stack.pop()) - x
                    stack.append(x)
                    i += 1
                elif rpExpression[i] == "/":
                    x = float(stack.pop())
                    x = float(stack.pop()) / x
                    stack.append(x)
                    i += 1
                elif rpExpression[i] == "*":
                    x = float(stack.pop())
                    x = float(stack.pop()) * x
                    stack.append(x)
                    i += 1
                elif rpExpression[i] == "^":
                    x = float(stack.pop())
                    x = pow(float(stack.pop()), x)
                    stack.append(x)
                    i += 1
                elif rpExpression[i] == " ":
                    i += 1
                else:
                    number = ""
                    while rpExpression[i] in digits or rpExpression[i] == ".":
                        number = number + rpExpression[i]
                        i += 1
                    stack.append(number)
                    if rpExpression[i] == " ":
                        i += 1
        except ZeroDivisionError:
            return "Не мога да деля на 0."
        except:
            return "Не мога да сметна това което сте въвели."
            # print("stack: " + repr(stack))
        return "Отговора на задачата е: " + repr(stack[-1])

    def tellJoke(self, rest):
        if "ВИЦ" in rest or "ШЕГА" in rest:
            return choice(self.jokes)[:-1]
