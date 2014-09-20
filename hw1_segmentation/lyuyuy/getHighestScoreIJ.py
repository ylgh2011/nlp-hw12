import sys

bestScore = float('-Inf')
bestIJ = ''
for i in range(1, len(sys.argv)):
    with open(sys.argv[i], 'r') as fin:
        while True:
            line1 = fin.readline()
            line2 = fin.readline()
            if (line1 is None) or (len(line1) < len('Score: ')):
                break

            curScore = float(line1[len('Score: ') : ])
            if curScore > bestScore:
                bestScore = curScore
                bestIJ = line2


print bestScore, bestIJ
