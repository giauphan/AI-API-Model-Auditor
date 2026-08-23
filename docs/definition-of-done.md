# Definition of Done

This document outlines the criteria for a task to be considered "Done" within the AI-API-Model-Auditor project, specifically aligning with Big Plan sections 69-70.

## Implementation Rules
1. **Typed and Documented Interfaces:** Keep the public interfaces typed and documented.
2. **Strict Scope:** Do not silently expand scope into another task.
3. **No Sibling Interference:** Do not modify sibling-owned files unless a small, documented interface change is required.
4. **Focused Testing:** Add focused tests for the behavior introduced in the task.
5. **Safety Controls Maintained:** Preserve secret redaction, bounded cost/concurrency, and evidence-vs-inference separation.
6. **Task Completion:** A task is done only when its acceptance criteria pass and the parent group checklist is updated.

## Acceptance Criteria
- A real-world or safely recorded fixture handles WAF failure without identity inference.
- Successful runs produce the expected end-to-end report.
- All Big Plan acceptance criteria are checked and the parent epic is ready to close.
