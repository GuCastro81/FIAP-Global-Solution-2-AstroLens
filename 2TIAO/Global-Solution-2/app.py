"""Streamlit dashboard for AstroLens AI."""

from __future__ import annotations

import json
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

from src.agents.exoplanet_spectrum_agent import (
    ExoplanetAtmosphereResult,
    ExoplanetSpectrumAgent,
)
from src.agents.research_agent import ResearchAgent, ResearchResult
from src.agents.science_writer_agent import ScienceReport, ScienceWriterAgent
from src.agents.vision_agent import VisionAgent, VisionAnalysisResult
from src.reporting.exoplanet_reporter import ExoplanetReport, ExoplanetReporter
from src.services.gemini_service import GeminiService
from src.services.nasa_service import NASAImage, NASAService, NASAServiceError
from src.storage.result_storage_service import ResultStorageService

_MAX_NASA_RESULTS = 12
_MAX_NASA_IMAGE_BYTES = 20 * 1024 * 1024
_K2_18B_CHART_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "images"
    / "exoplanets"
    / "k2-18b"
    / "atmosphere_composition.jpg"
)


def main() -> None:
    st.set_page_config(
        page_title="AstroLens AI",
        page_icon="AL",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _apply_styles()

    st.sidebar.title("AstroLens AI")
    st.sidebar.caption("Astronomy image intelligence")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "Analyze Image",
            "NASA Explorer",
            "Exoplanet Atmosphere Visualizer",
            "Previous Analyses",
        ],
        label_visibility="collapsed",
    )

    storage_service = ResultStorageService()

    if page == "Home":
        _render_home()
    elif page == "Analyze Image":
        _render_analyze_image(storage_service)
    elif page == "NASA Explorer":
        _render_nasa_explorer(storage_service)
    elif page == "Exoplanet Atmosphere Visualizer":
        _render_exoplanet_visualizer(storage_service)
    else:
        _render_previous_analyses(storage_service)


def _render_home() -> None:
    st.title("AstroLens AI")
    st.markdown(
        "AstroLens AI analyzes astronomical images with a multi-agent pipeline: "
        "Gemini Vision identifies the object, ResearchAgent grounds the finding "
        "with scientific context, ScienceWriterAgent creates a concise report, "
        "and ResultStorageService preserves every output for review."
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Pipeline Agents", "3")
    metric_cols[1].metric("Result Files", "3")
    metric_cols[2].metric("Report Sections", "4")
    metric_cols[3].metric("Section Limit", "250 words")

    st.subheader("Architecture")
    st.graphviz_chart(
        """
        digraph astrolens {
            graph [rankdir=LR, bgcolor="transparent", pad="0.3"];
            node [shape=box, style="rounded,filled", color="#d9e2ec", fillcolor="#f8fafc", fontname="Helvetica"];
            edge [color="#64748b", arrowsize=0.8];

            Upload [label="Image Upload"];
            GeminiVision [label="GeminiService\\nVision"];
            Vision [label="VisionAgent\\nclassification + tags"];
            Knowledge [label="Knowledge Base\\nmarkdown sections"];
            Research [label="ResearchAgent\\nstructured context"];
            GeminiText [label="GeminiService\\nText"];
            Writer [label="ScienceWriterAgent\\nscience report"];
            Storage [label="ResultStorageService\\nJSON artifacts"];
            Dashboard [label="Streamlit Dashboard\\nreview + presentation"];

            Upload -> GeminiVision -> Vision;
            Vision -> Research;
            Knowledge -> Research;
            Vision -> Writer;
            Research -> Writer;
            GeminiText -> Writer;
            Vision -> Storage;
            Research -> Storage;
            Writer -> Storage;
            Storage -> Dashboard;
        }
        """
    )

    st.subheader("FIAP Presentation Flow")
    st.markdown(
        "- Upload an astronomy image and run the full agent pipeline.\n"
        "- Review classification confidence, scientific tags, and generated report sections.\n"
        "- Reopen previous analyses from persistent JSON artifacts."
    )


def _render_analyze_image(storage_service: ResultStorageService) -> None:
    st.title("Analyze Image")
    st.markdown(
        "Upload an astronomical image to run VisionAgent, ResearchAgent, and "
        "ScienceWriterAgent. Results are saved automatically after each stage."
    )

    uploaded_file = st.file_uploader(
        "Upload image",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=False,
    )

    if uploaded_file is None:
        st.info("Upload an image to start the analysis pipeline.")
        return

    preview_col, action_col = st.columns([1, 1])
    with preview_col:
        st.subheader("Image Preview")
        st.image(uploaded_file, width="stretch")

    with action_col:
        st.subheader("Pipeline")
        st.write("The uploaded image will be analyzed and stored as structured JSON.")
        run_analysis = st.button("Run Full Pipeline", type="primary")

    if not run_analysis:
        return

    image_path = _write_uploaded_file(uploaded_file)
    _run_and_render_pipeline(
        image_path=image_path,
        image_reference=uploaded_file.name,
        storage_service=storage_service,
    )


def _render_nasa_explorer(storage_service: ResultStorageService) -> None:
    st.title("NASA Explorer")
    st.markdown(
        "Search NASA's Image and Video Library and analyze a selected image "
        "with the complete AstroLens pipeline."
    )

    with st.form("nasa_search"):
        query = st.text_input(
            "Search NASA images",
            placeholder="Try: Andromeda, Orion Nebula, Jupiter",
        )
        search_submitted = st.form_submit_button("Search", type="primary")

    if search_submitted:
        if not query.strip():
            st.warning("Enter a search term.")
        else:
            try:
                with st.spinner("Searching NASA's image library..."):
                    results = NASAService().search_images(query)
                st.session_state.nasa_results = results[:_MAX_NASA_RESULTS]
            except (NASAServiceError, ValueError) as exc:
                st.session_state.nasa_results = []
                st.error(str(exc))

    results: list[NASAImage] = st.session_state.get("nasa_results", [])
    if not results:
        if search_submitted and query.strip():
            st.info("No NASA images matched this search.")
        return

    st.subheader(f"Results ({len(results)})")
    columns = st.columns(3)
    selected_image: Optional[NASAImage] = None

    for index, image in enumerate(results):
        with columns[index % len(columns)]:
            with st.container(border=True):
                st.image(image.image_url, width="stretch")
                st.markdown(f"**{image.title}**")
                st.write(_truncate_text(image.description, 220))
                if st.button(
                    "Analyze with AstroLens",
                    key=f"analyze_nasa_{image.nasa_id}_{index}",
                    width="stretch",
                ):
                    selected_image = image

    if selected_image is None:
        return

    try:
        with st.spinner("Preparing NASA image..."):
            image_details = NASAService().get_image_details(selected_image.nasa_id)
            image_path = _download_nasa_image(image_details)
    except (NASAServiceError, HTTPError, URLError, OSError, ValueError) as exc:
        st.error(f"Could not prepare the NASA image: {exc}")
        return

    st.subheader(f"Analyzing: {image_details.title}")
    _run_and_render_pipeline(
        image_path=image_path,
        image_reference=f"{image_details.nasa_id}.jpg",
        storage_service=storage_service,
    )


def _render_exoplanet_visualizer(storage_service: ResultStorageService) -> None:
    st.title("Exoplanet Atmosphere Visualizer")
    st.markdown(
        "This standalone AstroLens module interprets the visible labels in a "
        "published JWST atmospheric composition visualization for K2-18 b. It is "
        "an educational computer-vision demonstration and does not perform real "
        "scientific measurements, spectral peak fitting, or atmospheric retrieval."
    )

    image_path = _K2_18B_CHART_PATH
    if not image_path.exists():
        st.error(f"K2-18 b atmosphere chart not found: {image_path}")
        return
    if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        st.error(
            "Unsupported K2-18 b atmosphere chart format. "
            "Supported formats: .jpg, .jpeg, .png."
        )
        return

    preview_col, action_col = st.columns([1.4, 1])
    with preview_col:
        st.subheader("JWST Atmosphere Composition Chart")
        st.image(str(image_path), width="stretch")

    with action_col:
        st.subheader("Standalone Agent Flow")
        st.write(
            "Run ExoplanetSpectrumAgent on the fixed K2-18 b chart, then generate "
            "an educational report and an artist concept prompt."
        )
        run_analysis = st.button("Run Analysis", type="primary")

    if not run_analysis:
        return

    with st.status("Running exoplanet atmosphere analysis...", expanded=True) as status:
        try:
            gemini_service = GeminiService()

            st.write("Running ExoplanetSpectrumAgent...")
            atmosphere_result = ExoplanetSpectrumAgent(gemini_service).analyze(
                image_path
            )
            storage_service.save_result(image_path, atmosphere_result)

            st.write("Running ExoplanetReporter...")
            exoplanet_report = ExoplanetReporter(gemini_service).generate(
                atmosphere_result
            )
            storage_service.save_result(image_path, exoplanet_report)
            status.update(label="Exoplanet analysis complete", state="complete")
        except Exception as exc:
            status.update(label="Exoplanet analysis failed", state="error")
            st.error(str(exc))
            return

    _render_exoplanet_results(atmosphere_result, exoplanet_report)


def _run_and_render_pipeline(
    *,
    image_path: Path,
    image_reference: str,
    storage_service: ResultStorageService,
) -> None:
    with st.status("Running AstroLens pipeline...", expanded=True) as status:
        try:
            gemini_service = GeminiService()

            st.write("Running VisionAgent...")
            vision_result = VisionAgent(gemini_service).analyze(str(image_path))
            storage_service.save_result(image_reference, vision_result)

            st.write("Running ResearchAgent...")
            research_result = ResearchAgent().research(vision_result)
            storage_service.save_result(image_reference, research_result)

            st.write("Running ScienceWriterAgent...")
            science_report = ScienceWriterAgent(gemini_service).write(
                vision_result, research_result
            )
            storage_service.save_result(image_reference, science_report)
            status.update(label="Analysis complete", state="complete")
        except Exception as exc:
            status.update(label="Analysis failed", state="error")
            st.error(str(exc))
            return

    _render_analysis_results(vision_result, research_result, science_report)


def _render_previous_analyses(storage_service: ResultStorageService) -> None:
    st.title("Previous Analyses")
    st.markdown("Load saved JSON artifacts from previous pipeline runs.")

    analyses = _list_saved_analyses(storage_service)
    if not analyses:
        st.info("No saved analysis folders found yet.")
        return

    selected_name = st.selectbox("Saved analyses", analyses)
    image_reference = f"{selected_name}.jpg"

    vision_result = _safe_load(storage_service, image_reference, VisionAnalysisResult)
    research_result = _safe_load(storage_service, image_reference, ResearchResult)
    science_report = _safe_load(storage_service, image_reference, ScienceReport)

    status_cols = st.columns(3)
    status_cols[0].metric("Vision", "Saved" if vision_result else "Missing")
    status_cols[1].metric("Research", "Saved" if research_result else "Missing")
    status_cols[2].metric("Science Report", "Saved" if science_report else "Missing")

    if vision_result and research_result and science_report:
        _render_analysis_results(vision_result, research_result, science_report)
        return

    st.warning("This analysis does not have all result files yet.")
    with st.expander("Available JSON"):
        result_dir = storage_service.base_dir / selected_name
        for path in sorted(result_dir.glob("*.json")):
            st.caption(path.name)
            st.json(json.loads(path.read_text(encoding="utf-8")))


def _render_analysis_results(
    vision_result: VisionAnalysisResult,
    research_result: ResearchResult,
    science_report: ScienceReport,
) -> None:
    st.divider()
    st.subheader("Classification")

    metric_cols = st.columns(3)
    metric_cols[0].metric("Classification", vision_result.classification)
    metric_cols[1].metric("Confidence", f"{vision_result.confidence:.0%}")
    metric_cols[2].metric("Research Source", research_result.source)

    if vision_result.scientific_tags:
        st.markdown("**Scientific Tags**")
        st.caption(", ".join(vision_result.scientific_tags))

    st.subheader("Science Report")
    summary_col, exploration_col = st.columns(2)
    with summary_col:
        _render_report_section(
            "Scientific Summary", science_report.scientific_summary
        )
    with exploration_col:
        _render_report_section(
            "Space Exploration Importance",
            science_report.space_exploration_importance,
        )

    earth_col, curiosity_col = st.columns(2)
    with earth_col:
        _render_report_section("Impact on Earth", science_report.earth_impact)
    with curiosity_col:
        _render_report_section("Curiosities", science_report.curiosities)

    with st.expander("Structured JSON artifacts"):
        tab_vision, tab_research, tab_report = st.tabs(
            ["Vision", "Research", "Science Report"]
        )
        tab_vision.json(asdict(vision_result))
        tab_research.json(asdict(research_result))
        tab_report.json(asdict(science_report))


def _render_exoplanet_results(
    atmosphere_result: ExoplanetAtmosphereResult,
    exoplanet_report: ExoplanetReport,
) -> None:
    st.divider()
    st.subheader("Exoplanet Agent JSON Output")

    metric_cols = st.columns(3)
    metric_cols[0].metric("Planet", atmosphere_result.planet)
    metric_cols[1].metric("Planet Type", atmosphere_result.planet_type or "Unknown")
    metric_cols[2].metric(
        "Interpretation Confidence",
        f"{atmosphere_result.scientific_confidence:.0%}",
    )

    if atmosphere_result.detected_molecules:
        st.markdown("**Detected Molecules**")
        st.caption(", ".join(atmosphere_result.detected_molecules))

    st.json(asdict(atmosphere_result))

    st.subheader("Human-Readable Report")
    summary_col, atmosphere_col = st.columns(2)
    with summary_col:
        _render_report_section("Planet Summary", exoplanet_report.planet_summary)
    with atmosphere_col:
        _render_report_section(
            "Atmosphere Description", exoplanet_report.atmosphere_description
        )

    habitability_col, relevance_col = st.columns(2)
    with habitability_col:
        _render_report_section("Habitability Notes", exoplanet_report.habitability_notes)
    with relevance_col:
        _render_report_section(
            "Scientific Relevance", exoplanet_report.scientific_relevance
        )

    st.subheader("Artist Concept Prompt")
    st.code(exoplanet_report.artist_concept_prompt, language="text")


def _render_report_section(title: str, body: str) -> None:
    st.markdown(f"**{title}**")
    st.write(body or "Not available.")


def _list_saved_analyses(storage_service: ResultStorageService) -> list[str]:
    if not storage_service.base_dir.exists():
        return []
    return sorted(
        path.name
        for path in storage_service.base_dir.iterdir()
        if path.is_dir() and any(path.glob("*.json"))
    )


def _safe_load(
    storage_service: ResultStorageService,
    image_reference: str,
    result_type: type[VisionAnalysisResult] | type[ResearchResult] | type[ScienceReport],
) -> Optional[VisionAnalysisResult | ResearchResult | ScienceReport]:
    try:
        return storage_service.load_result(image_reference, result_type)
    except FileNotFoundError:
        return None


def _write_uploaded_file(uploaded_file: object) -> Path:
    suffix = Path(uploaded_file.name).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(uploaded_file.getbuffer())
        return Path(handle.name)


def _download_nasa_image(image: NASAImage) -> Path:
    request = Request(
        image.image_url,
        headers={"User-Agent": "AstroLens-AI/1.0"},
    )
    with urlopen(request, timeout=30) as response:
        content_type = response.headers.get_content_type()
        if not content_type.startswith("image/"):
            raise ValueError(f"NASA asset is not an image ({content_type}).")

        image_bytes = response.read(_MAX_NASA_IMAGE_BYTES + 1)
        if len(image_bytes) > _MAX_NASA_IMAGE_BYTES:
            raise ValueError("NASA image exceeds the 20 MB download limit.")

    suffix = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }.get(content_type, ".jpg")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(image_bytes)
        return Path(handle.name)


def _truncate_text(text: str, max_characters: int) -> str:
    normalized = " ".join(text.split())
    if not normalized:
        return "No description available."
    if len(normalized) <= max_characters:
        return normalized
    return f"{normalized[: max_characters - 3].rstrip()}..."


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 2rem;
            max-width: 1180px;
        }
        [data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 0.85rem 1rem;
        }
        div.stButton > button {
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
