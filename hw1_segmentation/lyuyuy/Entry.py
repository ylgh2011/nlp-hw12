#This class define the Entry class
class Entry:
    def __init__(self, word, logP, backPnt = None, inDict = False, isNum = False, isUnitNum = False, isChNum = False, isSingleCharInUnigram = False):
        self.word = word
        self.logP = logP
        self.backPnt = backPnt
        self.inDict = inDict
        self.isNum = isNum
        self.isUnitNum = isUnitNum
        self.isChNum = isChNum
        self.isSingleCharInUnigram = isSingleCharInUnigram
    def __str__(self):
        return '(word: ' + self.word + ', logP: ' + str(self.logP) + ', inDict:' + str(self.inDict) + ', isNum:' + str(self.isNum) + ', isUnitNum:' + str(self.isUnitNum) + ', isSingleCharInUnigram:' + str(self.isSingleCharInUnigram) + ')'

    @staticmethod
    def rollback(firstEntry):
        outString = ''
        preEntry = firstEntry
        while preEntry.backPnt:
            outString = " " + preEntry.word + outString
            preEntry = preEntry.backPnt
        outString = preEntry.word + outString
        return outString


