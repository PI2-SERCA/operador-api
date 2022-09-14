# $1 => Sleep time (in seconds) between rabbitmq and operador start

# Example:  sh start.sh 10

[ -z "$1" ] && sleep_time=5 || sleep_time="$1"

docker-compose up -d rabbitmq

sleep $sleep_time

docker-compose up -d operador
