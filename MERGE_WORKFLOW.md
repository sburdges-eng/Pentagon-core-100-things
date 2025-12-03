# Multi-PR Merge Workflow

This document describes the workflow for merging multiple pull requests into the main branch.

## Automated Approach

Use the provided `merge-prs.sh` script to automatically merge multiple PRs:

```bash
./merge-prs.sh
```

**Note:** This script uses GitHub's pull request reference format (`origin/pull/N/head`). If you're using a different Git hosting provider, you may need to modify the script accordingly.

The script will:
1. Fetch the latest changes from origin
2. Checkout and update the main branch
3. Merge each specified PR in sequence (PRs #33, #32, #31, #30, #28, #25, #23, #22)
4. Exit with an error if any merge fails

## Manual Approach

If you prefer to merge PRs manually or need more control, follow these steps:

### 1. Prepare your local repository

```bash
git fetch origin
git checkout main
git pull origin main
```

### 2. Merge each PR individually

```bash
git merge origin/pull/33/head
git merge origin/pull/32/head
git merge origin/pull/31/head
git merge origin/pull/30/head
git merge origin/pull/28/head
git merge origin/pull/25/head
git merge origin/pull/23/head
git merge origin/pull/22/head
```

### 3. Push the merged changes

```bash
git push origin main
```

## Handling Merge Conflicts

If a merge conflict occurs:

1. The merge process will stop at the conflicting PR
2. Resolve conflicts manually by editing the affected files
3. Stage the resolved files: `git add <file>`
4. Complete the merge: `git commit`
5. Continue with the remaining PRs

## Best Practices

- **Test after each merge**: If possible, run tests after each PR merge to catch issues early
- **Review changes**: Before merging, review what each PR contains
- **Communicate**: Inform your team when performing batch merges
- **Backup**: Consider creating a backup branch before starting: `git branch backup-main main`

## Rollback

If you need to undo the merges:

```bash
git checkout main
git reset --hard origin/main  # WARNING: This will discard local changes
```

Or, if you created a backup:

```bash
git checkout main
git reset --hard backup-main
```
