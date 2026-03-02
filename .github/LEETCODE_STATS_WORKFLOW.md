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
      contents: write
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
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
          import requests
          import re
          import json
          from datetime import datetime
          
          def get_stats(username):
              url = 'https://leetcode.com/graphql/'
              query = """
              query getUserProfile($username: String!) {
                allQuestionsCount {
                  difficulty
                  count
                }
                matchedUser(username: $username) {
                  contributions {
                    points
                  }
                  profile {
                    ranking
                  }
                  submitStats {
                    acSubmissionNum {
                      difficulty
                      count
                      submissions
                    }
                    totalSubmissionNum {
                      difficulty
                      count
                      submissions
                    }
                  }
                }
              }
              """
              variables = {'username': username}
              response = requests.post(url, json={'query': query, 'variables': variables}, timeout=15)
              response.raise_for_status()
              res_data = response.json()
              if 'errors' in res_data:
                  raise Exception(f"GraphQL Errors: {res_data['errors']}")
              return res_data['data']

          try:
              data = get_stats('amfooladgar')
              matched_user = data['matchedUser']
              if not matched_user:
                  raise Exception("User not found")
              
              ac_stats = {s['difficulty']: s for s in matched_user['submitStats']['acSubmissionNum']}
              total_stats = {s['difficulty']: s for s in matched_user['submitStats']['totalSubmissionNum']}
              count_stats = {c['difficulty']: c['count'] for c in data['allQuestionsCount']}
              
              total_solved = ac_stats['All']['count']
              easy_solved = ac_stats['Easy']['count']
              # ... (rest of parsing logic)
              # ... (README update regex logic)

              with open('README.md', 'w') as f:
                  f.write(readme)
              
              print("Stats updated successfully!")
          except Exception as e:
              print(f"Error updating stats: {e}")
              exit(1)
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

### Issue 4: Unstable Third-party API (JSONDecodeError)

**Problem**: The script fails with `json.decoder.JSONDecodeError` because the external API `leetcode-stats-api.herokuapp.com` is down or returning invalid JSON.

**Solution**: Switch to the official LeetCode GraphQL API. This requires updating the Python script to send a POST request with a GraphQL query and parsing the nested response.

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

**LeetCode Official GraphQL API**: `https://leetcode.com/graphql/`

**Query**: `getUserProfile` (Fetches comprehensive user statistics)

**Fields Extracted**:
- Total questions count by difficulty
- Problems solved (Easy, Medium, Hard, All)
- Submission stats (used for acceptance rate calculation)
- Global Ranking
- Contribution Points

---

## Maintenance Notes

- The workflow runs daily at 00:00 UTC
- Stats are fetched from the **official LeetCode GraphQL API**
- The script uses `requests.post` to interact with the GraphQL endpoint
- README.md markers: `<!-- LEETCODE_STATS:START -->` and `<!-- LEETCODE_STATS:END -->`

---

*Last Updated: 2026-03-02*
