# LeetCode Stats Auto-Update - Setup & Troubleshooting

This document contains setup instructions and troubleshooting information for the automated LeetCode statistics update workflow.

## Overview

The repository uses GitHub Actions to automatically fetch and update LeetCode statistics daily. The workflow:
- Runs daily at 00:00 UTC
- Fetches stats from LeetCode API
- Updates README.md with current statistics
- Commits and pushes changes automatically

## Workflow Files

- **Workflow**: `.github/workflows/update-leetcode-stats.yml`
- **Python Script**: `.github/scripts/update_leetcode_stats.py` (if using separate script approach)

## Common Issues & Solutions

### Issue 1: YAML Syntax Error (Line 48)

**Problem**: Python f-strings inside YAML heredoc cause parsing errors.

**Solution**: Use a separate Python script or use `.format()` instead of f-strings in heredoc.

**Fixed Approach**:
```yaml
- name: Create update script
  run: |
    cat > update_stats.py << 'SCRIPT_EOF'
    # Python code using .format() instead of f-strings
    SCRIPT_EOF

- name: Run update script
  run: python update_stats.py
```

---

### Issue 2: GitHub Actions Push Permission Denied (403 Error)

**Error Message**:
```
remote: Permission to amfooladgar/data_structure_algorithm.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/': The requested URL returned error: 403
```

**Root Cause**: The workflow lacks permission to push changes back to the repository.

**Solution**: Add permissions to the workflow file.

**Required Changes**:

1. Add `permissions` section to the job:
```yaml
jobs:
  update-stats:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # Required for pushing changes
```

2. Ensure checkout uses the token:
```yaml
- name: Checkout repository
  uses: actions/checkout@v3
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    fetch-depth: 0
```

**Complete Fixed Workflow Structure**:
```yaml
name: Update LeetCode Stats

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  update-stats:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # KEY FIX
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}  # KEY FIX
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install requests
      
      - name: Create update script
        run: |
          cat > update_stats.py << 'SCRIPT_EOF'
          # Python script content here
          SCRIPT_EOF
      
      - name: Run update script
        run: python update_stats.py
      
      - name: Commit and push if changed
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add README.md
          git diff --quiet && git diff --staged --quiet || (git commit -m "🤖 Auto-update LeetCode stats" && git push)
```

---

### Issue 3: Personal Access Token (PAT) Workflow Scope

**Problem**: Cannot push workflow files from local machine.

**Error Message**:
```
! [remote rejected] main -> main (refusing to allow a Personal Access Token to create or update workflow without `workflow` scope)
```

**Solution Options**:

**Option A**: Update PAT permissions
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Edit your token and enable the `workflow` scope
3. Update local git credentials with the new token

**Option B**: Edit workflow files via GitHub web interface
1. Navigate to the file on GitHub
2. Click the pencil icon to edit
3. Make changes and commit directly on GitHub

---

## Manual Trigger

To manually trigger the workflow:
1. Go to repository Actions tab
2. Select "Update LeetCode Stats" workflow
3. Click "Run workflow" button
4. Select branch (main) and click "Run workflow"

---

## Verification

After fixing issues, verify the workflow:
1. Check the Actions tab for successful runs
2. Verify README.md is updated with latest stats
3. Check commit history for automated commits from `github-actions[bot]`

---

## API Information

**LeetCode Stats API**: `https://leetcode-stats-api.herokuapp.com/amfooladgar`

**Returns**:
- Total problems solved
- Problems by difficulty (easy, medium, hard)
- Acceptance rate
- Ranking
- Contribution points
- Submission calendar

---

## Maintenance Notes

- The workflow runs daily at 00:00 UTC
- Stats are fetched from a third-party API (not official LeetCode API)
- If the API changes or becomes unavailable, the workflow will fail
- Check Actions tab regularly for any failures
- README.md markers: `<!-- LEETCODE_STATS:START -->` and `<!-- LEETCODE_STATS:END -->`

---

*Last Updated: 2025-11-21*
