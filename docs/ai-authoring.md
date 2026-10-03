# Authoring problems with AI agents

autogradescoper is designed so that generative AI can do most of the
mechanical work of problem authoring **while the tool verifies the result
objectively**. The key insight: `autogradescoper validate` is a closed
feedback loop — an agent can write a problem, grade it, read the report, and
iterate without any human in the middle. Your judgment goes into the *spec*
and the *pedagogy*; the loop checks everything else.

## Setup

Give your AI agent access to this repository (or an assignment directory)
plus one of:

- **[AGENTS.md](../AGENTS.md)** (repo root) — picked up automatically by most
  coding agents (Claude Code, Codex, OpenCode, Antigravity, Gemini CLI);
- **[skills/problem-author/](../skills/problem-author/)** — a drop-in skill
  for Claude Code / Cowork: copy the directory into your skills folder or
  install it from the repo.

Both encode the same workflow; the skill triggers automatically when you ask
for "an autograded problem".

## The prompt that works

Tell the agent the three pedagogical facts only you know:

> Create an autograded problem for [course/topic]. Students must demonstrate
> [concept]. A correct-but-naive solution using [naive approach] must FAIL
> via time limits; the intended solution is [approach/complexity]. Students
> may use [base R only / Python stdlib only / anything]. Follow AGENTS.md:
> scaffold with `autogradescoper init`, write the solution, args, and
> slow/incorrect example traps, then run `autogradescoper validate` and
> iterate until the report shows solution 100%, v1_slow timing out on the
> large cases, and v2_incorrect caught.

## What to review as the human

The validation report proves internal consistency, not pedagogical value.
Before shipping, check:

1. **The spec** (PROBLEM.md): is it unambiguous? Are tie-breaks and edge
   cases stated? Would *you* accept the intended solution as the lesson?
2. **The traps**: is `v1_slow` the mistake your students will actually make?
3. **Margins**: intended solution ≤ 20% of maxtime on the slowest hardware
   you care about (Gradescope machines are slower than your laptop — multiply
   local times by ~2–3× when setting limits).
4. **Determinism across runs**: run `validate` twice; identical reports.

## Verifying AI-written solutions

Treat the AI's reference solution like any AI code (this is the course
thesis, after all): ask the agent to also write a brute-force reference and a
cross-check script, or require the solution to match a trusted library on
random inputs. The `validate` self-test catches nondeterminism and formatting
instability, but only an independent oracle catches a solution that is
*consistently* wrong.

## CI suggestion

Run validation on every commit of your assignments repository:

```yaml
# .github/workflows/validate.yml (sketch)
- run: pip install autogradescoper
- run: sudo apt-get install -y r-base   # if you have R problems
- run: for d in assignments/*/; do autogradescoper validate "$d" || exit 1; done
```
