
#!/bin/bash

PERCENT=${1:-33}

# Clamp between 0 and 100
PERCENT=$(( PERCENT < 0 ? 0 : PERCENT > 100 ? 100 : PERCENT ))

# 6500K = 0%, 3500K = 100%
TEMP=$((6500 - (PERCENT * 3000 / 100)))

qdbus org.kde.KWin /org/kde/KWin/NightLight \
  org.kde.KWin.NightLight.preview "$TEMP"

echo "Night Light: ${PERCENT}% (${TEMP}K)"
