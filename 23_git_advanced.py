#!/usr/bin/env python3
"""
Advanced Git Operations - Script 23
Why: Git expertise is fundamental for DevOps workflows and collaboration
"""

import subprocess
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class GitRepositoryManager:
    def __init__(self, repo_path: str = '.'):
        self.repo_path = repo_path
    
    def run_git_command(self, command: List[str]) -> Tuple[bool, str]:
        """Execute git command and return success status and output"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()
    
    def create_feature_branch(self, branch_name: str, base_branch: str = 'main') -> Dict:
        """
        Create feature branch following GitFlow conventions
        Why: Interview question - How do you manage branching strategies?
        """
        commands = [
            ['checkout', base_branch],
            ['pull', 'origin', base_branch],
            ['checkout', '-b', f'feature/{branch_name}'],
            ['push', '-u', 'origin', f'feature/{branch_name}']
        ]
        
        results = []
        for cmd in commands:
            success, output = self.run_git_command(cmd)
            results.append({'command': ' '.join(cmd), 'success': success, 'output': output})
            if not success:
                break
        
        return {'branch_created': f'feature/{branch_name}', 'steps': results}
    
    def create_release_branch(self, version: str) -> Dict:
        """
        Create release branch with version tagging
        Why: Interview question - How do you handle release management?
        """
        release_branch = f'release/{version}'
        
        # Create release branch
        success, output = self.run_git_command(['checkout', '-b', release_branch, 'develop'])
        if not success:
            return {'error': f'Failed to create release branch: {output}'}
        
        # Update version files (example)
        version_updates = self.update_version_files(version)
        
        # Commit version updates
        self.run_git_command(['add', '.'])
        self.run_git_command(['commit', '-m', f'Bump version to {version}'])
        
        # Push release branch
        self.run_git_command(['push', '-u', 'origin', release_branch])
        
        return {
            'release_branch': release_branch,
            'version': version,
            'version_updates': version_updates
        }
    
    def merge_with_strategy(self, source_branch: str, target_branch: str, 
                          strategy: str = 'merge') -> Dict:
        """
        Merge branches with different strategies
        Why: Interview question - Explain different merge strategies
        """
        # Checkout target branch
        self.run_git_command(['checkout', target_branch])
        self.run_git_command(['pull', 'origin', target_branch])
        
        if strategy == 'merge':
            # Create merge commit
            success, output = self.run_git_command(['merge', '--no-ff', source_branch])
        elif strategy == 'squash':
            # Squash merge
            success, output = self.run_git_command(['merge', '--squash', source_branch])
            if success:
                self.run_git_command(['commit', '-m', f'Squash merge {source_branch}'])
        elif strategy == 'rebase':
            # Rebase and merge
            self.run_git_command(['checkout', source_branch])
            success, output = self.run_git_command(['rebase', target_branch])
            if success:
                self.run_git_command(['checkout', target_branch])
                success, output = self.run_git_command(['merge', source_branch])
        
        return {
            'strategy': strategy,
            'success': success,
            'output': output,
            'merged_branch': source_branch,
            'target_branch': target_branch
        }
    
    def analyze_commit_history(self, since_days: int = 30) -> Dict:
        """
        Analyze commit history for insights
        Why: Interview question - How do you analyze development patterns?
        """
        since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d')
        
        # Get commit statistics
        success, commits_output = self.run_git_command([
            'log', '--since', since_date, '--pretty=format:%H|%an|%ae|%ad|%s', '--date=iso'
        ])
        
        if not success:
            return {'error': 'Failed to get commit history'}
        
        commits = []
        authors = {}
        commit_patterns = {'feat': 0, 'fix': 0, 'docs': 0, 'refactor': 0, 'test': 0}
        
        for line in commits_output.split('\n'):
            if not line:
                continue
            
            parts = line.split('|')
            if len(parts) >= 5:
                commit_hash, author, email, date, message = parts
                commits.append({
                    'hash': commit_hash,
                    'author': author,
                    'email': email,
                    'date': date,
                    'message': message
                })
                
                # Count commits per author
                authors[author] = authors.get(author, 0) + 1
                
                # Analyze commit message patterns
                for pattern in commit_patterns:
                    if message.lower().startswith(pattern):
                        commit_patterns[pattern] += 1
        
        # Get file change statistics
        success, stats_output = self.run_git_command([
            'log', '--since', since_date, '--numstat', '--pretty=format:'
        ])
        
        file_changes = {}
        if success:
            for line in stats_output.split('\n'):
                if line and '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        additions, deletions, filename = parts
                        if additions.isdigit() and deletions.isdigit():
                            file_changes[filename] = {
                                'additions': int(additions),
                                'deletions': int(deletions)
                            }
        
        return {
            'period_days': since_days,
            'total_commits': len(commits),
            'authors': authors,
            'commit_patterns': commit_patterns,
            'most_changed_files': sorted(
                file_changes.items(),
                key=lambda x: x[1]['additions'] + x[1]['deletions'],
                reverse=True
            )[:10]
        }
    
    def setup_git_hooks(self) -> Dict:
        """
        Setup Git hooks for quality control
        Why: Interview question - How do you enforce code quality?
        """
        hooks = {
            'pre-commit': '''#!/bin/bash
# Pre-commit hook for code quality checks
set -e

echo "Running pre-commit checks..."

# Check for Python syntax errors
if git diff --cached --name-only | grep -q "\.py$"; then
    echo "Checking Python syntax..."
    python -m py_compile $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$")
fi

# Check for large files
git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        if [ $size -gt 10485760 ]; then  # 10MB
            echo "Error: File $file is larger than 10MB"
            exit 1
        fi
    fi
done

# Check for secrets
if git diff --cached | grep -E "(password|secret|key|token)" -i; then
    echo "Warning: Potential secrets detected in commit"
    echo "Please review and remove any sensitive information"
    exit 1
fi

echo "Pre-commit checks passed!"
''',
            'commit-msg': '''#!/bin/bash
# Commit message validation
commit_regex='^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "Invalid commit message format!"
    echo "Format: type(scope): description"
    echo "Types: feat, fix, docs, style, refactor, test, chore"
    echo "Example: feat(auth): add user authentication"
    exit 1
fi
''',
            'pre-push': '''#!/bin/bash
# Pre-push hook for additional checks
protected_branch='main'
current_branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

if [ $protected_branch = $current_branch ]; then
    echo "Direct push to $protected_branch branch is not allowed"
    echo "Please create a pull request instead"
    exit 1
fi

# Run tests before push
if [ -f "requirements.txt" ]; then
    echo "Running tests..."
    python -m pytest tests/ || exit 1
fi

echo "Pre-push checks passed!"
'''
        }
        
        hooks_dir = f"{self.repo_path}/.git/hooks"
        installed_hooks = []
        
        for hook_name, hook_content in hooks.items():
            hook_path = f"{hooks_dir}/{hook_name}"
            try:
                with open(hook_path, 'w') as f:
                    f.write(hook_content)
                
                # Make executable
                subprocess.run(['chmod', '+x', hook_path], check=True)
                installed_hooks.append(hook_name)
                
            except Exception as e:
                return {'error': f'Failed to install {hook_name}: {e}'}
        
        return {'installed_hooks': installed_hooks}
    
    def create_conventional_commit(self, commit_type: str, scope: str, 
                                 description: str, breaking: bool = False) -> Dict:
        """
        Create conventional commit message
        Why: Interview question - How do you standardize commit messages?
        """
        # Validate commit type
        valid_types = ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']
        if commit_type not in valid_types:
            return {'error': f'Invalid commit type. Use: {", ".join(valid_types)}'}
        
        # Build commit message
        message = f"{commit_type}"
        if scope:
            message += f"({scope})"
        
        if breaking:
            message += "!"
        
        message += f": {description}"
        
        # Add breaking change footer if needed
        if breaking:
            message += "\n\nBREAKING CHANGE: " + description
        
        # Create commit
        success, output = self.run_git_command(['commit', '-m', message])
        
        return {
            'success': success,
            'message': message,
            'output': output
        }
    
    def setup_gitflow_workflow(self) -> Dict:
        """
        Initialize GitFlow workflow
        Why: Interview question - How do you structure branching strategies?
        """
        # Initialize git flow
        gitflow_config = {
            'master': 'main',
            'develop': 'develop',
            'feature': 'feature/',
            'release': 'release/',
            'hotfix': 'hotfix/',
            'support': 'support/'
        }
        
        # Create develop branch if it doesn't exist
        success, output = self.run_git_command(['checkout', '-b', 'develop'])
        if not success and 'already exists' not in output:
            return {'error': f'Failed to create develop branch: {output}'}
        
        # Push develop branch
        self.run_git_command(['push', '-u', 'origin', 'develop'])
        
        # Set up branch protection (would typically be done via API)
        protection_rules = {
            'main': {
                'require_pull_request': True,
                'require_status_checks': True,
                'require_up_to_date': True,
                'dismiss_stale_reviews': True
            },
            'develop': {
                'require_pull_request': True,
                'require_status_checks': True
            }
        }
        
        return {
            'gitflow_initialized': True,
            'config': gitflow_config,
            'protection_rules': protection_rules
        }
    
    def update_version_files(self, version: str) -> List[str]:
        """Update version in common files"""
        version_files = []
        
        # Common version file patterns
        patterns = [
            ('package.json', r'"version":\s*"[^"]*"', f'"version": "{version}"'),
            ('setup.py', r'version\s*=\s*["\'][^"\']*["\']', f'version="{version}"'),
            ('pyproject.toml', r'version\s*=\s*["\'][^"\']*["\']', f'version = "{version}"'),
            ('VERSION', r'.*', version),
            ('version.txt', r'.*', version)
        ]
        
        import os
        for filename, pattern, replacement in patterns:
            filepath = os.path.join(self.repo_path, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    updated_content = re.sub(pattern, replacement, content)
                    
                    with open(filepath, 'w') as f:
                        f.write(updated_content)
                    
                    version_files.append(filename)
                except Exception as e:
                    print(f"Failed to update {filename}: {e}")
        
        return version_files

class GitWorkflowAutomation:
    """
    Automate common Git workflows
    Why: Interview question - How do you automate development workflows?
    """
    
    def __init__(self, repo_manager: GitRepositoryManager):
        self.git = repo_manager
    
    def automated_hotfix_workflow(self, hotfix_name: str, version: str) -> Dict:
        """Automated hotfix creation and deployment"""
        steps = []
        
        # Create hotfix branch from main
        success, output = self.git.run_git_command(['checkout', 'main'])
        steps.append({'step': 'checkout_main', 'success': success})
        
        success, output = self.git.run_git_command(['pull', 'origin', 'main'])
        steps.append({'step': 'pull_main', 'success': success})
        
        hotfix_branch = f'hotfix/{hotfix_name}'
        success, output = self.git.run_git_command(['checkout', '-b', hotfix_branch])
        steps.append({'step': 'create_hotfix_branch', 'success': success})
        
        return {
            'hotfix_branch': hotfix_branch,
            'version': version,
            'steps': steps,
            'next_actions': [
                'Make necessary fixes',
                'Test thoroughly',
                'Merge to main and develop',
                'Tag release',
                'Deploy to production'
            ]
        }
    
    def automated_release_workflow(self, version: str) -> Dict:
        """Automated release preparation"""
        release_branch = f'release/{version}'
        
        # Create release branch
        result = self.git.create_release_branch(version)
        
        # Generate changelog
        changelog = self.generate_changelog(version)
        
        # Create release checklist
        checklist = [
            'Code freeze implemented',
            'All tests passing',
            'Documentation updated',
            'Security scan completed',
            'Performance testing done',
            'Staging deployment successful',
            'Release notes prepared'
        ]
        
        return {
            'release_branch': release_branch,
            'version': version,
            'changelog': changelog,
            'checklist': checklist,
            'branch_creation': result
        }
    
    def generate_changelog(self, version: str) -> Dict:
        """Generate changelog from commit messages"""
        # Get commits since last tag
        success, last_tag = self.git.run_git_command(['describe', '--tags', '--abbrev=0'])
        
        if success:
            success, commits = self.git.run_git_command([
                'log', f'{last_tag}..HEAD', '--pretty=format:%s'
            ])
        else:
            success, commits = self.git.run_git_command([
                'log', '--pretty=format:%s'
            ])
        
        if not success:
            return {'error': 'Failed to generate changelog'}
        
        # Categorize commits
        categories = {
            'Features': [],
            'Bug Fixes': [],
            'Documentation': [],
            'Refactoring': [],
            'Tests': [],
            'Other': []
        }
        
        for commit in commits.split('\n'):
            if commit.startswith('feat'):
                categories['Features'].append(commit)
            elif commit.startswith('fix'):
                categories['Bug Fixes'].append(commit)
            elif commit.startswith('docs'):
                categories['Documentation'].append(commit)
            elif commit.startswith('refactor'):
                categories['Refactoring'].append(commit)
            elif commit.startswith('test'):
                categories['Tests'].append(commit)
            else:
                categories['Other'].append(commit)
        
        return {
            'version': version,
            'categories': categories,
            'total_commits': len(commits.split('\n')) if commits else 0
        }

if __name__ == "__main__":
    # Example usage for interview demonstration
    git_manager = GitRepositoryManager()
    workflow = GitWorkflowAutomation(git_manager)
    
    print("Git Advanced Operations - Interview Ready!")
    print("Key concepts: GitFlow, Conventional Commits, Automation, Hooks")