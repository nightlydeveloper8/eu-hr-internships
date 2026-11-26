#!/usr/bin/env bash
# Publish the single prepared commit without overwriting a concurrent update.
set -euo pipefail

for attempt in 1 2 3; do
    if git pull --rebase origin main; then
        if git push origin HEAD:main; then
            exit 0
        fi
    elif test -d "$(git rev-parse --git-path rebase-merge)" ||
         test -d "$(git rev-parse --git-path rebase-apply)"; then
        git rebase --abort
        exit 1
    fi
done
exit 1
