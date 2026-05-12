# Phase 6 Plan

## Goals

Phase 6 turns the MVP pipeline into a more useful local deck generator while preserving the current architecture:

User Input -> RequirementSpec -> OutlineSpec -> SlideSpec -> Renderer -> PPTX

The phase should improve content quality, layout fidelity, and distribution reliability without moving generation logic into the CLI or coupling non-renderer modules to PPTX libraries.

## Priorities

1. LLM body generation
   - Replace deterministic placeholder `message` and `bullets` with generated business content.
   - Keep generated output validated through SlideSpec.
   - Address R-009 first because it has the largest impact on deck usefulness.

2. Minimal layout_rules/style_rules reflection
   - Improve BuiltinPptxRenderer output quality in a controlled way.
   - Start with a small set of style tokens and layout decisions that can be represented before the Renderer boundary.
   - Address R-004 and R-008 after SlideSpec content quality is stable.

3. Template evolution
   - Make templates richer only where the pipeline has a clear consumer.
   - Avoid turning TemplateRepository into a selector or policy engine.
   - Support future alias/scoring work without changing existing template loading responsibilities.

4. Packaging and wheel distribution
   - Make non-editable installs reliable by including default templates in the distribution.
   - Address R-021 before treating wheel installs as supported.

5. Optional dependency cleanup
   - Separate base CLI dependencies from optional LLM, image generation, MCP, and renderer integrations.
   - Keep the default install light and deterministic.

6. Image generation integration
   - Treat Stable Diffusion or other image generation as supplemental image production.
   - Do not use image generation for diagrams, charts, or structured consulting logic.

7. MCP Renderer and external renderer future
   - Keep as a later extension after the local BuiltinPptxRenderer contract is stable.
   - Do not implement MCP in the first Phase 6 slice.

## Roadmap

### Step 1: LLM Text Adapter

- Add a narrow text generation boundary that takes RequirementSpec, OutlineSpec, and TemplateSpec context and returns validated slide content.
- Keep SlideBuilder responsible for producing SlideSpec.
- Add tests that first fail on placeholder text, then pass with deterministic fake LLM output.
- Do not call network services in unit tests.

Expected output:
- Generated `message`, `bullets`, and optional `notes`.
- SlideSpec remains the only object passed to Renderer.

### Step 2: SlideSpec-Safe Style Inputs

- Decide the minimal style data that must survive until rendering.
- Prefer explicit SlideSpec fields or a narrow renderer settings object over passing TemplateSpec into Renderer.
- Start with font name, basic title/content positioning, and simple two-column behavior.
- Add tests around rendered PPTX structure and text placement where feasible.

Expected output:
- R-004/R-008 reduced without widening the Renderer protocol beyond `render(spec, output_dir)`.

### Step 3: Template Evolution

- Extend template YAML only after a consumer exists in tests.
- Keep TemplateRepository limited to loading and validation.
- Keep TemplateSelector limited to matching and later scoring.
- Consider alias dictionaries or template metadata for R-001/R-002/R-003, but do not mix them into repository loading.

Expected output:
- Template changes remain backward-compatible or explicitly migrated.

### Step 4: Packaging Reliability

- Verify wheel contents with a build/install smoke test.
- Include `assets/templates` through package data, hatch artifacts, or a resource package.
- Prefer `importlib.resources` for installed default template access if assets move under the Python package.
- Keep editable install behavior working.

Expected output:
- R-021 resolved and R-020 reduced.

### Step 5: Optional Dependency Groups

- Split dependencies into core and optional groups.
- Candidate groups:
  - `llm`
  - `image`
  - `mcp`
  - `dev`
- Ensure base `consultdeck --help` and basic local rendering work without optional integrations.

Expected output:
- Smaller base install and clearer operational constraints.

### Step 6: Supplemental Image Generation

- Add image generation only after text and layout are stable.
- Enforce GPU workload serialization before any local image generation is invoked.
- Store generated image references in SlideSpec.ImageSpec or equivalent validated fields.
- Keep diagrams and charts as PPT-native or structured Renderer output.

Expected output:
- Optional visual enrichment without weakening core deck structure.

### Step 7: MCP Renderer Exploration

- Implement only after the local Renderer contract has enough coverage.
- Keep integration behind McpClient, McpAdapter, and McpRenderer.
- Preserve the same narrow Renderer protocol.

Expected output:
- External rendering can be evaluated without changing Pipeline or SlideSpec contracts.

## Architecture Constraints

- SlideSpec remains the central contract between generation and rendering.
- Renderer protocol remains narrow: `render(spec: SlideSpec, output_dir: Path) -> Path`.
- Non-renderer modules must not import PPTX libraries.
- CLI remains a thin adapter from arguments to RequirementSpec and Pipeline.
- Pipeline orchestrates existing components but does not own generation, template policy, or rendering details.
- TemplateRepository stays a data access layer.
- TemplateSelector owns matching/scoring rules.
- GPU workloads must not run concurrently.
- Network-backed or model-backed generation must be isolated behind testable adapters.

## Postponed Work

- Full MCP Renderer implementation.
- Stable Diffusion integration as a default path.
- Advanced template scoring and audience ontology.
- Full visual design system for PPTX.
- Multi-renderer routing or DI containers.
- UI-based configuration.
- Automatic versioned output management.

## Risk Mapping

| Risk | Phase 6 response |
| --- | --- |
| R-001 | Consider alias dictionaries after template evolution has tests. |
| R-002 | Add scoring only when multiple real templates require prioritization. |
| R-003 | Move doc_type aliases toward configuration or metadata when template evolution starts. |
| R-004 | Add minimal style/layout propagation without passing TemplateSpec into Renderer. |
| R-008 | Improve renderer output incrementally after content generation is useful. |
| R-009 | First implementation slice: LLM text generation behind a testable adapter. |
| R-010 | Keep MCP Renderer postponed until local Renderer contract is stable. |
| R-011 | Keep image generation supplemental and optional. |
| R-020 | Reduce after installed default template access is verified. |
| R-021 | Resolve with wheel packaging and installed smoke tests. |
| R-022 | Track optional dependency sprawl before adding LLM/image/MCP integrations. |

## Small-Step Implementation Policy

- Start each slice with a failing test.
- Prefer fake adapters and deterministic fixtures before real model calls.
- Add one contract at a time; avoid broad framework setup.
- Update docs/06_decisions.md only when a durable design decision is made.
- Update docs/07_risks.md when a risk is introduced, reduced, or accepted.
- Keep each commit scoped to one coherent change.
