#!/bin/bash

# Script to merge multiple pull requests into main branch
# This automates the process of merging several PRs in sequence
# Note: This script uses GitHub's pull request reference format (origin/pull/N/head)

set -e  # Exit on error (except where explicitly handled)

echo "Starting PR merge process..."

# Fetch latest changes from origin
echo "Fetching latest changes from origin..."
git fetch origin

# Checkout and update main branch
echo "Checking out main branch..."
git checkout main

echo "Pulling latest changes on main..."
git pull origin main

# List of PRs to merge
PRS=(33 32 31 30 28 25 23 22)

# Merge each PR
for PR in "${PRS[@]}"; do
    echo "Merging PR #${PR}..."
    # Temporarily disable exit-on-error for the merge command to handle conflicts gracefully
    set +e
    git merge origin/pull/${PR}/head --no-edit
    MERGE_STATUS=$?
    set -e
    
    if [ $MERGE_STATUS -eq 0 ]; then
        echo "Successfully merged PR #${PR}"
    else
        echo "ERROR: Failed to merge PR #${PR}"
        echo "Please resolve conflicts manually and continue"
        exit 1
    fi
done

echo "All PRs merged successfully!"
echo "Don't forget to push the changes: git push origin main"
