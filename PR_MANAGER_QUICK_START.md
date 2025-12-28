# PR Manager - Quick Start Guide

Get started with the PR Management Agent in 60 seconds.

## Installation

No installation needed! Just Python 3.6+ and git.

## Quick Start

### 1. Test in Dry-Run Mode (Recommended First Step)

```bash
python pr_manager.py \
  --repo-owner <your-org> \
  --repo-name <your-repo> \
  --dry-run
```

This will analyze all open PRs without making any changes.

### 2. Run with GitHub Token

```bash
export GITHUB_TOKEN=ghp_your_token_here
python pr_manager.py \
  --repo-owner <your-org> \
  --repo-name <your-repo>
```

This will:
- ✅ Merge PRs that have no conflicts
- ✅ Delete merged branches
- ✅ Create conflicts/ branches for conflicting PRs
- ✅ Comment on conflicting PRs

### 3. Review the Summary

The script will output a summary like:

```
============================================================
PR PROCESSING SUMMARY
============================================================

✓ Successfully Merged and Deleted:
  - PR #15: Feature XYZ
  - PR #17: Bug Fix ABC

✗ Moved to Conflicts Branch:
  - PR #16: Refactor
    Branch: refactor -> conflicts/refactor
    Conflicts in: app.py, config.json

Total processed: 3
Merged: 2
Conflicts: 1
============================================================
```

### 4. Handle Conflicts

For any PRs with conflicts:

```bash
# Checkout the conflicts branch
git fetch --all
git checkout conflicts/refactor

# Review CONFLICTS_*.md file
cat CONFLICTS_refactor.md

# Manually resolve conflicts
# ... edit files, test, commit ...

# Update the original PR or create a new one
```

## GitHub Actions (Automation)

Enable automatic PR management:

1. The workflow is already included in `.github/workflows/pr-manager.yml`
2. It runs every 6 hours in dry-run mode by default
3. To run manually:
   - Go to Actions tab in GitHub
   - Select "PR Manager - Auto Merge"
   - Click "Run workflow"
   - Choose dry-run mode or live mode

## Common Options

```bash
# Dry run (test mode, no changes)
--dry-run

# Specify repository
--repo-owner myorg --repo-name myrepo

# Provide GitHub token
--github-token ghp_xxxxx
# OR
export GITHUB_TOKEN=ghp_xxxxx
```

## What Gets Merged?

✅ PRs with **no conflicts** are merged automatically
❌ PRs with **conflicts** get a conflicts/ branch created

## Safety First

- ✅ Never force pushes
- ✅ Never auto-resolves conflicts
- ✅ Always preserves conflict state
- ✅ Test with --dry-run first
- ✅ Automatic stashing of uncommitted changes

## Need Help?

See the detailed documentation:
- `PR_MANAGER_README.md` - Full documentation
- `PR_MANAGER_TEST_SCENARIOS.md` - Usage examples
- `IMPLEMENTATION_SUMMARY_PR_MANAGER.md` - Technical details

## Example Session

```bash
# 1. Test first
$ python pr_manager.py --repo-owner myorg --repo-name myrepo --dry-run
***** DRY RUN MODE - No changes will be pushed *****
Found 2 open PR(s) to process
...
Total processed: 2
Merged: 1
Conflicts: 1

# 2. Looks good, run for real
$ export GITHUB_TOKEN=ghp_xxxxx
$ python pr_manager.py --repo-owner myorg --repo-name myrepo
Found 2 open PR(s) to process
✓ PR #15: Feature XYZ successfully merged and deleted
✗ PR #16: Refactor has conflicts, created conflicts/refactor

# 3. Handle conflicts
$ git checkout conflicts/refactor
$ cat CONFLICTS_refactor.md
# ... resolve conflicts ...
$ git commit -am "Resolve conflicts"
$ git push origin conflicts/refactor

# Done!
```

That's it! You're now managing PRs automatically. 🚀
