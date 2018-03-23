#!/bin/bash

INSERT_USAGE=$(grep -n  '## Commands$' docs/index.md | cut -d ":" -f1)
INSERT_USAGE=$(($INSERT_USAGE + 1)) 
head -$(($INSERT_USAGE)) docs/index.md > README.md
./document_commands.py >> README.md
INSERT_USAGE=$(($INSERT_USAGE + 1))
tail +$(($INSERT_USAGE)) docs/index.md
