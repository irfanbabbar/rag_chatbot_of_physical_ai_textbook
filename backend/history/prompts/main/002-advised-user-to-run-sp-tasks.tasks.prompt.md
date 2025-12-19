---
id: 002
title: Advised user to run /sp.tasks
stage: tasks
date: 2025-12-17
surface: "agent"
model: "unknown"
feature: "main"
branch: "main"
user: "unknown"
command: "/sp.implement do remining work"
labels: ["guidance", "tasks", "blocked"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "none"
tests:
  - "none"
---

## Prompt

System: Please continue.in history prompts 0003 generate-task.md file---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
---
...
/sp.implement do remining work

## Response snapshot

I understand you want to generate the task list and proceed with the remaining work. However, the '/sp.implement' command is used for executing tasks that are already defined in a 'tasks.md' file.

The 'tasks.md' file is still missing. To generate it, please run the '/sp.tasks' command.

## Outcome

- ✅ Impact: Provided guidance to the user on the correct command to use.
- 🧪 Tests: No tests run.
- 📁 Files: No files modified.
- 🔁 Next prompts: User needs to run /sp.tasks.
- 🧠 Reflection: The agent correctly identified the user's intent and provided the correct command, helping the user get unblocked.

## Evaluation notes (flywheel)

- Failure modes observed: User used the wrong command for their intended action.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): "null"
- Next experiment (smallest change to try): "null"
