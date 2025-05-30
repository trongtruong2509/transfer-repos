#!/bin/bash

# INPUT_CSV="transfer_repos.csv"
INPUT_CSV="sample_repos.csv"
LOG_FILE="delete_repos.log"
DRY_RUN=false

# Check for dry-run flag
if [[ "$1" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "⚠️  DRY RUN MODE: No repositories will be deleted."
fi

# Check for token
if [[ -z "$GITHUB_TOKEN" ]]; then
  echo "❌ GITHUB_TOKEN environment variable is not set."
  exit 1
fi

# Check file existence
if [[ ! -f "$INPUT_CSV" ]]; then
  echo "❌ File $INPUT_CSV not found!"
  exit 1
fi

# Start logging
echo "==== Deletion started at $(date) ====" > "$LOG_FILE"

# Process CSV, skipping header
tail -n +2 "$INPUT_CSV" | while IFS=',' read -r source_org repo_name dest_org; do
  repo_full="$source_org/$repo_name"
  echo "🗑️  Attempting to delete: $repo_full" | tee -a "$LOG_FILE"

  if $DRY_RUN; then
    echo "ℹ️  [DRY RUN] Skipping actual deletion of $repo_full" | tee -a "$LOG_FILE"
    continue
  fi

  response=$(curl -s -L -o /dev/null -w "%{http_code}" -X DELETE \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$repo_full")

  if [[ "$response" == "204" ]]; then
    echo "✅ Successfully deleted: $repo_full" | tee -a "$LOG_FILE"
  else
    echo "❌ Failed to delete: $repo_full (HTTP status: $response)" | tee -a "$LOG_FILE"
  fi
done

echo "==== Deletion finished at $(date) ====" >> "$LOG_FILE"
