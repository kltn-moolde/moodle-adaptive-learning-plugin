#!/bin/bash
MAX_SIZE=100000000  # 100 MB

echo "Scanning for files larger than $(($MAX_SIZE / 1000000))MB..."

# Add all files smaller than MAX_SIZE
find . -type f -size -${MAX_SIZE}c -not -path './.git/*' -print0 | xargs -0 git add

echo "Done. Files larger than $(($MAX_SIZE / 1000000))MB were skipped."