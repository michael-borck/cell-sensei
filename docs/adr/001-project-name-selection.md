# ADR-001: Project Name Selection

**Date:** 2025-05-08  
**Status:** Accepted

---

## Context

The project required a clear and memorable name that reflects its core purpose: providing intelligent, automated feedback for student notebooks in programming or data science courses. The name would ideally capture both the **domain** (e.g., notebook cells, code blocks) and the **educational function** (e.g., guidance, formative assessment), while also being unique and adaptable as the tool evolves.

Naming goals included:
- Avoiding overly technical or rigid terminology (e.g., “Grader”).
- Retaining clarity while allowing flexibility beyond Jupyter notebooks.
- Supporting an identity that feels approachable, instructional, and forward-looking.

---

## Decision

The name **CellSensei** was selected for the project.

- **"Cell"** refers to notebook cells — the atomic units of code in student submissions — while also remaining broad enough to apply to other domains (e.g., script blocks, AI prompt segments).
- **"Sensei"** evokes a mentor or guide, reinforcing the project's role in assisting students through feedback, not just grading.

This name is educational, brandable, and adaptable across future use cases.

---

## Alternatives Considered

- **NoteGrade**: Clear, but overly generic and focused on grading.
- **AutoGraderX**: Too mechanical and branding-unfriendly.
- **NotebookAI**: Broad and hard to distinguish in the AI tooling space.
- **Jupytector**: Playful but niche, and could confuse non-Jupyter users.
- **CellChecker**: Overly literal and lacks warmth or guidance connotation.
- **GradeGuard**: Emphasizes grading defensively rather than supportively.

---

## Consequences

- The project will use **CellSensei** consistently across repositories, docs, URLs, and UI.
- The name positions the tool as a *teaching assistant*, not just an autograder.
- Future expansions to support script files, code snippets, or other forms of "cells" will remain consistent with the brand.

---

## Justification

### Abstract but Not Too Abstract
The name has a distinctive ring without being so vague that it loses meaning. It blends technical relevance with metaphorical depth, making it both memorable and understandable.

### Catchy & Supportive
“Sensei” immediately signals a friendly, educational tone — ideal for a feedback tool aimed at helping beginner programmers. It conveys guidance rather than judgment.

### Future-Proof & Extensible
“Cell” initially aligns with notebook cells but could easily extend to other programmatic structures, like:
- Function blocks in Python scripts
- LLM prompt segments
- Code excerpts in web-based IDEs

Meanwhile, “Sensei” remains semantically relevant regardless of what kind of “cell” is being supported.

### Feedback over Grading
Unlike names like “GradeGuard” that focus on evaluation, “CellSensei” emphasizes formative assessment and skill-building. It’s about improvement, not just correctness.

### Not Tied to Notebooks
The metaphor of a “cell” as a contained unit of logic allows the tool to evolve beyond Jupyter notebooks without creating a naming mismatch. That flexibility supports long-term growth without rebranding.

**Summary**:  
CellSensei captures the project’s educational intent, technical roots, and future flexibility. It’s supportive, adaptable, and distinct — well-suited for a modern feedback tool.


