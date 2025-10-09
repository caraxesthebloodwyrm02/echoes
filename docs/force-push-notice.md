Subject: Repository history rewritten — please re-clone

Hi team,

Important: the repository history has been rewritten to remove sensitive data (committed .env). To avoid merge problems and accidental re-introduction of the removed secret, please re-clone the repository and discard any local branches that haven't been pushed.

Steps to follow (fast, safe):

1. Backup any uncommitted work you care about (copy files or create a patch):
   - git diff > ~/my-changes.patch

2. Remove your local clone and re-clone (recommended):
   - Close your editor/IDE
   - Remove the old clone: rm -rf /path/to/old/clone
   - Re-clone: git clone <REPO_URL>

3. Re-apply local changes if needed:
   - git apply ~/my-changes.patch

Notes:
- If you must preserve branches, rebase them onto the new main, but expect conflicts.
- If you use CI tokens or deploy keys, rotate them if they were referenced in the removed files.

If you need help, ping me in Slack or open an issue and I will assist.

Thanks
