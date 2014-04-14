#!/usr/bin/env bash
# Start redis daemons.
# Usage: start-redis.sh -d

pid="$(command \pgrep redis-server)"
if [ "x${pid}" != "x" ]; then
    echo 'Redis-server is already running. Exit.'
    exit 1
fi

case "$1" in
    -d|--daemon)
		echo "starting redis-server ..."
        $0 < /dev/null &> /dev/null & disown
        exit 0
        ;;
    -n|--normal)
		/usr/local/bin/redis-server
		;;
    *)
		# do background stuff here
		echo "Logging into ~/tmp/logs/redis.log"
		/usr/local/bin/redis-server > /path/to/logs/redis.log
        ;;
esac
