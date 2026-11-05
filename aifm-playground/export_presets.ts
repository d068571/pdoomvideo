// Dump the website's parameter presets (constants/parameters.ts) to JSON.
import { writeFileSync } from 'fs';
import { PRESET_BASELINES, PARAMETER_PRESETS, CURRENT_DEFAULT_BASELINE_ID } from '../constants/parameters';
writeFileSync(process.argv[2] ?? 'playground/presets.json', JSON.stringify(
  { default: CURRENT_DEFAULT_BASELINE_ID, menu: PARAMETER_PRESETS, presets: PRESET_BASELINES }, null, 2));
