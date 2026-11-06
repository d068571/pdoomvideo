# AI Futures Model playground

A local, scriptable copy of the model behind <https://www.aifuturesmodel.com/>.

## Is this the same model as the website?

Yes. Checked on 2026-11-05 against `AI-Futures-Project/aifm-public` @ `1c40ecd` ("Initial release"):

| Check | Result |
|---|---|
| `POST /api/compute`, default params, live vs local | all ~700 KB of output identical (max milestone Δ ≈ 1e-12 yr) |
| 3 non-default scenarios (time-horizon / revenue anchor, slow taste) | max milestone Δ ≤ 5e-8 yr |
| `/api/parameter-config`, `/api/sampling-config` | byte-identical |
| Homepage (local Next.js vs live) | same forecast (AC 10/2027, ASI 12/2028), same charts |
| `aifm.params()` vs what the browser POSTs on the homepage | identical dict |
| `python -m pytest` | 635 passed |

Caveats:
* **/forecast** shows *precomputed* Monte Carlo runs (`app/forecast/data/simulations/`), typically many thousands of samples. You can rerun them with `aifm.monte_carlo(...)`, but results depend on the sample count and seed.
* The UI's compute-growth knobs (`constant_training_system_performance_growth_rate`, `slowdown_year`, `post_slowdown_…`) are **disabled upstream** (`progress_model/time_series.py`, "TEMPORARILY DISABLED"), on the live site too. Use `aifm.compute_scenario()` / `custom_time_series` for compute scenarios.
* Two local fixes were needed:
  * `/api/default-data` called a helper that is missing from the public repo. It is patched in `api/index.py`.
  * Multi-worker Monte Carlo needs `--mp-context spawn` on Python 3.14. `aifm.monte_carlo` passes it.

## Setup (fresh machine / new session)

From the `pdoomvideo` repo root (the script copies these playground files into the clone's `playground/`):

```bash
bash aifm-playground/setup.sh ~/aifm-public          # clones, pins 1c40ecd, patches, installs py3.14 venv + npm deps
cd ~/aifm-public && source .venv/bin/activate
```

## Use it

```python
import playground.aifm as aifm             # run from the repo root

r = aifm.run()                             # homepage forecast (Daniel's median, 08/16/26)
r.milestones                               # dates of AC, SAR, TED-AI, ASI, ...
r.series                                   # yearly-ish trajectory: progress, horizon, multipliers...
aifm.list_presets()                        # Daniel / Eli / Brendan / AI-2027-like
aifm.compare(aifm.run(), aifm.run('eli-08-16-26', label='Eli'))
aifm.run(excess_uplift_doubling_time=10, ai_research_taste_slope=1.5)   # move the sliders
aifm.sweep('excess_uplift_doubling_time', [3, 5, 8, 12])
aifm.run(custom_time_series=aifm.compute_scenario(after=2027, growth_multiplier=0.5))
aifm.plot(r, column='aiSwProgressMultRefPresentDay', logy=True)
m = aifm.model()                           # raw ProgressModel for internals

run_dir = aifm.monte_carlo('config/sampling_config_q2_daniel.yaml', num_samples=200)
aifm.mc_summary(run_dir)                   # p10/p50/p90 + P(by year) per milestone
```

Parameters use **API units**. For example, `ac_time_horizon_minutes` is in minutes, while the website slider stores log10(minutes). Bounds are in `/api/parameter-config`; defaults are in `progress_model/config.py`.

* Notebook: `jupyter lab playground/playground.ipynb`
* Full website locally: `bash playground/start.sh`, then open <http://localhost:3000>
* Presets: refresh from the TS source with `npx tsx playground/export_presets.ts`
