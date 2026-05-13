# LLM Generation Design

## Purpose

Phase 6 introduces LLM-backed body generation without changing the core contract:

User Input -> RequirementSpec -> OutlineSpec -> SlideSpec -> Renderer -> PPTX

The immediate goal is not to call a real model. The goal is to define a narrow boundary that can be tested with a fake provider, preserves deterministic fallback behavior, and later supports Ollama or other providers.

## Non-Goals

- Do not implement an MCP renderer.
- Do not introduce LangChain or another orchestration framework.
- Do not move generation logic into the CLI.
- Do not pass provider-specific objects into SlideSpec or Renderer.
- Do not remove deterministic SlideBuilder fallback.
- Do not make network or model calls in unit tests.

## Minimal Architecture

The smallest useful shape is:

RequirementSpec + OutlineSpec + TemplateSpec
-> prompt input
-> LlmProvider
-> generated slide content
-> SlideBuilder validates into SlideSpec
-> Renderer

SlideSpec remains the only contract that crosses into rendering. The LLM layer may influence `message`, `bullets`, and `notes`, but it must not own PPTX layout or renderer behavior.

## LLM Provider Boundary

Use a narrow provider boundary that is independent from any concrete runtime:

```python
class LlmProvider(Protocol):
    def generate_slide_content(self, request: LlmGenerationRequest) -> LlmGenerationResult:
        ...
```

The provider is responsible for turning a structured prompt request into structured text output. It is not responsible for:

- Building SlideSpec.
- Selecting templates.
- Rendering PPTX.
- Retrying pipeline steps.
- Owning application configuration.

### Request Shape

`LlmGenerationRequest` should be a small structured object with:

- `requirement`: the user's RequirementSpec fields needed for content.
- `outline`: ordered slide roles/titles from OutlineSpec.
- `template_context`: only safe, relevant TemplateSpec fields such as doc_type, use_case, audience, tone/style hints.
- `constraints`: slide count, tone, language, and optional user constraints.

Do not pass raw TemplateSpec to the provider if only a subset is needed. Start with explicit fields and add only when tests need them.

### Result Shape

`LlmGenerationResult` should contain generated content by slide id:

- `slide_id`
- `message`
- `bullets`
- `notes`

The result should be validated before SlideSpec construction. Missing or invalid generated fields should fall back per slide rather than failing the whole deck unless the failure is structural and unrecoverable.

## Fake Provider Strategy

The first implementation should use a fake provider in tests.

Fake provider requirements:

- Deterministic output.
- No network or subprocess calls.
- Able to simulate provider failure.
- Able to simulate partial output, malformed output, and timeout-like errors.

Recommended fake outputs:

- One success fixture that replaces placeholder message/bullets.
- One partial fixture that omits a slide to prove fallback behavior.
- One exception fixture to prove deterministic fallback for the whole generation step.

This allows RED/GREEN tests before adding any real provider.

## Prompt Contract

Prompts should be generated from structured inputs, not free-form concatenation spread across the codebase.

Prompt assembly should live behind a small prompt builder:

```python
class LlmPromptBuilder:
    def build(self, request: LlmGenerationRequest) -> str:
        ...
```

The prompt should ask for structured JSON-like output. The parser should convert provider output into `LlmGenerationResult`.

Initial prompt requirements:

- Preserve slide order and slide ids.
- Generate one concise message per slide.
- Generate 0 or more bullets depending on layout role.
- Generate optional speaker notes.
- Avoid renderer-specific instructions.

Output parsing must be strict enough to reject malformed provider output, then allow fallback.

## Prompt Builder Responsibility

`LlmPromptBuilder` owns prompt text construction. It should be provider-agnostic and deterministic for the same `LlmGenerationRequest`.

Responsibilities:

- Convert `LlmGenerationRequest` into one prompt string.
- Include slide ids, titles, roles, audience, purpose, tone, and template context.
- Specify the expected response shape.
- Avoid Renderer-specific or PPTX-specific instructions.
- Keep prompt wording in one module so OllamaProvider does not grow ad hoc string assembly.

Non-responsibilities:

- Calling Ollama or any model runtime.
- Parsing provider responses.
- Retrying failed calls.
- Building SlideSpec.

Initial output contract should ask for JSON with a top-level `slides` list:

```json
{
  "slides": [
    {
      "slide_id": "slide-001",
      "message": "one concise message",
      "bullets": ["bullet 1"],
      "notes": "optional speaker note"
    }
  ]
}
```

## Response Parser Responsibility

`LlmResponseParser` owns conversion from provider text to `LlmGenerationResult`.

Responsibilities:

- Parse JSON text returned by a provider.
- Validate the top-level shape and per-slide fields.
- Ignore unknown fields.
- Return `LlmGenerationResult` for valid records.
- Raise a typed parse error for malformed JSON or invalid required fields.

Non-responsibilities:

- Calling providers.
- Deciding retry behavior.
- Falling back to deterministic content.
- Applying content to SlideSpec.

Fallback remains in SlideBuilder. If the parser rejects a provider response, OllamaProvider should surface a provider failure and SlideBuilder should use deterministic fallback.

## Failure Fallback Strategy

Deterministic fallback remains mandatory.

Fallback rules:

1. If no provider is configured, use current deterministic SlideBuilder behavior.
2. If provider call fails, use deterministic output for all slides.
3. If provider output is partially invalid, use generated content for valid slides and deterministic output for invalid or missing slides.
4. If generated content fails SlideSpec validation, fall back before rendering.
5. Log or expose enough diagnostic information later, but do not print noisy provider details from the CLI in the first slice.

Fallback should happen before Renderer. Renderer should never know whether content came from LLM or fallback.

## Timeout and Retry Responsibility

Timeouts and retries belong to provider adapters, not Pipeline, Renderer, or SlideSpec.

Initial rule:

- Fake provider has no timeout.
- Ollama provider owns request timeout.
- Retry count defaults to zero or one conservative retry.
- Pipeline receives either structured generated content or a provider failure.

The pipeline should not implement provider-specific retry loops. It may choose fallback when the generation component returns failure.

Logging responsibility:

- Provider adapters log provider call failures at warning level.
- SlideBuilder logs fallback after provider exceptions.
- Parser errors should be logged without dumping full prompt or full model output by default.
- CLI should avoid printing provider internals in the first implementation.

## Pipeline Integration Point

The preferred integration point is SlideBuilder or a small collaborator used by SlideBuilder.

Initial constructor shape:

```python
SlideBuilder(llm_provider: LlmProvider | None = None)
```

Where `LlmProvider` can be a fake provider in unit tests or a future Ollama-backed provider. This keeps Pipeline orchestration simple:

- Pipeline still selects template.
- Pipeline still builds outline.
- Pipeline still asks SlideBuilder for SlideSpec.
- Renderer still receives only SlideSpec and output_dir.

Do not add a DI container. Passing an optional collaborator is enough for Phase 6.

### Provider Injection Path

Provider construction should be isolated from Pipeline orchestration.

Recommended path:

1. Add a small CLI/provider factory module, for example `consultdeck.llm.provider_factory`.
2. CLI parses minimal LLM options and asks the factory for `LlmProvider | None`.
3. CLI passes the provider into `Pipeline`.
4. Pipeline passes it into `SlideBuilder`, or accepts a prebuilt `SlideBuilder`.
5. SlideBuilder remains the only component that applies provider output to SlideSpec.

Pipeline should not construct OllamaProvider directly. CLI should not assemble prompts or parse responses.

### Minimal CLI Option Proposal

Avoid exposing broad provider configuration until Ollama works behind tests.

Initial option set:

- Current implemented slice: `--llm-provider {none,fake,ollama}` with default `none`
- Current Ollama settings: fixed native `POST /api/generate`, fixed `model="gemma3"`, provider-owned timeout
- Optional later: `--ollama-base-url`, `--ollama-model`, `--llm-timeout-seconds`, `--llm-retries`

Do not add multi-provider routing options in the first Ollama slice.

## Ollama Future Integration

Ollama should be a provider adapter, not a core dependency.

Future shape:

- `OllamaLlmProvider` implements `LlmProvider`.
- It lives in an optional module or behind an optional dependency group.
- It receives `LlmPromptBuilder` and `LlmResponseParser` collaborators, or creates defaults internally.
- It accepts model name, base URL, timeout, and retry settings.
- It returns structured provider output or raises/returns a typed provider failure.
- It does not contain ad hoc prompt string construction or JSON parsing logic.

Unit tests should continue to use FakeProvider. Ollama can have integration tests that are skipped unless explicitly enabled.

## Evolution Path

### Step 1: Deterministic Content Generator Interface

- Extract current deterministic message/bullets/notes behavior behind a small generator boundary.
- Add tests proving existing output stays stable.

### Step 2: Fake LLM Provider

- Add fake provider and LLM-backed generator.
- Test success, partial failure, malformed output, and provider exception.

### Step 3: Prompt Builder and Parser

- Introduce prompt builder and strict parser.
- Keep both provider-independent.

### Step 4: Provider Factory and Injection Path

- Add a small factory that maps minimal CLI options to `LlmProvider | None`.
- Keep Pipeline free of provider construction logic.
- Add tests with fake/factory doubles before exposing real Ollama.

### Step 5: Ollama Adapter

- Add optional Ollama provider.
- Keep unit tests fake-only.
- Add opt-in integration test instructions.

### Step 6: Multi-Provider

- Add provider selection only when a second real provider is needed.
- Avoid generic orchestration framework until real duplication appears.

## Test Strategy

Minimum test coverage:

- Current deterministic SlideBuilder output remains unchanged when no generator/provider is configured.
- Fake provider success replaces placeholder content.
- Fake provider failure falls back to deterministic content.
- Partial invalid provider output falls back per slide.
- Prompt builder output is deterministic and contains required slide ids.
- Response parser accepts valid JSON and rejects malformed/invalid output.
- OllamaProvider unit tests use a fake HTTP transport, not a real Ollama process.
- Provider factory returns `None` by default and builds Ollama only when explicitly requested.
- Generated content still produces a valid SlideSpec.
- Renderer tests remain unchanged because Renderer receives SlideSpec only.
- CLI tests remain mostly unchanged until provider configuration is exposed.

No unit test should require Ollama, network access, GPU, or external credentials.

## Risk and Decision Impact

Related risks:

- R-009: LLM body generation is currently missing.
- R-022: Optional dependency boundaries must stay clear when adding LLM support.
- R-023: Provider failure or malformed output can destabilize deck generation if fallback is not enforced.
- R-024: Prompt/response parsing can drift into provider adapters or CLI if not kept behind explicit boundaries.

Decision impact:

- Existing Decision 002 remains valid: SlideSpec is the central contract.
- Existing Decision 003 and 015 remain valid: Renderer receives SlideSpec only.
- Decision 022 records the initial implementation choice: LLM content enters through a provider boundary, SlideBuilder reflects it into SlideSpec, and deterministic fallback remains mandatory.

## Boundary Against Over-Engineering

Do:

- Use Protocols or small classes only at clear seams.
- Keep provider request/result small and explicit.
- Keep deterministic fallback as the default path.
- Add one real provider only after fake-provider tests pass.

Do not:

- Add LangChain or an orchestration framework.
- Add provider routing before multiple providers exist.
- Add async pipelines unless the provider adapter requires it and tests justify it.
- Let provider output bypass SlideSpec validation.
- Put prompt text into CLI or Renderer modules.
- Parse provider output inside CLI or Pipeline.
