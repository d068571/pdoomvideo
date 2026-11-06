#!/usr/bin/env bash
# Monte Carlo rollouts of the three forecasters' Q2-2026 configs (unchanged), for METR conditioning.
set -e
cd "$(dirname "$0")/../_ext/aifm-public"
source .venv/bin/activate
for spec in "daniel 1000" "eli 600" "brendan 600"; do
  set -- $spec
  python scripts/pipelines/batch_rollout.py --config config/sampling_config_q2_$1.yaml \
    --num-samples $2 --num-workers 4 --seed 2026 --mp-context spawn --skip-summary \
    --output-dir outputs/metr/$1 > outputs/metr_$1.log 2>&1
  echo "$1 done $(date)"
done
