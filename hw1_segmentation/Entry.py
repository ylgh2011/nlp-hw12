#This class define the Entry class
class Entry:
    def __init__(self, word, logP, backPnt = None, inDict = False):
        self.word = word
        self.logP = logP
        self.backPnt = backPnt
        self.inDict = inDict
    @staticmethod
    def rollback(firstEntry):
        outString = ""
        preEntry = firstEntry
        while (preEntry.backPnt):
            outString = " " + preEntry.word + outString
            preEntry = preEntry.backPnt
        outString = preEntry.word + outString
        return outString
