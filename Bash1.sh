FILE_NAME=diff_report_$2_vs_$3.txt
CURRENT_TIME="`date "+%Y-%m-%d %H:%M:%S"`"
touch $FILE_NAME
echo ================================ > $FILE_NAME
echo Реопзиторий: $1 >> $FILE_NAME
echo Ветка 1: $2 >> $FILE_NAME
echo Ветка 2: $3 >> $FILE_NAME
echo Дата генерации: $CURRENT_TIME >> $FILE_NAME
echo ================================ >> $FILE_NAME
echo "" >> $FILE_NAME
echo СПИСОК ИЗМЕНЕННЫХ ФАЙЛОВ: >> $FILE_NAME
git clone $1
DIR="$(basename "$_" .git)"
cd $DIR
git checkout $3
git checkout $2
COMPARE="$(git diff --name-status $2..$3)"
A_COUNT=0
D_COUNT=0
M_COUNT=0
cd ..
rm -rf $DIR
while IFS=$'\t' read -r status file; do
	echo "$status $file" >> $FILE_NAME
	if [ $status = "A" ]; then A_COUNT=$((A_COUNT+1))
	elif [ $status = "D" ]; then D_COUNT=$((D_COUNT+1))
	elif [ $status = "M" ]; then M_COUNT=$((M_COUNT+1))
	fi
done <<< "$COMPARE"
echo "" >> $FILE_NAME
echo СТАТИСТИКА: >> $FILE_NAME
echo Всего измененных файлов: $((A_COUNT+D_COUNT+M_COUNT)) >> $FILE_NAME
echo Добавлено \(A\): $A_COUNT >> $FILE_NAME
echo Удалено \(D\): $D_COUNT  >> $FILE_NAME
echo Изменено \(M\): $M_COUNT >> $FILE_NAME
