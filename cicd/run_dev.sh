#!/bin/bash

if [ -z "$1" ]; then
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml up -d --remove-orphans
elif [ "$1" = "--server" ]; then
    docker-compose -f docker-compose.dev.yml build core
    docker-compose -f docker-compose.dev.yml up -d --remove-orphans core
elif [ "$1" = "--client" ]; then
    docker-compose -f docker-compose.dev.yml build client
    docker-compose -f docker-compose.dev.yml up -d --remove-orphans client
fi
