freference = open('./data/reference', 'r')
foutput = open('./output', 'r')
fcompare = open('./cmp.txt', 'w')
ans = ''

while True:
	line_ref = freference.readline()
	line_out = foutput.readline()

	if (line_ref == '') or (line_out == ''):
		break

	if line_ref != line_out:
		ans += '_'*max(len(line_ref), len(line_out)) + '\n'
		ans += 'Ref: ' + line_ref
		ans += 'Out: ' + line_out
	

fcompare.write(ans)

fcompare.close()
foutput.close()
freference.close()

