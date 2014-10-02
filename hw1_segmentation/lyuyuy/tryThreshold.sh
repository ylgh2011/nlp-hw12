for i in {0..50}
do
	for j in {0..0}
	do
		python default.py $i $j | python score-segments.py
		echo "i=$i j=$j"
	done
done
