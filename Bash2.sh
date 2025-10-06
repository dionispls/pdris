PID_EXTERNAL=$(pgrep -f "$0" | grep -v $$)
if [ "$1" = "START" ]; 
	then if [ -n "$PID_EXTERNAL" ]; then echo "Такой процесс уже запущен"; exit; fi
nohup ./Bash2.sh &
exit
fi

if [ "$1" = "STATUS" ];
	then if [ -n "$PID_EXTERNAL" ]; then echo "Процесс запущен"
	     else echo "Процесс не запущен"
 	     fi
	exit
fi

if [ "$1" = "STOP" ];
        then if [ -n "$PID_EXTERNAL" ]; then kill $PID_EXTERNAL; echo "Убили процесс"
	     else echo "Нет такого процесса" 
	     fi
	exit
fi

touch "system_report_$(date '+%Y-%m-%d').csv"
while true;do
	ALL_MEMORY=$(free -m | awk '/Mem:/ {print $2}')
	FREE_MEMORY=$(free -m | awk '/Mem:/ {print $4}')
	PERCENT_MEMORY=$(( (ALL_MEMORY - FREE_MEMORY) * 100 / ALL_MEMORY))
	PERCENT_CPU=$(top -bn1 | awk '/Cpu\(s\)/ {print 100 - $8}')
	PERCENT_DISK=$(df / | awk 'NR==2 {gsub(/%/,"",$5); print $5}')
	MINUTE_LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $1}' | xargs)
	TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
	echo "$TIMESTAMP;$ALL_MEMORY;$FREE_MEMORY;$PERCENT_MEMORY;$PERCENT_CPU;$PERCENT_DISK;$MINUTE_LOAD" >> "system_report_$(date '+%Y-%m-%d').csv"
	sleep 600
done
