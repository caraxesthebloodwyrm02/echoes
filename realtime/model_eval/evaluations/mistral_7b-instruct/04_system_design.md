# 04 System Design

## Model: mistral:7b-instruct

## Prompt

```
# System Design: Versioning System

Design a versioning system for JSON documents that supports offline editing. Include:

1. Data structures for storing document versions
2. Algorithm for generating version identifiers
3. Approach to handling concurrent edits
4. Method for three-way merge during sync
5. Conflict detection and resolution strategy

Provide pseudo-code or Python examples for key operations.

```

## Response

For this system, I'll design a versioning system using Git's approach as a reference. Let's call the JSON documents "commits," and each commit will have its own unique identifier (hash). This system will store commits in a directed acyclic graph (DAG) where each node represents a commit, and edges represent the parent-child relationship between commits.

1. Data structures for storing document versions:
   A dictionary called `commit_graph` to store all commits as keys with their parents as values in a list.
   ```python
   commit_graph = {}
   ```

2. Algorithm for generating version identifiers (hashes):
   Use a secure hash algorithm like SHA-256 to generate unique identifiers (hashes) for each commit.
   ```python
   import hashlib

   def hash_commit(content):
       return hashlib.sha256(content.encode()).hexdigest()
   ```

3. Approach to handling concurrent edits:
   To handle concurrent edits, use the last-writer-wins approach: save the most recent commit (the one with the latest timestamp) and discard any conflicting commits.
   ```python
   from datetime import datetime

   def create_commit(content, parent_hashes):
       timestamp = datetime.now()
       hash = hash_commit(content)
       commit = {
           'content': content,
           'parent_hashes': parent_hashes,
           'timestamp': timestamp
       }
       commit_graph[hash] = commit
       return hash
   ```

4. Method for three-way merge during sync:
   Implement a three-way merge algorithm to resolve conflicts between remote and local versions of the same document during sync. This method can use external libraries like `pydiff` or roll its own logic using string comparison functions.
   ```python
   from pydiff import unified_diff

   def merge(local, remote, base):
       # Implement your three-way merge logic here, for simplicity, this example uses a naive approach
       merged = local if base == remote else remote
       differences = unified_diff(base.splitlines(), local.splitlines())
       for difference in differences:
           if difference[0] == '-':
               merged = merged.replace(difference[1], '')
           elif difference[0] == '+':
               merged = merged.replace(difference[2], difference[1])
       return merged
   ```

5. Conflict detection and resolution strategy:
   When syncing, check for conflicts by comparing the base (remote commit) and local commits using your preferred conflict detection algorithm. If a conflict is detected, prompt the user to resolve it manually and save the merged result as a new commit.
   ```python
   def sync():
       # Fetch remote commits from a server or other storage
       base = fetch_remote_commit()
       local_hash = ... # Get the current local commit hash
       local = commit_graph[local_hash]['content']

       if local != base:
           conflicts, merged = detect_conflicts(base, local)

           if conflicts:
               # User should resolve conflicts and provide a resolved version of the document
               user_resolution = get_user_resolution(conflicts)
               merged += user_resolution

           create_commit(merged, [base_hash])
   ```