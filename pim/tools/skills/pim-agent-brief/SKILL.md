---
name: pim-agent-brief
description: Write the brief for a subagent working in the living-computing pim/ project (PIM/m, PIMOS, SIMPOS/PSI, window system). The standing rules live in pim/tools/agent_rules.md, so the brief states only the task. Use whenever spawning an Agent for pim work.
---

# Briefing a pim agent

Do not paste the rules. Start every pim brief with this line:

> You are working in the living-computing repo, only under `pim/`. First read
> `/Users/npe/src/living-computing/AGENTS.md` and
> `pim/tools/agent_rules.md` and follow them; they override anything below.

Then give only what is specific to the task:
1. **Goal**, named by milestone, with the plan file and section to read
   (for example `docs/simpos/window_hardware_plan.md` H3, `plan.md`, or
   `docs/simpos/boot_route.md`).
2. **Starting point**: the master commit, what the last milestone left,
   and what was already ruled out.
3. **Done means**: the evidence expected, as commands and counts.
4. **Special risks** this task has beyond the rules file, for example
   a shared file another agent is editing. Name the file and say whether
   to stay out of it.
5. **Report**: which items to include beyond the standard ones in the
   rules file.

Use `isolation: "worktree"` and `run_in_background: true`. When the agent
hands back, merge with the `pim-merge` skill.

When the rules change (an owner instruction), edit
`pim/tools/agent_rules.md` and commit it. Do not patch individual briefs.
