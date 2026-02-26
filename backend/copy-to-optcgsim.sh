#!/bin/bash

# OPTCGSim Card Copy Script
# This script searches for OPTCGSim directories on your Mac and copies card images to them

SEARCH_PATHS=("/Applications" "$HOME/Applications")
CARD_SUBPATH="Contents/Resources/Data/StreamingAssets/Cards"

echo "🔍 Searching for OPTCGSim directories..."

# Search for OPTCGSim in common locations
TARGETS=""
for search_path in "${SEARCH_PATHS[@]}"; do
  if [ -d "$search_path" ]; then
    TARGETS+=$(find "$search_path" -type d -name "OPTCGSim*" 2>/dev/null)
    TARGETS+=$'\n'
  fi
done

# Remove empty lines
TARGETS=$(echo "$TARGETS" | grep -v '^[[:space:]]*$')

if [ -z "$TARGETS" ]; then
  echo "❌ No OPTCGSim directories found in /Applications or ~/Applications"
  echo "   If your OPTCGSim is installed elsewhere, you can manually specify:"
  echo "   sudo bash copy-to-optcgsim.sh /path/to/OPTCGSim.app"
  exit 1
fi

# Process each found directory
FOUND_COUNT=0
while IFS= read -r target; do
  [ -z "$target" ] && continue
  
  CARDSPATH="$target/$CARD_SUBPATH"
  
  if [ ! -d "$CARDSPATH" ]; then
    echo "⚠️  Cards path not found: $CARDSPATH"
    echo "   Skipping..."
    continue
  fi
  
  echo ""
  echo "✓ Found: $target"
  
  # Copy set directories
  for dir in */; do
    [ -d "$dir" ] || continue
    
    # Create set directory if it doesn't exist
    mkdir -p "$CARDSPATH/$dir"
    
    echo "  📋 Copying $dir -> $CARDSPATH/"
    
    # Copy all files and show detailed output
    cp -R "$dir"/* "$CARDSPATH/$dir/" 2>/dev/null
    
    if [ $? -eq 0 ]; then
      FILE_COUNT=$(ls "$CARDSPATH/$dir" 2>/dev/null | wc -l)
      echo "     ✓ Copied ($FILE_COUNT files)"
    else
      echo "     ❌ Failed to copy $dir"
    fi
  done
  
  echo "  ✓ Transfer complete!"
  ((FOUND_COUNT++))
  
done <<< "$TARGETS"

echo ""
if [ $FOUND_COUNT -eq 0 ]; then
  echo "❌ No valid targets were updated"
  exit 1
else
  echo "✅ Successfully updated $FOUND_COUNT OPTCGSim installation(s)"
fi
