# Manager

A coordination agent for complex task execution.

File: `agents/manager.md`

**Features:**
- Breaks down complex requests into smaller subtasks
- Maintains a todo-based execution flow
- Delegates implementation to the build worker
- Delegates audits and quality gates to the review worker
- Coordinates final integration checks
- Hands off final documentation updates to the documentation worker

**Use cases:**
- Large coding tasks  
- Multi-step automation  
- Delegation and orchestration  

### Subagents

**Build Worker**
File: `agents/build_worker.md`

Implements features and fixes.
- Reads related code and dependencies first
- Applies precise, architecture-safe code changes
- Reports changed files and technical deltas

**Review Worker**
File: `agents/review_worker.md`

Performs read-only quality audits.
- Reports blocking issues (bugs, regressions, requirement gaps)
- Reports optional improvements
- Returns an explicit **PASS** or **FAIL** verdict

**Documentation Worker**
File: `agents/documentation_worker.md`

Maintains comments and documentation.
- Updates README/docs/changelog content
- Adds or improves comments where needed
- Does not change runtime code behavior

---

## Manager and Subagent Interaction

For each subtask, the manager coordinates this loop:
1. Build: delegate implementation to `build_worker.md`.
2. Review: send output to `review_worker.md`.
3. Evaluate:
  - If verdict is **FAIL**, send feedback back to `build_worker.md` for fixes.
  - Re-run `review_worker.md` after fixes.
  - Continue until verdict is **PASS**.

After all subtasks are complete, the manager performs integration-level validation:
1. Run final test/integration checks with `build_worker.md`.
2. Request a final regression/architecture audit from `review_worker.md`.
3. Request final documentation updates from `documentation_worker.md`.

This workflow keeps responsibilities separated while improving reliability and maintainability.

---

## Test

The `test/` directory contains two one-shot tests to compare the **Manager** agent against the default OpenCode **Build** agent.

These tests were conducted using **MiniMax M2.5 Free** with standard reasoning effort.

### Prompt Used

```text
Build a chess game using pygame. I want a visual chess board with figurines. The game should track which pieces have been eliminated, the time that has passed and properly detect win and lose conditions. Obviously the game should only allow legal moves of pieces.
```

## Results

- The **Manager** agent appeared to significantly outperform the **Build** agent.
- The **Documentation Worker** was not invoked by the **Manager**. This was likely caused by limitations of the relatively weak LLM used in the test.
- The **Build Worker → Review Worker** chain executed as intended.
- Both implementations left a lot to be desired. This was likely caused by both the LLM used in the test and the weak prompt.
