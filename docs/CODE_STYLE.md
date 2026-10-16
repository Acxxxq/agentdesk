# AgentOrbis Code Style

These guidelines keep the project readable and maintainable. They also make the business rules behind the code easier to understand for Chinese-speaking contributors.

## Language and naming

- Write project documentation, issues, and pull requests in English; common technical terms may remain in English.
- Use clear English identifiers for modules, classes, functions, variables, database fields, and API fields. Avoid pinyin and unclear abbreviations.
- Add Python type annotations. Keep I/O paths asynchronous and do not run blocking operations in the event loop.
- Choose names that express business meaning, such as `conversation_id` and `request_id`, instead of vague names like `id1` or `data2`.

## Readability and structure

- Give each function and class a clear, limited responsibility. Split complex flows into small functions that reflect business steps.
- Prefer direct, easy-to-follow control flow. Avoid unnecessary layers, hidden side effects, over-generalized frameworks, and duplicate configuration sources.
- Keep business rules in the domain or application layer. Put HTTP, database, and external service details in their corresponding adapters.
- Make shared state and database writes visible. Keep transaction, concurrency, idempotency, and tenant-isolation rules traceable in code and tests.
- Follow the repository's Ruff configuration and existing formatting conventions.

## Chinese comments and docstrings

- Write new or modified code comments, module descriptions, and public function/class docstrings in Chinese.
- Explain why a decision exists, its business meaning, edge cases, or non-obvious concurrency/compatibility constraints. Do not translate each line of code into a comment.
- Add concise Chinese comments around critical state transitions, authorization, idempotency, transaction boundaries, and external side effects to explain invariants or risks.
- Do not add comments just to increase their count. Use clear naming and structure when code is self-explanatory.
- When modifying existing code, update touched comments and docstrings in Chinese. Avoid unrelated large-scale comment rewrites.

## Errors and security

- Use explicit error types and stable API responses for expected business failures. Do not hide errors with broad exception handling.
- Do not include passwords, tokens, database URLs, or sensitive customer information in logs or diagnostics.
- Read secrets from environment configuration; never put real values in source code, test snapshots, or example commands.
- Set timeouts for external side effects. Confirm an operation is idempotent before retrying it, and support recovery behavior with tests or documentation.

## Tests and validation

- Add meaningful tests for new behavior and bug fixes, including relevant edge cases. Test names should describe the scenario and expected result.
- Keep domain logic testable offline where possible. Clearly distinguish fast offline checks from validation that requires live MySQL, Redis, or APIs.
- State the checks performed and any uncovered scenarios in the pull request.
