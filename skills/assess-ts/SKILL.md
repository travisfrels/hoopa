---
name: assess-ts
description: Assess a technical solution against the *Technical Solution Rubric*.
---

Assess the technical solution $ARGUMENTS against the *Technical Solution Rubric*.

## Technical Solution Rubric

### Task

Assessing the viability of a technical solution — how completely it solves the stated technical problem, how predictably it behaves, how idiomatically it uses its language and framework, and how implementable / reversible it is within project constraints.

The dimensions assume a software engineering context (language, library, framework, dependencies, blast radius).

### Dimensions

| Dimension | Evaluative Question |
| --- | --- |
| Impact | How completely does it solve the stated problem? |
| Least Astonishment | Does it behave as a subject-matter expert would expect? |
| Idiomaticity | Does it use the languages, libraries, and/or frameworks with deep knowledge, understanding, and expertise? |
| Cost / Effort | How much engineering investment does it require? |
| Risk | How recoverable is failure? |

### Descriptors

Quality Scale. For inverted-polarity dimensions (Cost / Effort, Risk), `Strong` means low effort / small blast radius — not high cost / high risk.

| Dimension | Strong | Adequate | Marginal | Weak |
| --- | --- | --- | --- | --- |
| Impact | Solves the full stated scope. | Solves the dominant scope; minor gaps remain. | Solves part of the scope; meaningful gaps require follow-on work. | Partial — major gaps remain. |
| Least Astonishment | Behaves as a subject-matter expert expects. | Non-obvious behavior, but documented or discoverable. | Non-obvious behavior requiring explanation; not surfaced in the code. | Surprising side effects or unfamiliar mental model. |
| Idiomaticity | Uses the languages, libraries, and/or frameworks idiomatically. | Adjacent to idiomatic usage; minor deviations. | Notably non-idiomatic; mixes conventions or works around the framework. | Fights the languages, libraries, or frameworks. |
| Cost / Effort | Trivial change; no new dependencies. | Moderate change; manageable new dependencies or learning curve. | Substantial change; new dependency surface or specialized expertise. | Significant engineering effort or large new dependency surface. |
| Risk | Fully reversible; small blast radius. | Reversible with effort; medium blast radius. | Reversible only with coordination; broad blast radius. | Hard to reverse; large blast radius or fragile coupling. |

### References

- Raymond, E. S. (2003). *The Art of Unix Programming*. Addison-Wesley. — Principle of Least Astonishment; idiomatic design.
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (Eds.). (2016). *Site Reliability Engineering*. O'Reilly. — Blast radius; reversibility; risk.

## Assessment Steps

1. Assess the technical solution against the *Technical Solution Rubric* to make a *viability determination*
2. Render the *viability determination* as a markdown table composed of rubric dimensions and their corresponding scores
   - DO NOT INCLUDE:
      - Evaluative questions
      - Descriptors
      - Sources

The intention is a concise view of the technical solution's viability, not a lengthy analysis. Be as brief and clear as possible in your assessment.
