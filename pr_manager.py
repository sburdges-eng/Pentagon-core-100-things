#!/usr/bin/env python3
"""
PR Management Agent

This script manages open pull requests by:
1. Fetching all open PRs
2. Attempting to merge each PR into its target branch
3. For successful merges: completing the merge and deleting the source branch
4. For conflicts: creating a conflicts branch and documenting the issues

Usage:
    python pr_manager.py --repo-owner <owner> --repo-name <name> [--github-token <token>]
    
Note: This script requires git to be configured with push access to the repository.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class PRManager:
    def __init__(self, repo_owner: str, repo_name: str, github_token: Optional[str] = None, dry_run: bool = False):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token or os.environ.get('GITHUB_TOKEN')
        self.repo_path = Path.cwd()
        self.merged_prs = []
        self.conflicted_prs = []
        self.api_base = 'https://api.github.com'
        self.dry_run = dry_run
        
    def run_git_command(self, command: List[str], check=True) -> Tuple[int, str, str]:
        """Run a git command and return the result."""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
    
    def github_api_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to the GitHub API."""
        url = f"{self.api_base}{endpoint}"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        request_data = None
        if data:
            request_data = json.dumps(data).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        
        req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"GitHub API error: {e.code} - {e.reason}")
            return None
        except Exception as e:
            print(f"Error making API request: {e}")
            return None
    
    def get_open_prs(self) -> List[Dict]:
        """Fetch open pull requests from GitHub API."""
        if not self.github_token:
            print("Warning: No GitHub token provided. Using git branches as fallback.")
            return self._get_prs_from_branches()
        
        endpoint = f"/repos/{self.repo_owner}/{self.repo_name}/pulls"
        params = "?state=open&per_page=100"
        prs = self.github_api_request(endpoint + params)
        
        if prs is None:
            print("Warning: GitHub API request failed. Using git branches as fallback.")
            return self._get_prs_from_branches()
        
        return prs if prs else []
    
    def _get_prs_from_branches(self) -> List[Dict]:
        """Fallback: Get PRs by examining git branches."""
        default_branch = self.get_default_branch()
        returncode, stdout, stderr = self.run_git_command(
            ['git', 'branch', '-r', '--no-merged', f'{default_branch}']
        )
        
        if returncode != 0:
            print(f"Error getting branches: {stderr}")
            return []
        
        prs = []
        for line in stdout.strip().split('\n'):
            if not line.strip() or 'origin/HEAD' in line:
                continue
            
            branch_name = line.strip().replace('origin/', '')
            # Skip the default branch, HEAD, and conflicts branches
            if (branch_name == default_branch or 
                branch_name.startswith('conflicts/') or
                'HEAD' in branch_name):
                continue
            
            prs.append({
                'number': f"branch-{branch_name}",
                'head': {'ref': branch_name},
                'base': {'ref': default_branch},
                'title': f"Branch: {branch_name}"
            })
        
        return prs
    
    def add_pr_comment(self, pr_number: int, comment: str) -> bool:
        """Add a comment to a pull request."""
        endpoint = f"/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/comments"
        data = {'body': comment}
        result = self.github_api_request(endpoint, method='POST', data=data)
        return result is not None
    
    def fetch_all_branches(self):
        """Fetch all branches from remote."""
        print("Fetching all branches from remote...")
        returncode, stdout, stderr = self.run_git_command(['git', 'fetch', '--all', '--prune'])
        if returncode != 0:
            print(f"Warning: Failed to fetch branches: {stderr}")
        return returncode == 0
    
    def get_default_branch(self) -> str:
        """Get the default branch from GitHub API or git."""
        # Try GitHub API first
        if self.github_token:
            endpoint = f"/repos/{self.repo_owner}/{self.repo_name}"
            repo_info = self.github_api_request(endpoint)
            if repo_info and 'default_branch' in repo_info:
                return repo_info['default_branch']
        
        # Fallback to git
        returncode, stdout, stderr = self.run_git_command(
            ['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'],
            check=False
        )
        if returncode == 0:
            default_branch = stdout.strip().replace('refs/remotes/origin/', '')
            return default_branch
        
        # Check if main or master exists
        for branch in ['main', 'master']:
            returncode, _, _ = self.run_git_command(
                ['git', 'rev-parse', '--verify', f'origin/{branch}'],
                check=False
            )
            if returncode == 0:
                return branch
        
        return 'main'  # Default fallback
    
    def test_merge(self, pr_branch: str, target_branch: str) -> Tuple[bool, List[str]]:
        """
        Test if a PR branch can be merged into target branch.
        Returns (success, list_of_conflicted_files)
        """
        print(f"\nTesting merge of {pr_branch} into {target_branch}...")
        
        # Check if working directory is clean
        returncode, stdout, _ = self.run_git_command(['git', 'status', '--porcelain'])
        if stdout.strip():
            print(f"Warning: Working directory has uncommitted changes. Stashing...")
            self.run_git_command(['git', 'stash', 'push', '-m', 'PR manager auto-stash'])
            stashed = True
        else:
            stashed = False
        
        # Save current branch
        returncode, current_branch, _ = self.run_git_command(['git', 'branch', '--show-current'])
        current_branch = current_branch.strip()
        
        try:
            # Checkout target branch
            returncode, _, stderr = self.run_git_command(['git', 'checkout', target_branch])
            if returncode != 0:
                print(f"Error checking out {target_branch}: {stderr}")
                return False, []
            
            # Update target branch
            returncode, _, _ = self.run_git_command(['git', 'pull', 'origin', target_branch], check=False)
            
            # Attempt merge with no-commit flag to test
            returncode, stdout, stderr = self.run_git_command(
                ['git', 'merge', '--no-commit', '--no-ff', f'origin/{pr_branch}'],
                check=False
            )
            
            if returncode == 0:
                # Merge successful - abort it for now
                self.run_git_command(['git', 'merge', '--abort'], check=False)
                return True, []
            else:
                # Check for conflicts
                conflicted_files = []
                returncode, stdout, _ = self.run_git_command(
                    ['git', 'diff', '--name-only', '--diff-filter=U'],
                    check=False
                )
                if stdout.strip():
                    conflicted_files = stdout.strip().split('\n')
                
                # Abort the merge attempt
                self.run_git_command(['git', 'merge', '--abort'], check=False)
                
                return False, conflicted_files
                
        finally:
            # Return to original branch
            if current_branch:
                self.run_git_command(['git', 'checkout', current_branch], check=False)
            
            # Restore stashed changes
            if stashed:
                self.run_git_command(['git', 'stash', 'pop'], check=False)
    
    def perform_merge(self, pr_branch: str, target_branch: str, pr_number: Optional[int] = None) -> bool:
        """
        Perform the actual merge of a PR branch into target branch.
        """
        print(f"\nMerging {pr_branch} into {target_branch}...")
        
        if self.dry_run:
            print("[DRY RUN] Would merge branch (skipping)")
            return True
        
        # Checkout target branch
        returncode, _, stderr = self.run_git_command(['git', 'checkout', target_branch])
        if returncode != 0:
            print(f"Error checking out {target_branch}: {stderr}")
            return False
        
        # Update target branch
        self.run_git_command(['git', 'pull', 'origin', target_branch])
        
        # Perform merge
        pr_title = f"PR #{pr_number}" if pr_number else pr_branch
        returncode, _, stderr = self.run_git_command(
            ['git', 'merge', '--no-ff', f'origin/{pr_branch}', 
             '-m', f'Merge {pr_title} into {target_branch}']
        )
        
        if returncode != 0:
            print(f"Error during merge: {stderr}")
            return False
        
        # Push the merge
        returncode, _, stderr = self.run_git_command(['git', 'push', 'origin', target_branch])
        if returncode != 0:
            print(f"Error pushing merge: {stderr}")
            # Try to undo the merge
            self.run_git_command(['git', 'reset', '--hard', 'HEAD~1'], check=False)
            return False
        
        print(f"✓ Successfully merged {pr_branch} into {target_branch}")
        return True
    
    def delete_branch(self, branch_name: str) -> bool:
        """Delete a branch both locally and remotely."""
        print(f"Deleting branch {branch_name}...")
        
        if self.dry_run:
            print("[DRY RUN] Would delete branch (skipping)")
            return True
        
        # Delete local branch if it exists
        self.run_git_command(['git', 'branch', '-D', branch_name], check=False)
        
        # Delete remote branch
        returncode, _, stderr = self.run_git_command(
            ['git', 'push', 'origin', '--delete', branch_name],
            check=False
        )
        
        if returncode != 0:
            print(f"Warning: Could not delete remote branch: {stderr}")
            return False
        
        print(f"✓ Successfully deleted branch {branch_name}")
        return True
    
    def create_conflicts_branch(self, pr_branch: str, conflicted_files: List[str]) -> bool:
        """
        Create a conflicts branch with the conflicting state.
        """
        conflicts_branch = f"conflicts/{pr_branch}"
        print(f"\nCreating conflicts branch: {conflicts_branch}")
        
        if self.dry_run:
            print("[DRY RUN] Would create conflicts branch (skipping)")
            return True
        
        # Create and checkout new conflicts branch from the PR branch
        returncode, _, stderr = self.run_git_command(
            ['git', 'checkout', '-b', conflicts_branch, f'origin/{pr_branch}']
        )
        
        if returncode != 0:
            print(f"Error creating conflicts branch: {stderr}")
            return False
        
        # Create a conflicts documentation file
        conflicts_doc = f"CONFLICTS_{pr_branch.replace('/', '_')}.md"
        conflicts_content = f"""# Merge Conflicts for {pr_branch}

## Conflicting Files
The following files have conflicts when merging into the target branch:

"""
        for file in conflicted_files:
            conflicts_content += f"- {file}\n"
        
        conflicts_content += """
## Resolution Instructions
1. Review the conflicting files listed above
2. Resolve conflicts manually by editing the files
3. Test your changes
4. Commit the resolved changes
5. Merge this branch or create a new PR

## Original PR Branch
This conflicts branch was created from: `{}`
""".format(pr_branch)
        
        conflicts_file_path = self.repo_path / conflicts_doc
        conflicts_file_path.write_text(conflicts_content)
        
        # Commit the conflicts documentation
        self.run_git_command(['git', 'add', conflicts_doc])
        self.run_git_command(
            ['git', 'commit', '-m', f'Document conflicts for {pr_branch}']
        )
        
        # Push the conflicts branch
        returncode, _, stderr = self.run_git_command(
            ['git', 'push', 'origin', conflicts_branch]
        )
        
        if returncode != 0:
            print(f"Error pushing conflicts branch: {stderr}")
            return False
        
        print(f"✓ Successfully created conflicts branch: {conflicts_branch}")
        return True
    
    def process_pr(self, pr: Dict):
        """Process a single PR."""
        pr_number = pr.get('number', 'N/A')
        pr_branch = pr['head']['ref']
        target_branch = pr['base']['ref']
        pr_title = pr.get('title', pr_branch)
        
        print(f"\n{'='*60}")
        print(f"Processing PR #{pr_number}: {pr_title}")
        print(f"Branch: {pr_branch} -> {target_branch}")
        print(f"{'='*60}")
        
        # Test if merge is possible
        can_merge, conflicted_files = self.test_merge(pr_branch, target_branch)
        
        if can_merge:
            print(f"✓ PR #{pr_number} can be merged without conflicts")
            
            # Perform the merge
            if self.perform_merge(pr_branch, target_branch, pr_number):
                # Delete the source branch
                if self.delete_branch(pr_branch):
                    self.merged_prs.append({
                        'number': pr_number,
                        'branch': pr_branch,
                        'title': pr_title
                    })
                    print(f"✓ PR #{pr_number} successfully merged and deleted")
                else:
                    print(f"✓ PR #{pr_number} merged but branch deletion failed")
                    self.merged_prs.append({
                        'number': pr_number,
                        'branch': pr_branch,
                        'title': pr_title,
                        'warning': 'Branch not deleted'
                    })
        else:
            print(f"✗ PR #{pr_number} has merge conflicts")
            print(f"Conflicting files: {', '.join(conflicted_files)}")
            
            # Create conflicts branch
            conflicts_branch = f'conflicts/{pr_branch}'
            if self.create_conflicts_branch(pr_branch, conflicted_files):
                self.conflicted_prs.append({
                    'number': pr_number,
                    'branch': pr_branch,
                    'title': pr_title,
                    'conflicts': conflicted_files,
                    'conflicts_branch': conflicts_branch
                })
                
                # Add comment to PR about conflicts
                if pr_number != 'N/A' and isinstance(pr_number, int):
                    comment = f"""## Merge Conflicts Detected

This PR has merge conflicts that need to be resolved before it can be merged.

### Conflicting Files:
{chr(10).join(f'- `{file}`' for file in conflicted_files)}

### Resolution:
A conflicts branch has been created: `{conflicts_branch}`

Please review the conflicts, resolve them, and update this PR. The original PR remains open for your review.
"""
                    if self.add_pr_comment(pr_number, comment):
                        print(f"✓ Added comment to PR #{pr_number} about conflicts")
                    else:
                        print(f"✗ Failed to add comment to PR #{pr_number}")
                elif not isinstance(pr_number, int):
                    print(f"Note: Skipping PR comment (no API access or PR number unavailable)")
                
                print(f"✓ Created conflicts branch for PR #{pr_number}")
            else:
                print(f"✗ Failed to create conflicts branch for PR #{pr_number}")
    
    def print_summary(self):
        """Print a summary of all processed PRs."""
        print("\n" + "="*60)
        print("PR PROCESSING SUMMARY")
        print("="*60)
        
        print("\n✓ Successfully Merged and Deleted:")
        if self.merged_prs:
            for pr in self.merged_prs:
                warning = f" (Warning: {pr['warning']})" if 'warning' in pr else ""
                print(f"  - PR #{pr['number']}: {pr['title']}")
                print(f"    Branch: {pr['branch']}{warning}")
        else:
            print("  (none)")
        
        print("\n✗ Moved to Conflicts Branch:")
        if self.conflicted_prs:
            for pr in self.conflicted_prs:
                print(f"  - PR #{pr['number']}: {pr['title']}")
                print(f"    Branch: {pr['branch']} -> {pr['conflicts_branch']}")
                print(f"    Conflicts in: {', '.join(pr['conflicts'])}")
        else:
            print("  (none)")
        
        print("\n" + "="*60)
        print(f"Total processed: {len(self.merged_prs) + len(self.conflicted_prs)}")
        print(f"Merged: {len(self.merged_prs)}")
        print(f"Conflicts: {len(self.conflicted_prs)}")
        print("="*60)
    
    def run(self):
        """Main execution flow."""
        print("PR Management Agent Starting...")
        if self.dry_run:
            print("***** DRY RUN MODE - No changes will be pushed *****")
        print(f"Repository: {self.repo_owner}/{self.repo_name}")
        
        # Check git configuration
        returncode, stdout, _ = self.run_git_command(['git', 'config', 'user.name'], check=False)
        if returncode != 0 or not stdout.strip():
            print("Warning: Git user.name is not configured")
            # Set a default for this run
            self.run_git_command(['git', 'config', 'user.name', 'PR Manager Bot'], check=False)
        
        returncode, stdout, _ = self.run_git_command(['git', 'config', 'user.email'], check=False)
        if returncode != 0 or not stdout.strip():
            print("Warning: Git user.email is not configured")
            # Set a default for this run
            self.run_git_command(['git', 'config', 'user.email', 'pr-manager@bot.local'], check=False)
        
        # Fetch all branches
        if not self.fetch_all_branches():
            print("Warning: Failed to fetch all branches")
        
        # Get default branch
        default_branch = self.get_default_branch()
        print(f"Default branch: {default_branch}")
        
        # Get open PRs from GitHub API
        prs = self.get_open_prs()
        
        if not prs:
            print("\nNo open PRs found to process.")
            return
        
        print(f"\nFound {len(prs)} open PR(s) to process")
        
        # Process each PR
        for pr in prs:
            try:
                self.process_pr(pr)
            except Exception as e:
                print(f"Error processing PR: {e}")
                import traceback
                traceback.print_exc()
        
        # Print summary
        self.print_summary()


def main():
    parser = argparse.ArgumentParser(description='PR Management Agent')
    parser.add_argument('--repo-owner', default='sburdges-eng',
                        help='Repository owner (default: sburdges-eng)')
    parser.add_argument('--repo-name', default='Pentagon-core-100-things',
                        help='Repository name (default: Pentagon-core-100-things)')
    parser.add_argument('--github-token', 
                        help='GitHub personal access token (optional)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Test mode - analyze PRs but do not push changes')
    
    args = parser.parse_args()
    
    manager = PRManager(args.repo_owner, args.repo_name, args.github_token, args.dry_run)
    manager.run()


if __name__ == '__main__':
    main()
