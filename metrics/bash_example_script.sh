#!/bin/bash
echo "
metrics:
- metric: "metric003"
  description: "this is a description"
  type: "gauge"
  value: 3434
  labels:
  - label: "label001"
    value: 233

- metric: "metric004"
  description: "this is a description"
  type: "gauge"
  value: 323
  labels:
  - label: "label001"
    value: 233
"
