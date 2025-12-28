# PR Manager - Test Scenarios

This document describes test scenarios for the PR Manager tool and demonstrates its behavior with different types of pull requests.

## Scenario 1: Clean Merge (No Conflicts)

**Setup:**
- Branch: `feature/simple-addition`
- Base: `main`
- Changes: Adds a new file or modifies a file that hasn't been changed in main

**Expected Behavior:**
```
Testing merge of feature/simple-addition into main...
✓ PR #123 can be merged without conflicts
Merging feature/simple-addition into main...
✓ Successfully merged feature/simple-addition into main
Deleting branch feature/simple-addition...
✓ Successfully deleted branch feature/simple-addition
```

**Result:**
- PR is merged into main
- Branch `feature/simple-addition` is deleted
- PR is automatically closed (if using GitHub API)

## Scenario 2: Merge Conflicts

**Setup:**
- Branch: `feature/conflicting-change`
- Base: `main`
- Changes: Modifies the same lines in a file that were also changed in main

**Expected Behavior:**
```
Testing merge of feature/conflicting-change into main...
✗ PR #124 has merge conflicts
Conflicting files: src/app.py, README.md

Creating conflicts branch: conflicts/feature/conflicting-change
✓ Successfully created conflicts branch: conflicts/feature/conflicting-change
✓ Added comment to PR #124 about conflicts
```

**Result:**
- New branch created: `conflicts/feature/conflicting-change`
- Documentation file created: `CONFLICTS_feature_conflicting-change.md`
- Comment added to PR listing conflicting files:
  - `src/app.py`
  - `README.md`
- Original PR remains open
- Developer can review conflicts branch and resolve manually

## Scenario 3: Multiple PRs

**Setup:**
- 3 open PRs with various states

**Expected Behavior:**
```
Found 3 open PR(s) to process

Processing PR #120: Feature A
✓ Successfully merged and deleted

Processing PR #121: Feature B  
✗ Conflicts detected, conflicts branch created

Processing PR #122: Feature C
✓ Successfully merged and deleted

============================================================
PR PROCESSING SUMMARY
============================================================

✓ Successfully Merged and Deleted:
  - PR #120: Feature A
    Branch: feature-a
  - PR #122: Feature C
    Branch: feature-c

✗ Moved to Conflicts Branch:
  - PR #121: Feature B
    Branch: feature-b -> conflicts/feature-b
    Conflicts in: config.json

Total processed: 3
Merged: 2
Conflicts: 1
```

## Scenario 4: Dry Run Mode

**Setup:**
- Use `--dry-run` flag
- Any PR state

**Expected Behavior:**
```
***** DRY RUN MODE - No changes will be pushed *****

Testing merge of feature/example into main...
✓ PR #125 can be merged without conflicts
[DRY RUN] Would merge branch (skipping)
[DRY RUN] Would delete branch (skipping)
```

**Result:**
- No actual merges performed
- No branches deleted
- No changes pushed to remote
- Useful for testing and validation

## Scenario 5: No GitHub Token

**Setup:**
- Run without `--github-token` or `GITHUB_TOKEN` env var
- GitHub API not accessible

**Expected Behavior:**
```
Warning: No GitHub token provided. Using git branches as fallback.

Found 1 open PR(s) to process
Processing PR #branch-feature/example: Branch: feature/example
Note: Skipping PR comment (no API access or PR number unavailable)
```

**Result:**
- Uses git branch analysis instead of GitHub API
- Cannot add comments to PRs
- Can still perform local git operations
- Branch names used instead of PR numbers

## Conflicts Branch Structure

When conflicts are detected, the tool creates:

### New Branch: `conflicts/original-branch-name`
Based on the original PR branch

### Documentation File: `CONFLICTS_original_branch_name.md`
Contains:
```markdown
# Merge Conflicts for original-branch-name

## Conflicting Files
The following files have conflicts when merging into the target branch:

- path/to/file1.py
- path/to/file2.js

## Resolution Instructions
1. Review the conflicting files listed above
2. Resolve conflicts manually by editing the files
3. Test your changes
4. Commit the resolved changes
5. Merge this branch or create a new PR

## Original PR Branch
This conflicts branch was created from: `original-branch-name`
```

### PR Comment (if GitHub token available):
```markdown
## Merge Conflicts Detected

This PR has merge conflicts that need to be resolved before it can be merged.

### Conflicting Files:
- `path/to/file1.py`
- `path/to/file2.js`

### Resolution:
A conflicts branch has been created: `conflicts/original-branch-name`

Please review the conflicts, resolve them, and update this PR. 
The original PR remains open for your review.
```

## Common Error Scenarios

### Authentication Error
```
Error pushing merge: fatal: Authentication failed
```
**Solution:** Ensure git credentials are configured or use SSH keys

### Protected Branch
```
Error pushing merge: remote: error: GH006: Protected branch update failed
```
**Solution:** Update branch protection rules or merge via GitHub UI

### Dirty Working Directory
```
Warning: Working directory has uncommitted changes. Stashing...
```
**Solution:** The tool automatically stashes changes and restores them after

## Running Tests

### Test Clean Merge
```bash
python pr_manager.py --dry-run
```

### Test with GitHub API
```bash
export GITHUB_TOKEN=ghp_your_token_here
python pr_manager.py
```

### Test Specific Repository
```bash
python pr_manager.py --repo-owner myorg --repo-name myrepo
```

## Best Practices

1. **Always test in dry-run mode first**
   ```bash
   python pr_manager.py --dry-run
   ```

2. **Use GitHub token for full functionality**
   - Enables PR commenting
   - Higher API rate limits
   - Access to private repositories

3. **Review the summary carefully**
   - Check which PRs were merged
   - Verify conflict reports are accurate

4. **Monitor conflicts branches**
   - Review and resolve promptly
   - Delete conflicts branches after resolution

5. **Run periodically**
   - Set up as a cron job or GitHub Action
   - Process PRs automatically on schedule

## Integration with CI/CD

Example GitHub Action:
```yaml
name: PR Manager
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  manage-prs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Run PR Manager
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python pr_manager.py
```

This automates PR management without manual intervention.
