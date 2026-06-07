"""CLI smoke test for ResearchAgent."""

import json
import logging
from typing import Optional

from bootstrap import add_repo_root

add_repo_root()

from src.agents.research_agent import ResearchAgent
from src.agents.vision_agent import VisionAnalysisResult


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    analysis = VisionAnalysisResult(
        classification="Galaxy",
        confidence=0.95,
        description="Spiral galaxy",
        astronomical_objects=["spiral arms"],
        scientific_tags=["Spiral Galaxy", "Star Formation"],
    )

    agent = ResearchAgent()
    result = agent.research(analysis)

    print(
        json.dumps(
            {
                "topic": result.topic,
                "definition": result.definition,
                "scientific_importance": result.scientific_importance,
                "space_exploration_relevance": result.space_exploration_relevance,
                "earth_impact": result.earth_impact,
                "source": result.source,
                "related_tags": result.related_tags,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
