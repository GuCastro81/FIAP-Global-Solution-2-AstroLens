# Exoplanet Atmosphere Visualizer

## Purpose

Exoplanet Atmosphere Visualizer is a standalone AstroLens proof of concept for
interpreting the published JWST atmospheric composition chart for K2-18 b:

`data/images/exoplanets/k2-18b/atmosphere_composition.jpg`

The module demonstrates generative AI, computer vision, multi-agent systems,
scientific data interpretation, space exploration, and exoplanet research. It is
educational only. It does not perform atmospheric retrieval, spectral peak
fitting, or scientific calculations.

## Architecture

The module follows the existing AstroLens structure:

- `src/agents/exoplanet_spectrum_agent.py` contains the isolated vision agent.
- `src/reporting/exoplanet_reporter.py` contains the isolated text reporter.
- `src/reporting/artist_concept_prompt_enhancer.py` contains the isolated
  prompt enhancement layer for future image-generation use.
- `ResultStorageService` persists the new dataclass outputs under the existing
  `data/analysis_results/<image_name>/` convention.
- `app.py` exposes a new Streamlit navigation option:
  `Exoplanet Atmosphere Visualizer`.

The existing VisionAgent, ResearchAgent, ScienceWriterAgent, NASA Explorer, and
image-analysis workflow remain separate.

## Agent Flow

1. The Streamlit page loads only the K2-18 b atmosphere composition image.
2. `ExoplanetSpectrumAgent` validates that the file exists, has a supported
   `.jpg`, `.jpeg`, or `.png` extension, and has a loadable image signature.
3. The agent sends the chart to Gemini Vision with instructions to interpret
   only visible labels and return strict JSON.
4. The agent parses and validates:

```json
{
  "planet": "K2-18 b",
  "planet_type": "Sub-Neptune",
  "detected_molecules": ["Methane", "Carbon Dioxide", "Dimethyl Sulfide"],
  "scientific_confidence": 0.89,
  "summary": "The atmosphere shows evidence of methane and carbon dioxide."
}
```

5. `ExoplanetReporter` generates an educational report with uncertainty-aware
   language and a final `artist_concept_prompt`.
6. `ArtistConceptPromptEnhancer` transforms the basic artist concept prompt into
   a richer visual prompt while preserving scientific caution.
7. The agent and report outputs are saved by `ResultStorageService`.

## Example Outputs

Expected agent JSON:

```json
{
  "planet": "K2-18 b",
  "planet_type": "Sub-Neptune",
  "detected_molecules": [
    "Methane",
    "Carbon Dioxide",
    "Dimethyl Sulfide"
  ],
  "scientific_confidence": 0.89,
  "summary": "The chart labels evidence associated with methane and carbon dioxide, with uncertainty around dimethyl sulfide."
}
```

Expected report JSON:

```json
{
  "planet_summary": "K2-18 b is commonly described as a sub-Neptune exoplanet and is shown here through a JWST atmosphere visualization.",
  "atmosphere_description": "The chart labels methane and carbon dioxide, with dimethyl sulfide presented cautiously as an uncertain interpretation.",
  "habitability_notes": "The visualization can support discussion of habitability questions, but it does not establish that the planet is habitable.",
  "scientific_relevance": "K2-18 b is relevant because JWST observations help researchers study exoplanet atmospheres beyond the Solar System.",
  "artist_concept_prompt": "A scientifically plausible artist concept of K2-18 b, a sub-Neptune exoplanet with an atmosphere containing methane and carbon dioxide, orbiting a red dwarf star, NASA-style space illustration."
}
```

Expected enhanced artist prompt JSON:

```json
{
  "enhanced_artist_prompt": "A scientifically plausible NASA/JWST-inspired artist concept of K2-18 b...",
  "visual_style": "NASA/JWST-inspired artist concept, scientifically plausible, realistic astrophysics, cinematic lighting, high detail, educational scientific visualization",
  "scientific_constraints": [
    "Represent K2-18 b as a sub-Neptune exoplanet, not an Earth twin.",
    "Include methane and carbon dioxide as atmospheric components.",
    "Describe dimethyl sulfide (DMS) only as an uncertain candidate atmospheric feature."
  ],
  "negative_prompt": "fantasy landscape, alien cities, spaceships, humanoids, exaggerated colors, cartoon style, impossible surface details, unsupported biological claims"
}
```

## Artist Concept Prompt Enhancer

### Purpose

`ArtistConceptPromptEnhancer` improves the basic `artist_concept_prompt`
produced by `ExoplanetReporter`. The enhanced prompt is designed for a future
image-generation module, but this component does not generate images.

The enhancer adds richer visual direction, including a dense atmosphere,
atmospheric haze, cloud layers, red dwarf illumination, deep space background,
and possible liquid reservoirs or ocean-like regions hidden beneath clouds.

### Input Schema

```json
{
  "planet_name": "K2-18 b",
  "detected_molecules": ["Methane", "Carbon Dioxide", "Dimethyl Sulfide"],
  "exoplanet_report": {
    "planet_summary": "",
    "atmosphere_description": "",
    "habitability_notes": "",
    "scientific_relevance": "",
    "artist_concept_prompt": ""
  },
  "original_artist_concept_prompt": ""
}
```

### Output Schema

```json
{
  "enhanced_artist_prompt": "",
  "visual_style": "",
  "scientific_constraints": [],
  "negative_prompt": ""
}
```

### Scientific Limitations

- The enhanced prompt is a visualization prompt, not a scientific result.
- It must not claim confirmed habitability, confirmed oceans, or confirmed life.
- Dimethyl sulfide must be described only as a possible or uncertain candidate
  atmospheric feature.
- Visual elements should remain scientifically plausible and educational.
- The negative prompt excludes fantasy landscapes, alien cities, spaceships,
  humanoids, exaggerated colors, cartoon style, impossible surface details, and
  unsupported biological claims.

### Future Use With Image Generation

The enhanced prompt can be passed to a future image-generation module after
review. That future module should keep the same scientific constraints and avoid
presenting generated artwork as observational evidence.

## Scientific Limitations

- The module interprets a visualization, not raw JWST spectra.
- The module reads visible labels and summaries only.
- The module does not fit spectral peaks.
- The module does not calculate abundances, temperatures, pressures, or
  atmospheric models.
- Gemini output must be treated as educational interpretation and may contain
  uncertainty or mistakes.
- Any claim about habitability must remain cautious and explicitly uncertain.

## Future Improvements

- Add review controls for educators to approve or edit generated sections.
- Add side-by-side comparison with official explanatory text when available.
- Add cached demo outputs for offline classroom presentations.
- Add support for additional JWST datasets through separate isolated modules.
- Add an image-generation module that consumes `artist_concept_prompt` without
  changing this analysis flow.
- Add an optional image-generation module that consumes
  `enhanced_artist_prompt` after scientific review.

## Future Quantum Astrophysics Applications

This section is conceptual only. No implementation is included.

1. Quantum-assisted exoplanet atmosphere simulation could explore future methods
   for modeling complex molecular interactions in planetary atmospheres.
2. Neutron star interior modeling could investigate whether quantum algorithms
   help approximate dense-matter equations and high-energy astrophysical states.
3. Quantum optimization for astrophysical calculations could support future
   scheduling, parameter search, or model-selection workflows.
4. Future integration with additional JWST datasets could provide a broader
   educational environment for comparing exoplanet atmosphere visualizations.
