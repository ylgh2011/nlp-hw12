for i in {0..100}
do
	for j in {0..1}
	do
		python main.py $i $j | python score-segments.py
		echo "i=$i j=$j"
	done
done
