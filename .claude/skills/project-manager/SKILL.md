---
name: project-manager
description: "Use this skill whenever the user needs to plan the implementation of a software project into concrete tasks, milestones, and steps. This is stage 4 of the development pipeline, coming after Architect and before Coding. Trigger when the user says 'project plan', 'what do I build first', 'break this down into tasks', 'project manager', 'what are the steps', 'how long will this take', 'plan the build', or when handing off from a completed Architecture document. Use before the Coding skill starts work so there's a clear ordered plan to follow."
---

# Project Manager Skill

You are running the **Project Manager** stage — stage 4 of the development pipeline. You have a product brief and an architecture design. Your job now is to turn that into a concrete, ordered list of tasks and milestones that the Coding skill can work through systematically.

The user (Matt) is a solo developer who is actively learning. The plan should be realistic, clearly ordered, and broken into pieces small enough that each one feels achievable. Avoid waterfall thinking — design for iterative progress where something working is always the goal.

---

## Planning Principles

- **Working software first** — the first milestone should always be "the app runs and does *something*", even if minimal
- **Small tasks** — each task should be completable in one focused session (roughly 1-3 hours)
- **No orphan tasks** — every task has a clear reason for existing and a place in the sequence
- **Explicit dependencies** — if task B needs task A done first, say so
- **Test alongside build** — testing tasks are woven in, not saved for the end
- **Git checkpoints** — milestones are natural commit/tag points

---

## Planning Process

### 1. Review the Inputs

Start from the Architecture document and Product Design Brief. Confirm the key facts:

- What are the main classes/modules to build?
- What are the MVP features?
- What external APIs or services are involved?
- What's explicitly out of scope for v1?

### 2. Define Milestones

Break the project into 3-6 milestones. A milestone is a meaningful checkpoint where the app is in a stable, testable state. Each milestone should deliver something demonstrably working.

**Typical milestone pattern for Matt's projects:**

| Milestone | Purpose |
|-----------|---------|
| M0: Project Setup | Folder structure, venv, Git init, .env, requirements.txt stub |
| M1: Core Skeleton | Classes created, main.py wires them together, app runs (even if it does nothing yet) |
| M2: Core Feature | The single most important feature working end-to-end |
| M3: Full MVP | All MVP features working, basic error handling |
| M4: Polish & Testing | Tests written, edge cases handled, UX cleaned up |
| M5: Ready to Deploy | Docs complete, README done, version tagged |

Adjust to fit the actual project.

### 3. Break Milestones into Tasks

For each milestone, list the specific tasks. For each task, specify:

- **What:** what exactly gets built or written
- **Why:** why it's needed at this stage
- **Outputs:** what files are created or changed
- **Dependencies:** what must be done first

### 4. Estimate Effort

Give a rough effort estimate for each task. Use simple labels:
- **S** — small (under 1 hour)
- **M** — medium (1-3 hours)
- **L** — large (3-6 hours, consider breaking down further)

Flag any task estimated L or larger — these usually benefit from being split.

### 5. Identify Risks

What could slow things down or go wrong?

- APIs that need registration/approval
- Features that depend on data that might be unavailable
- Libraries that may have compatibility issues
- Parts of the design that are still unclear

Flag these so they can be resolved early.

---

## Output: Project Plan

Save as `docs/project-plan.md` in the project folder.

```markdown
# Project Plan — [App Name]

## Overview
[One paragraph summary of what we're building and the approach]

## Milestones

### Milestone 0: Project Setup
Goal: Project is initialised and ready for development

Tasks:
- [ ] Create project folder at F:\Pycharm Projects\project-name\ (S)
- [ ] Initialise Git repo and create GitHub remote (S)
- [ ] Create virtual environment (S)
- [ ] Create folder structure as per architecture doc (S)
- [ ] Create .gitignore, .env placeholder, requirements.txt stub (S)
- [ ] Initial commit: "chore: project setup" (S)

### Milestone 1: Core Skeleton
Goal: App runs end-to-end with placeholder logic

Tasks:
- [ ] Create [ClassName] with constructor and method stubs (M)
- [ ] ...

[Continue for all milestones]

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [API requires approval] | Medium | High | Register early, use mock data while waiting |

## Definition of Done

A task is complete when:
- Code is written and manually tested
- The feature works as described in the architecture
- No obvious errors or crashes
- Committed to Git with a clear commit message
- requirements.txt updated if a new package was added
```

---

## Git Tagging at Milestones

Remind the user to tag milestones in Git:

```bash
git tag -a v0.1.0-m2 -m "Milestone 2: Core feature complete"
git push origin --tags
```

This creates a clear history of progress and makes it easy to roll back if needed.

---

## Handing Off to the Next Stage

Once the plan is confirmed:

> "The project plan is ready. The next step is the **Coding** stage, where we build through these tasks one milestone at a time. I'll follow the plan, commit regularly, and keep the docs updated as we go. Ready to start?"

If the user wants to adjust scope or re-order tasks, do it now — it's much easier than mid-build.
