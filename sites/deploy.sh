#!/bin/bash
set -e
set -u

SITES_DIR=$(dirname "$0")
rsync --archive --verbose --compress --delete -e "ssh -i $PRIVATE_KEY_FILE -o 'StrictHostKeyChecking=no' -p $SSH_PORT" "$SITES_DIR/hurl.dev/_site/" "$SSH_USER"@hurl.dev:www

