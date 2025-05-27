#!/bin/bash

set -e

# Start the pipeline
python -m pipeline.main &

# Keep the container running
tail -f /dev/null