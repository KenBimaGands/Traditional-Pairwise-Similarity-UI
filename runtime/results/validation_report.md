# Pilot run validation

82/82 screenshots extracted successfully; no missing or corrupt dataset images.
Five unittest tests passed. All 82 exported records passed ID alignment, palette count/proportion, finite Lab, density, box-boundary, and layout validation. Smoke and full-run numerical results matched exactly for all three selected screens.
82 full-run and 3 smoke six-panel plots generated.

foreground_coverage: min=0.048284, max=0.961439
edge_density: min=0.006974, max=0.108519
component_count: min=6.000000, max=204.000000

Observed smoke limitations: source attribution footers and device chrome contribute to all relevant descriptors; pale outlines can be missed; chart rectangles include empty interiors. Full outputs passed numerical checks; only smoke plots and one additional full-run plot were visually inspected.
No dataset files were modified. No pairwise similarity or graph work was implemented.
