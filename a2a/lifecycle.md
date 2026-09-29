# Bonus: the failed case on the A2A task lifecycle

The AgentCard the orchestrator would advertise is `a2a/agent-card.json`: one
skill (`adapt-recipe-for-allergen`), text/JSON in, JSON out, and bearer auth
with the same scopes as the Week 9 gateway. It is not served anywhere; this is
the card as it would be published at `/.well-known/agent-card.json`.

## s01 with the allergen worker down, as A2A task states

```
What actually happened (plain function calls):
  submitted -> working -> [allergen worker 500, retry 500] -> working -> "completed" (with a caveat)

What it should have been:
  submitted -> working -> [allergen worker task: failed] -> failed
```

**It should have ended `failed`, not paused at `input-required`.**

`input-required` is for when **the user** holds the missing piece. In s01 the
user already said "leave out anything with egg". The allergy list was in the
request. What was missing was the allergen worker's *answer*, and no reply from
the user can supply that. Asking "what are you allergic to?" would have been
theatre.

`input-required` would be right for a request like *"make it safe for my son"*
with no allergen named. The AgentCard's skill description says exactly that.

Marking it `completed`, which is what the current code effectively does, tells
a calling agent the recipe was checked. The caveat text sits inside the
artifact, and a machine caller reading only the task state never sees it. With
people's allergies at stake, a `failed` state is the honest signal.

## What A2A buys over a plain REST call to the worker

1. **A shared task lifecycle.** `failed`, `input-required`, `completed` and the
   others are protocol states a caller must handle, instead of a bare 500 that
   every caller reinterprets. This is exactly why our 500 got papered over.
2. **Discovery and auth, declared up front.** The AgentCard says what the
   worker can do and what token it needs, so a new orchestrator can find and
   call it without a bespoke integration.

(MCP connects an agent to *tools*. A2A connects an agent to *another agent*,
which can pause, ask, and fail as an agent.)
