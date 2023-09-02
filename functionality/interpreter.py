from .functions import Functions
from string import punctuation


class Interpreter:
    def __init__(self):
        f = Functions()
        # add keywords and commands here
        self.functionDict = {
            "ВРЕМЕТО": f.getWeather,
            "КАКВО Е": f.getWikiSummary,
            "КОЙ Е": f.getWikiSummary,
            "КОЯ Е": f.getWikiSummary,
            "КАЖИ МИ ЗА": f.getWikiSummary,
            "КОЙ ДЕН": f.getDay,
            "КАКВО ОЗНАЧАВА": f.getWordMeaning,
            "ПОТЪРСИ": f.getFirstResult,
            "СМЕТНИ": f.doMath,
            "КОЛКО Е": f.doMath,
            "КАЖИ": f.tellJoke,
            "АМИ": self.repeat,
        }
        self.puncDict = str.maketrans("", "", punctuation)
        self.removePunc = True
        self.justToldRepeatable = False
        self.lastAnswer = None

    def executeCommand(self, query: str):
        "executes command based on search query"
        # if you get one of these words and you can repeat - repeat
        if ("ОЩЕ" in query or "ПАК" in query) and self.justToldRepeatable:
            return self.repeat(self.lastAnswer[1])
        for i in self.functionDict.keys():
            if i in query:
                # remove punctuation unless its a calculate function
                if i == "СМЕТНИ":
                    self.removePunc = False
                elif i != "АМИ":
                    self.removePunc = True

                if self.removePunc:
                    query.translate(self.puncDict)

                # store query and get answer
                x = query[query.find(i) + len(i) :]
                answer = self.functionDict[i](x.strip(" ?"))

                if (i == "КАЖИ" or i == "ПОТЪРСИ") and answer != None:
                    self.justToldRepeatable = True
                else:
                    self.justToldRepeatable = False
                if i != "АМИ":
                    self.lastAnswer = (i, x)

                return answer

    def repeat(self, lA):
        return self.functionDict[self.lastAnswer[0]](lA.strip(" ?"))
