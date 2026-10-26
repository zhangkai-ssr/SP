# SP Video Workflow Adaptation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adapt the proven collaboration structure from `C:\work1\JSZN\ESP32_S3\1.6_R6` to the `D:\sp` video workspace without copying firmware-only rules.

**Architecture:** Add one repository-level instruction file and one concise cross-session ledger. Keep the existing numbered directory layout, and make verification depend on the artifact being changed: source checks for scripts, render checks for videos, provenance checks for assets, and explicit authorization for external generation or publishing.

**Tech Stack:** Markdown, Git, PowerShell, Python, FFmpeg/ffprobe.

## Global Constraints

- Preserve the current numbered directory structure and all user-owned media.
- Do not add firmware, device, COM/MAC, flashing, hardware, or ESP-IDF rules.
- Do not publish, upload, spend provider credits, or modify external accounts without explicit authorization.
- Use explicit Git staging; never use `git add .` or `git add -A` in the normal workflow.
- Keep the workflow lean: one final HEAD verification, one independent review, and one freshness check.

---

### Task 1: Add repository collaboration rules

**Files:**
- Create: `AGENTS.md`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: current directory layout and existing Git repository.
- Produces: repository-wide operating rules and ignored `.WORKTREE/` state.

- [x] **Step 1: Define directory ownership**

Document `01_工具`, `02_项目`, `03_交付`, `05_研究参考`, `90_归档`, `plan.md`, and `.WORKTREE` with one owner and one source-of-truth rule per area.

- [x] **Step 2: Define the six-step worktree/PR flow**

Use branch names `feature/sp/<task>` and worktrees under `D:\sp\.WORKTREE\<purpose>`. Allow small documentation/index changes directly on `main`; require behavior changes to use the isolated flow.

- [x] **Step 3: Define media-specific evidence gates**

Separate script/source verification, local render QA, editable-draft compatibility, external-provider generation, and actual platform publication.

- [x] **Step 4: Ignore local worktrees**

Add this rule to `.gitignore`:

```gitignore
.WORKTREE/
```

### Task 2: Add the cross-session work ledger

**Files:**
- Create: `plan.md`

**Interfaces:**
- Consumes: the current verified repository and video-tool state.
- Produces: a concise source of truth for durable status, acceptance boundaries, and unresolved risks.

- [x] **Step 1: Define record rules**

Record only cross-session scope, external provider/task state, formal artifact acceptance, and important unresolved risks. Leave ordinary implementation, tests, review, and PR history to Git and GitHub.

- [x] **Step 2: Record the current baseline**

Record the organized repository baseline and the verified `AI判断权_最终成片.mp4` properties without claiming platform publication.

- [x] **Step 3: Record unresolved workflow gaps**

Keep Runway availability, Jianying draft compatibility, and the planned task-manifest/provenance/QA improvements as explicit pending boundaries.

### Task 3: Connect the workflow from the root README

**Files:**
- Modify: `README.md`
- Create: `docs/superpowers/plans/2026-09-10-video-workflow-adaptation.md`

**Interfaces:**
- Consumes: `AGENTS.md` and `plan.md`.
- Produces: a discoverable workflow entry point and a retained implementation plan.

- [x] **Step 1: Add the required reading order**

At the top of `README.md`, link to `AGENTS.md` and `plan.md` and state when each is used.

- [x] **Step 2: Add the change modes**

Explain that small documentation changes may be direct while script/render behavior changes use `.WORKTREE` and PR review.

- [x] **Step 3: Verify the adaptation**

Run:

```powershell
git diff --check
python .\01_工具\文字卡片生成器\make_video.py --help
Push-Location .\02_项目\存在主义项目
python .\manju.py --help
Pop-Location
```

Expected: no whitespace errors; both command-line entry points exit successfully.

Also verify every Markdown link target referenced by `README.md` and `AGENTS.md`, confirm `.WORKTREE/` is ignored, and review the final diff for firmware-only terms.

### Task 4: Resolve independent review findings

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `plan.md`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: the first independent review of the complete workflow draft.
- Produces: worktree-safe commands, complete cache ignores, an actual-remote Git baseline, a large-media policy, and a full delivery-package gate.

- [x] **Step 1: Make commands worktree-safe**

Replace hard-coded `D:\sp` run commands with paths relative to the current repository root and keep the source project in `02_项目` when promoting a delivery.

- [x] **Step 2: Close cache and Git-baseline gaps**

Ignore project `work/` and `_tmp/` paths. Require fetch before branching, review against `origin/main...HEAD`, distinguish Git publication authorization from video publication, and prove local/tracking/remote synchronization after merge.

- [x] **Step 3: Define media and delivery gates**

Require an explicit storage decision at 50 MiB, prohibit ordinary Git blobs at GitHub's 100 MiB limit, and verify the complete delivery package including provenance, rights, and hashes.

- [x] **Step 4: Add minimal skill routing**

Route worktree setup, root-cause diagnosis, behavior-change TDD, and final verification without adding duplicate process stages.
