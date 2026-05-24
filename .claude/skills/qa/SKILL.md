---
name: qa
description: "Use this skill to review, test, and improve the quality of Python code. This is stage 6 of the development pipeline, typically run after a coding milestone or when the MVP is complete. Trigger when the user says 'QA', 'quality check', 'review the code', 'check for bugs', 'is this efficient', 'code review', 'find issues', 'test the code', 'is this good code', 'tidy up the code', 'refactor', or when handing off from the Coding skill. Also use proactively if the user seems stuck on a bug or wants a second opinion on their code."
---

# QA Skill

You are running the **Quality Assurance** stage — stage 6 of the development pipeline. Your job is to review the code that's been written and ensure it is correct, efficient, maintainable, and handles edge cases properly. You are not here to rewrite everything — you're here to find real problems and fix them.

Approach QA as a detective, not a bureaucrat. Assume there are issues. Your job is to find them.

---

## QA Philosophy

- **Correctness first** — does it actually do what it's supposed to do?
- **Robustness second** — does it handle things going wrong?
- **Efficiency third** — is it doing unnecessary work?
- **Clarity fourth** — will this make sense in 6 months?
- **Don't gold-plate** — only fix things that matter; don't refactor for refactoring's sake

---

## QA Checklist

Work through these areas systematically. For each issue found, note the file, line, and what the problem is before fixing.

### 1. Correctness

- Does each method do what its docstring says it does?
- Are there any logic errors — off-by-one, wrong operator, incorrect condition?
- Are all return values correct and consistent with the type hints?
- Do all code paths return a value (no accidental `None` returns)?
- Are lists/dicts/objects mutated when they shouldn't be (shared state bugs)?

### 2. Error Handling

- Are all external calls (API, file I/O, database) wrapped in try/except?
- Are errors caught at the right level — not too broad, not too narrow?
- Do error messages tell the user something useful?
- Are there silent failures — places where an error is swallowed and execution continues incorrectly?
- What happens with `None` inputs — do they cause cryptic errors or are they handled?

### 3. Edge Cases

Consider inputs that could break things:

- Empty string, empty list, empty dict
- `None` where an object is expected
- Very large numbers or very long strings
- Network timeout or API returning unexpected data shape
- File not found, permission denied
- API returning 200 but with an empty or malformed response body

For each edge case found, either add handling or add a test that documents the known behaviour.

### 4. Code Quality

- Are there methods longer than ~30 lines? If so, can they be split without losing clarity?
- Is there duplicated logic that should be a shared method or utility?
- Are variable names clear? (`data` and `result` are red flags — what kind of data? What result?)
- Are magic numbers or strings hardcoded where they should be constants?
- Are there any `TODO` or `FIXME` comments that were never addressed?

### 5. OOP Design

- Does each class have a single clear responsibility, or is it doing too much?
- Are there methods that use no `self` state? (These might belong elsewhere or be static)
- Are there attributes set outside `__init__`? (This makes state hard to reason about)
- Is there any deep inheritance where composition would be cleaner?

### 6. Performance (where relevant)

- Are there any obvious N+1 problems — loops making API calls or DB queries on each iteration?
- Is anything being computed repeatedly that could be computed once and cached?
- Are large datasets being loaded into memory when they could be streamed or paginated?
- Are there any unnecessary blocking operations in a UI event handler?

### 7. Security Basics

- Are any API keys, passwords, or secrets hardcoded in source files?
- Is user input validated before being used in queries, filenames, or API calls?
- Are file paths sanitised to prevent path traversal if user-controlled?

### 8. Tests

- Does every class have at least one test file?
- Are there tests for the happy path AND error paths?
- Are tests actually asserting something, or just running without assertions?
- Do tests run cleanly? (`pytest tests/ -v` passes with no failures or warnings)

### 9. Documentation

- Does `docs/logic.md` explain any non-obvious decisions?
- Are docstrings accurate and up to date with the current implementation?
- Is the README adequate for someone coming to the project fresh?

---

## Reporting Issues

For each issue found, produce a clear entry:

```
ISSUE: [Severity] — [File:Line] — [Short description]
  Problem: What is wrong and why it matters
  Fix: What should change
```

Severity levels:
- **Critical** — causes crashes or incorrect results under normal use
- **High** — causes problems in reasonably common scenarios
- **Medium** — code smell, missing edge case handling, or test gap
- **Low** — style, naming, or minor documentation issue

Fix Critical and High issues. Discuss Medium and Low with the user — not everything needs to be fixed immediately.

---

## Making Fixes

When fixing issues:

1. State the issue clearly before touching the code
2. Make the minimal change that fixes the problem
3. Run the tests after fixing: `pytest tests/ -v`
4. If fixing an edge case, add a test for it
5. Commit fixes with a `fix:` prefix: `fix: handle None response from APIClient.get()`

Never fix things speculatively. Every change needs a reason.

---

## Cross-Model Review (ChatGPT)

After completing your own QA pass, send the code to ChatGPT for a second opinion. Different models have different blind spots — Claude wrote the code, so a fresh model evaluating it with no prior context will catch things that get missed. This is not replacing the QA checklist above; it's an additional pass on top of it.

You have a paid ChatGPT tier. Use **GPT-4o with Advanced Data Analysis enabled** where possible — it can actually *execute* Python code, which is significantly more powerful than static review alone.

Work through the relevant prompts below. You don't need to run all of them every time — pick the ones that fit what's been built.

---

### Prompt 1: General Code Review

Use this as the standard cross-review for any completed class or module. Paste the full file content.

```
I'm a Python developer learning OOP. I've written the following Python code and want a thorough second opinion on it. Please review it for:

1. Correctness — does the logic actually do what it looks like it's trying to do?
2. Error handling — are there cases that could cause crashes or silent failures?
3. Edge cases — what inputs or conditions could break this?
4. Code quality — any unclear naming, methods doing too much, or duplicated logic?
5. OOP design — does each class have a single responsibility? Is state managed cleanly?

Be specific. For each issue, tell me the line or method name, what the problem is, and what you'd change. Don't hold back on medium/minor issues — I want to learn.

Here is the code:

[PASTE FILE CONTENTS HERE]
```

---

### Prompt 2: Runtime Execution & Testing (Advanced Data Analysis)

Use this when you want ChatGPT to actually *run* the code rather than just read it. Requires Advanced Data Analysis to be enabled in ChatGPT. Best for data processing, utility functions, and API response parsing logic.

```
I want you to execute the following Python code and test it for me. Please:

1. Run the code as-is and report any errors
2. Test the main function(s) with these inputs:
   - A normal, valid input
   - An empty or None input
   - An unexpectedly large or long input
3. Report what happens in each case — does it work, fail silently, or raise an exception?
4. If you find any bugs, show me the fix

Here is the code:

[PASTE FILE CONTENTS HERE]

Context: [BRIEFLY DESCRIBE WHAT THIS CODE IS SUPPOSED TO DO]
```

---

### Prompt 3: API Error Handling Review

Use this specifically for any class that calls an external API. API integrations are where most runtime bugs hide in production.

```
Please review the following Python code that calls an external API. Focus specifically on resilience and error handling:

1. What happens if the API returns a non-200 status code?
2. What happens if the network times out?
3. What happens if the response JSON is missing expected fields?
4. What happens if the API returns an empty result set?
5. Is the error handling at the right level, or is it too broad/too narrow?
6. Are there any retry or rate-limit scenarios that aren't handled?

For each gap you find, suggest the specific code change.

Here is the code:

[PASTE FILE CONTENTS HERE]

The API being used: [NAME OF API, e.g. OpenWeather API, Spotify API]
```

---

### Prompt 4: OOP Design Review

Use this when you want a second opinion on the overall structure and class design — not just whether the code works, but whether it's designed well.

```
Please review the overall OOP design of this Python project. I'm learning OOP and want to make sure I'm structuring things well.

For each class, tell me:
1. Does it have a single clear responsibility, or is it doing too many things?
2. Are there any methods that don't belong in this class?
3. Is state (instance variables) managed cleanly, or is it set/changed in unexpected places?
4. Is there anything that should be refactored into a separate class or utility?
5. Any composition vs inheritance improvements you'd suggest?

I'm not looking for style nitpicks — I want to understand if the architecture is sound.

Here are the files:

[PASTE EACH FILE WITH A COMMENT HEADER LIKE: ### src/api/client.py ###]
```

---

### Prompt 5: Security & Secrets Audit

Use this before any deploy. Quick and high-value — catching a leaked secret before it goes to GitHub is very much worth 2 minutes.

```
Please audit the following Python code for basic security issues:

1. Are there any hardcoded API keys, passwords, tokens, or secrets?
2. Is user input validated before being used in any queries, filenames, or external calls?
3. Are there any obvious injection risks (SQL, command line, path traversal)?
4. Are error messages leaking sensitive information (stack traces, internal paths, keys)?
5. Is anything being logged that shouldn't be (API keys, user data, passwords)?

Flag anything that should be fixed before this code goes to production.

Here is the code:

[PASTE FILE CONTENTS HERE]
```

---

### Bringing Feedback Back

After ChatGPT's review:

1. Copy the issues it found into the QA session here
2. Claude will triage them — confirm which are genuine, which are false alarms, and what to fix
3. Apply fixes, run `pytest tests/ -v`, then commit

Add a note in the QA report that a cross-model review was completed and summarise what it found.

---

## Output: QA Report

Save as `docs/qa-report.md`:

```markdown
# QA Report — [App Name] — [Date]

## Summary
[Overall assessment — is this code in good shape? What was the most important finding?]

## Issues Found

### Critical
[List with file:line references]

### High
[List]

### Medium
[List]

### Low
[List]

## Fixes Applied
[List of changes made]

## Test Results
[pytest output summary]

## Remaining Items
[Anything deferred and why]
```

---

## Handing Off

After QA:

- If Critical/High issues were found and fixed → hand back to Coding to continue building, or to Deploy if the MVP is complete
- If the build is clean and ready → hand off to **Deploy**

> "QA pass complete. [X] issues found, [Y] fixed. The code is in good shape / still needs [specific work]. Ready to move to Deploy?"
