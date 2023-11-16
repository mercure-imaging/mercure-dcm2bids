#!/usr/bin/env bash
set -Eeo pipefail
echo "-- Starting dcm2bids conversion..."
conda run -n dcm2bids python m_dcm2bids.py $MERCURE_IN_DIR $MERCURE_OUT_DIR
echo "-- Done."
