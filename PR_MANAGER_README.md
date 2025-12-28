# PR Management Agent

An automated tool for managing pull requests in a GitHub repository. This script processes open pull requests, attempting to merge them automatically or documenting conflicts for manual resolution.

## Features

- **Automatic Merging**: Merges PRs that have no conflicts with their target branch
- **Branch Cleanup**: Automatically deletes source branches after successful merge
- **Conflict Management**: Creates dedicated `conflicts/` branches for PRs with merge conflicts
- **Documentation**: Adds detailed comments to PRs with conflicts, listing affected files
- **Summary Reports**: Provides comprehensive reports of all processed PRs

## Requirements

- Python 3.6+
- Git (configured with push access to the repository)
- GitHub Personal Access Token (optional, for API access and PR commenting)

## Installation

No installation required beyond Python 3. The script is standalone.

## Usage

### Basic Usage

```bash
python pr_manager.py
```

This will process all open PRs in the default repository (`sburdges-eng/Pentagon-core-100-things`).

### With Custom Repository

```bash
python pr_manager.py --repo-owner <owner> --repo-name <repository>
```

### With GitHub Token (Recommended)

```bash
python pr_manager.py --github-token <your-token>
```

Or set the environment variable:

```bash
export GITHUB_TOKEN=<your-token>
python pr_manager.py
```

### Full Options

```bash
python pr_manager.py \
  --repo-owner sburdges-eng \
  --repo-name Pentagon-core-100-things \
  --github-token ghp_xxxxxxxxxxxx
```

## How It Works

For each open pull request:

1. **Fetch Latest**: Updates all remote branches
2. **Identify Target**: Determines the target branch (usually `main` or `master`)
3. **Test Merge**: Attempts a test merge without committing
4. **Success Path** (no conflicts):
   - Performs the actual merge
   - Pushes to the target branch
   - Deletes the source branch
   - Records success
5. **Conflict Path** (conflicts detected):
   - Creates a new branch: `conflicts/<original-branch-name>`
   - Adds a conflicts documentation file
   - Pushes the conflicts branch
   - Comments on the PR with conflicting files
   - Leaves the original PR open

## Output

The script provides real-time progress updates and a final summary:

```
PR PROCESSING SUMMARY
============================================================

✓ Successfully Merged and Deleted:
  - PR #15: Feature: Add new widget
    Branch: feature/new-widget

✗ Moved to Conflicts Branch:
  - PR #17: Fix: Update dependencies
    Branch: fix/dependencies -> conflicts/fix/dependencies
    Conflicts in: package.json, requirements.txt

============================================================
Total processed: 2
Merged: 1
Conflicts: 1
============================================================
```

## Conflicts Resolution Workflow

When conflicts are detected:

1. A new branch `conflicts/<branch-name>` is created
2. A `CONFLICTS_<branch-name>.md` file documents the conflicting files
3. A comment is added to the PR listing the conflicts
4. The original PR remains open

To resolve:

1. Check out the conflicts branch: `git checkout conflicts/<branch-name>`
2. Review the `CONFLICTS_*.md` file
3. Manually resolve the conflicts in the listed files
4. Test your changes
5. Commit and update the original PR, or create a new one

## Safety Features

- **No Force Push**: The script never uses force push operations
- **No Auto-Resolution**: Conflicts are never automatically resolved
- **Conflict Preservation**: All conflict states are preserved for human review
- **Dry-Run Test**: Each merge is tested before being applied

## Permissions Required

The script requires:

- **Read access**: To fetch PR information and branches
- **Write access**: To push merges and create branches
- **PR comment access**: To add comments (if using GitHub token)

## Limitations

- Cannot process PRs with protected branch restrictions that prevent direct merges
- Requires appropriate git credentials for push operations
- GitHub API rate limits may apply (higher limits with authentication token)

## Troubleshooting

### "Error pushing merge"

Ensure you have push access to the repository and that git is configured with valid credentials.

### "GitHub API error: 401"

Provide a valid GitHub Personal Access Token with appropriate permissions.

### "No open PRs found"

Verify the repository name and owner are correct, and that open PRs exist.

## Example Workflow

```bash
# Set your GitHub token
export GITHUB_TOKEN=ghp_your_token_here

# Run the PR manager
python pr_manager.py

# Review the output
# - Merged PRs are automatically closed
# - Conflicted PRs have new conflicts/ branches
# - Check the summary for details

# For conflicts, review and resolve:
git fetch --all
git checkout conflicts/feature-branch
# ... resolve conflicts ...
git commit -am "Resolve conflicts"
git push origin conflicts/feature-branch
```

## Contributing

This tool is part of the Pentagon-core-100-things repository. Contributions and improvements are welcome.

## License

Same as the parent repository.
