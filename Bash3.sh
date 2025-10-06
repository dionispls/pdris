cat $1 | grep $2 > "errors.txt"
wc -l < "errors.txt" > "count_errors.txt"

