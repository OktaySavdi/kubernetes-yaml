# Cluster Intelligence Operator

## Overview
AI/ML-powered anomaly detection and predictive failure analysis with ServiceNow/Teams integration.

## Features
- ✅ AI-powered anomaly detection (CPU/Memory spikes, pod restarts, evictions)
- ✅ Predictive failure analysis with recommendations
- ✅ Priority-based ServiceNow ticketing (P1/P2/P3)
- ✅ Multi-layer monitoring (nodes, pods, events, storage)
- ✅ Baseline comparison with spike detection
- ✅ Runs every 15 minutes
- ✅ ConfigMap-based configuration

## Quick Start

### 1. Update Configuration
Edit ConfigMap in `cluster-intelligence-operator.yaml`:
```yaml
data:
  # AI/ML Thresholds
  NODE_CPU_SPIKE_THRESHOLD: "85"
  NODE_MEMORY_SPIKE_THRESHOLD: "85"
  POD_RESTART_ANOMALY: "5"
  EVICTION_ANOMALY_COUNT: "3"
  
  # Baselines (update based on your cluster)
  BASELINE_CPU_AVG: "45"
  BASELINE_MEMORY_AVG: "60"
  SPIKE_DETECTION_THRESHOLD: "30"
  
  # ServiceNow Priority Thresholds
  PRIORITY_CRITICAL_THRESHOLD: "5"    # ≥5 anomalies = P1
  PRIORITY_HIGH_THRESHOLD: "3"        # ≥3 anomalies = P2
  
  # Feature Flags
  ENABLE_SERVICENOW: "true"
  ENABLE_TEAMS_ALERTS: "true"
  ENABLE_PREDICTIONS: "true"
```

### 2. Update Credentials
Edit Secret in `cluster-intelligence-operator.yaml`:
```yaml
stringData:
  TEAMS_WEBHOOK_URL: "https://your-webhook-url"
  SERVICENOW_INSTANCE: "your-instance.service-now.com"
  SERVICENOW_USER: "api_user"
  SERVICENOW_PASS: "api_password"
```

### 3. Deploy
```bash
kubectl apply -f cluster-intelligence-operator.yaml
```

### 4. Test Manually
```bash
kubectl create job intel-test --from=cronjob/cluster-intelligence -n gt-operators
kubectl logs -n gt-operators job/intel-test
```

## AI Detection Logic

### Baseline Comparison
```
Current CPU: 80%
Baseline CPU: 45%
Spike: 80 - 45 = 35%

If spike > 30% → ANOMALY DETECTED
Prediction: "Node may become unresponsive"
```

### Pattern Recognition
- **Pod Restarts >5**: Analyze crash reason (OOM vs Error)
- **Evictions >3**: Detect resource pressure patterns
- **Pressure Conditions**: Predict cascading failures

## Anomaly Types

### Critical Anomalies (ServiceNow P1)
| Type | Detection | Prediction |
|------|-----------|------------|
| CPU Spike | Current >85% AND Spike >30% | Node unresponsiveness |
| Memory Spike | Current >85% AND Spike >30% | OOM kills likely |
| Disk Pressure | DiskPressure = True | Disk failure imminent |
| High Evictions | >3 in 30min | Resource exhaustion |

### Warning Anomalies (Teams Only)
| Type | Detection | Action |
|------|-----------|--------|
| Memory Pressure | MemoryPressure = True | Monitor evictions |
| Pod Restart Loop | >5 restarts | Check OOM/errors |
| Image Pull Failures | >5 failures | Check registry |
| Scheduling Failures | >5 failures | Check capacity |

## ServiceNow Integration

### Priority Assignment
- **P1 (Critical)**: ≥5 anomalies detected
- **P2 (High)**: 3-4 anomalies detected
- **P3 (Moderate)**: 1-2 anomalies detected

### Ticket Content
- Anomaly details (type, resource, metrics)
- AI predictions with confidence
- Recommendations for remediation
- Cluster info (name, timestamp, counts)

### Deduplication
- Checks last 6 hours for existing tickets (configurable via `DUPLICATE_DETECTION_HOURS`)
- Updates existing ticket with work notes
- Prevents ticket spam

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| NODE_CPU_SPIKE_THRESHOLD | 85 | CPU % for spike detection |
| NODE_MEMORY_SPIKE_THRESHOLD | 85 | Memory % for spike detection |
| POD_RESTART_ANOMALY | 5 | Restart count threshold |
| EVICTION_ANOMALY_COUNT | 3 | Eviction count threshold |
| BASELINE_CPU_AVG | 45 | Normal CPU % (update for your cluster) |
| BASELINE_MEMORY_AVG | 60 | Normal Memory % (update for your cluster) |
| SPIKE_DETECTION_THRESHOLD | 30 | % increase from baseline = spike |
| PRIORITY_CRITICAL_THRESHOLD | 5 | Anomalies for P1 ticket |
| PRIORITY_HIGH_THRESHOLD | 3 | Anomalies for P2 ticket |
| DUPLICATE_DETECTION_HOURS | 6 | Hours to check for existing tickets |
| ENABLE_SERVICENOW | true | Enable ServiceNow integration |
| ENABLE_TEAMS_ALERTS | true | Enable Teams notifications |
| ENABLE_PREDICTIONS | true | Enable AI predictions |

## Tuning Baselines

### Calculate Your Cluster's Baseline
```bash
# Check average CPU/Memory usage
kubectl top nodes

# Example output:
# worker-01: 42% CPU, 58% Memory
# worker-02: 48% CPU, 62% Memory
# Average: ~45% CPU, ~60% Memory

# Update ConfigMap with these values
BASELINE_CPU_AVG: "45"
BASELINE_MEMORY_AVG: "60"
```

### Adjust Sensitivity
```yaml
# More sensitive (detect earlier, more alerts)
SPIKE_DETECTION_THRESHOLD: "20"
POD_RESTART_ANOMALY: "3"

# Less sensitive (fewer false positives)
SPIKE_DETECTION_THRESHOLD: "40"
POD_RESTART_ANOMALY: "10"
```

## Sample Output

```
=== Summary ===
Total Anomalies: 3 (Critical: 2, Warning: 1)
Predictions Made: 3

=== Detected Anomalies ===
🔴 CRITICAL: Node CPU Spike
   Resource: worker-02
   Details: CPU: 92% (spike: 47% from baseline)

🔴 CRITICAL: High Eviction Rate
   Evictions: 5

🟠 WARNING: Pod Restart Anomaly
   Resource: myapp/frontend
   Restarts: 7 (OOMKilled)

=== AI Predictions ===
- Node worker-02 may become unresponsive
- Cluster resource exhaustion - scale up nodes
- Pod myapp/frontend needs memory limit increase

=== ServiceNow ===
✅ Ticket Created: INC0123456 (Priority: P1)
```

## Troubleshooting

**No anomalies detected:**
- Cluster is healthy ✅
- Thresholds too conservative (lower them)
- Baselines don't match your usage (update them)

**Too many false positives:**
```yaml
# Increase thresholds
NODE_CPU_SPIKE_THRESHOLD: "90"
SPIKE_DETECTION_THRESHOLD: "40"
POD_RESTART_ANOMALY: "10"
```

**No ServiceNow ticket:**
- Verify `ENABLE_SERVICENOW: "true"` in ConfigMap
- Check SERVICENOW_INSTANCE is not placeholder
- Validate credentials in Secret
- Review logs for API errors

**No Teams notification:**
- Check `ENABLE_TEAMS_ALERTS: "true"` in ConfigMap
- Verify TEAMS_WEBHOOK_URL in Secret
