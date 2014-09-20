#This class define the Entry class
class Entry:
    def __init__(self, word, logP, backPnt = None, inDict = False, isNum = False, isCharNum = False):
        self.word = word
        self.logP = logP
        self.backPnt = backPnt
        self.inDict = inDict
        self.isNum = isNum
        self.isCharNum = isCharNum
    def __str__(self):
        return '(word: ' + self.word + ', logP: ' + str(self.logP) + ', inDict:' + str(self.inDict) + ', isNum:' + str(self.isNum) + ', isCharNum:' + str(self.isCharNum) + ')'

    @staticmethod
    def rollback(firstEntry):
        outString = ""
        preEntry = firstEntry
        while (preEntry.backPnt):
            outString = " " + preEntry.word + outString
            preEntry = preEntry.backPnt
        outString = preEntry.word + outString
        return outString


