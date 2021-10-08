#!/bin/env bash

set -ex

if [[ -x godotenv ]]; then \
  COMMAND="godotenv docker"
else
  COMMAND="docker"
fi

$COMMAND build --build-arg ALPINE_MIRROR . -t bilibili-live-notification
