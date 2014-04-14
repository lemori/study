#!/usr/bin/env bash
# Stop redis daemons.
# Usage: stop-redis.sh

pkill -9 redis-server
echo 'Stopped if exists'