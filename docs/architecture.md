# Architecture

## Overview
AstroLens AI is a proof of concept for FIAP Global Solution 2026.1. It accepts astronomical image uploads, classifies objects with Gemini Vision, grounds interpretation with NASA and ESA sources via RAG, and produces scientific reports. A Streamlit dashboard presents results, analytics, and a Planet Explorer.

## Module Responsibilities
- src/app.py: Application entrypoint that wires configs, services, and run modes.
- src/config/settings.py: Environment and runtime settings loader.
- src/config/logging_config.py: Logging setup and formatting.
- src/core/orchestrator.py: End-to-end workflow coordinator across agents.
- src/core/prompt_library.py: Canonical prompts and system instructions for agents.
- src/vision/image_preprocess.py: Image normalization, resizing, and metadata extraction.
- src/vision/gemini_client.py: Gemini Vision request/response handling.
- src/rag/embeddings.py: Embedding generation for documents and queries.
- src/rag/vector_store.py: Vector database connector and index management.
- src/rag/retrieval.py: Context retrieval and re-ranking.
- src/agents/planner_agent.py: Workflow planning, task routing, and guardrails.
- src/agents/researcher_agent.py: Evidence collection and citation packaging.
- src/agents/writer_agent.py: Scientific narrative synthesis and report drafting.
- src/agents/evaluator_agent.py: Quality checks, factuality, and compliance scoring.
- src/reporting/templates.py: Report templates and formatting logic.
- src/reporting/report_generator.py: Report assembly and export packaging.
- src/data/ingestion.py: Image upload handling and input validation.
- src/data/metadata.py: Metadata parsing and provenance tracking.
- src/storage/cache.py: Cache for intermediate artifacts and model outputs.
- src/storage/artifacts.py: Persistent storage for reports and derived assets.
- src/api/routes.py: API route registration for ingestion and report access.
- src/api/schemas.py: Request/response schema definitions and validation.
- src/analytics/dashboard_metrics.py: Metrics aggregation and KPIs.
- src/analytics/telemetry.py: Trace events, spans, and audit trail emission.
- src/ui/dashboard_stub.py: Streamlit page wiring and UI scaffolding.

## Agent Data Flow
1. Vision Agent receives preprocessed image and returns object hypotheses.
2. Research Agent receives object hypotheses and requests RAG context.
3. Science Writer Agent receives hypotheses and evidence bundle to draft report.
4. Evaluator Agent scores factuality and completeness, returning checks.
5. Orchestrator merges results and persists artifacts.

## JSON Contracts Between Agents
All agent exchanges use JSON with a shared envelope:

```json
{
	"request_id": "string",
	"timestamp": "ISO-8601",
	"source": "string",
	"payload": {}
}
```

### Vision Agent Output
```json
{
	"request_id": "req_123",
	"timestamp": "2026-06-01T00:00:00Z",
	"source": "vision_agent",
	"payload": {
		"image_id": "img_abc",
		"objects": [
			{
				"label": "nebula",
				"confidence": 0.92,
				"attributes": {
					"color": "red",
					"shape": "diffuse"
				}
			}
		],
		"summary": "string",
		"warnings": ["string"]
	}
}
```

### Research Agent Output
```json
{
	"request_id": "req_123",
	"timestamp": "2026-06-01T00:00:00Z",
	"source": "research_agent",
	"payload": {
		"image_id": "img_abc",
		"objects": ["nebula"],
		"citations": [
			{
				"source": "NASA",
				"title": "string",
				"url": "https://example.org",
				"snippet": "string"
			}
		],
		"context_summary": "string"
	}
}
```

### Science Writer Agent Output
```json
{
	"request_id": "req_123",
	"timestamp": "2026-06-01T00:00:00Z",
	"source": "science_writer_agent",
	"payload": {
		"report_id": "rep_001",
		"title": "string",
		"abstract": "string",
		"sections": [
			{
				"heading": "string",
				"content": "string",
				"citations": ["string"]
			}
		],
		"impact_on_earth": "string",
		"confidence": 0.87
	}
}
```

### Evaluator Agent Output
```json
{
	"request_id": "req_123",
	"timestamp": "2026-06-01T00:00:00Z",
	"source": "evaluator_agent",
	"payload": {
		"report_id": "rep_001",
		"checks": [
			{
				"name": "factuality",
				"score": 0.9,
				"notes": "string"
			}
		],
		"recommendations": ["string"],
		"pass": true
	}
}
```

## RAG Ingestion Flow
1. Collect NASA and ESA documents in a raw document store.
2. Normalize text (cleaning, chunking, metadata tagging).
3. Generate embeddings for each chunk.
4. Store embeddings and metadata in vector database.
5. Build retrieval index and run evaluation set for relevance.
6. Publish ingestion report and version tag.

## Streamlit Page Structure
- Home: System overview, recent uploads, and status tiles.
- Upload & Analysis: Image upload, preprocessing preview, and classification output.
- Reports: Generated reports with citations and export options.
- Planet Explorer: Comparison view for Earth, Mars, Venus, Titan.
- RAG Explorer: Retrieved sources, similarity scores, and evidence trace.
- Telemetry: Trace timeline, agent decisions, and evaluation scores.

## Non-Functional Requirements
- Full traceability from image to report, with citations.
- Structured audit logs for model decisions and data sources.
- Responsible AI checks and evaluation scoring.
- Clear separation between raw inputs and generated artifacts.

## Deployment (Planned)
Containerized deployment with persistent storage for artifacts and vector index.
