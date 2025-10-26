# SPICA Experiment API

## Registering a New Experiment
POST /api/spica/experiments
body: { "name": str, "domain": str, "pipeline": path, "variant": str }
