Across these 12 chip projects, I designed the analog compute-in-memory macros and was responsible for system design and integration. Several of the chips incorporate design ideas I originated. I also developed our lab’s FPGA-based chip test platform.

<article class="tapeout" markdown="1">
<div markdown="1">

## Mixed-precision PCM chip for embodied AI

I designed the compute macro that supports both analog and digital operation, along with the PCM write circuitry and the circuits that compensate for conductance drift.

[IEDM 2025 paper](https://ieeexplore.ieee.org/document/11353523) · [ESSERC 2026 paper](../publications/#esserc-2026)

</div>
<img src="images/tapeout-mixed-precision-pcm.webp" width="640" height="451" alt="Die micrograph of the 256 Kb mixed-precision PCM chip">
</article>

<article class="tapeout" markdown="1">
<div markdown="1">

## First-generation charge-domain RRAM chip for AI inference

I designed the compute cell, the charge-sharing array and its multibit readout. I also evaluated how chip-level compute errors affected a ternary BERT model.

[ESSERC 2025 paper](https://ieeexplore.ieee.org/document/11214056)

</div>
<img src="images/tapeout-charge-domain-rram.webp" width="640" height="493" loading="lazy" alt="Die micrograph of the 1 Mb charge-domain RRAM chip">
</article>

## Additional tape-outs

<div class="tapeout-gallery">
<figure>
  <img src="images/tapeout-neural-dynamics.webp" width="607" height="616" loading="lazy" alt="PCM compute core and time-step drift array">
  <figcaption>
    <h3>PCM chip for neural dynamics</h3>
    <p>144 Kb · <a href="https://www.science.org/doi/10.1126/science.aee6277">Science 2026 paper</a></p>
  </figcaption>
</figure>

<figure>
  <img src="images/tapeout-llm-inference.webp" width="800" height="408" loading="lazy" alt="Die of the PCM processor for attention and KV-cache storage">
  <figcaption>
    <h3>PCM processor for long-context LLM inference</h3>
    <p>288 Mb · IEDM 2026</p>
  </figcaption>
</figure>

<figure>
  <img src="images/tapeout-neurostimulation.webp" width="723" height="1038" loading="lazy" alt="Paired micrographs of the RRAM processor and VO₂ stimulation chip">
  <figcaption>
    <h3>RRAM decision processor and VO₂ neural stimulation chip</h3>
    <p>8 Mb RRAM and 24 VO₂ devices · IEDM 2026</p>
  </figcaption>
</figure>

<figure>
  <img src="images/tapeout-private-edge-inference.webp" width="800" height="418" loading="lazy" alt="Die of the PCM chip for local inference">
  <figcaption>
    <h3>PCM chip for private edge inference</h3>
    <p>2 Mb · IEDM 2026</p>
  </figcaption>
</figure>

<figure>
  <img src="images/tapeout-wear-resilient-rram.webp" width="469" height="640" loading="lazy" alt="Die of the 16-core wear-resilient RRAM processor">
  <figcaption>
    <h3>Wear-resilient RRAM processor for on-chip learning</h3>
    <p>8 Mb · ESSERC 2026</p>
  </figcaption>
</figure>

<figure>
  <img src="images/tapeout-second-generation-charge-domain.webp" width="472" height="640" loading="lazy" alt="Analog compute die of the second-generation charge-domain design">
  <figcaption>
    <h3>Second-generation charge-domain RRAM chip</h3>
    <p>128 Kb · ESSERC 2026</p>
  </figcaption>
</figure>

<figure>
  <img src="images/tapeout-multimodal-fusion.webp" width="517" height="487" loading="lazy" alt="Die of the 64-core PCM processor">
  <figcaption>
    <h3>64-core PCM processor for multimodal fusion</h3>
    <p>9 Mb · <a href="https://ieeexplore.ieee.org/document/11353552">IEDM 2025 paper</a></p>
  </figcaption>
</figure>

<figure>
  <img src="images/tapeout-embodied-learning.webp" width="263" height="640" loading="lazy" alt="Die of the RRAM accelerator for on-chip model updates">
  <figcaption>
    <h3>RRAM accelerator for embodied self-supervised learning</h3>
    <p>8 Mb · <a href="https://ieeexplore.ieee.org/document/11353856">IEDM 2025 paper</a></p>
  </figcaption>
</figure>

<figure>
  <img src="images/tapeout-scalable-charge-domain.webp" width="640" height="395" loading="lazy" alt="Charge-domain PCM macro with local compute units">
  <figcaption>
    <h3>Scalable charge-domain PCM macro</h3>
    <p>64 Kb · <a href="https://doi.org/10.1109/ICTA68203.2025.11329816">ICTA 2025 paper</a> · ICAS 2026</p>
  </figcaption>
</figure>

<figure>
  <img src="images/tapeout-neural-decoding.webp" width="640" height="387" loading="lazy" alt="Die of the dual-mode PCM chip for neural manifold learning">
  <figcaption>
    <h3>Dual-mode PCM chip for brain-signal decoding</h3>
    <p>288 Kb · <a href="https://ieeexplore.ieee.org/document/10873590">IEDM 2024 paper</a></p>
  </figcaption>
</figure>

</div>
