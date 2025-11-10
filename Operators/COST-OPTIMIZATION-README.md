# Cost Optimization Operator

## Overview
Analyzes resource usage to identify over-provisioned pods and idle resources with right-sizing recommendations.

## Features
- ✅ Over-provisioning detection (<50% CPU/Memory usage)
- ✅ Idle resource detection (<10m CPU, <50Mi Memory)
- ✅ Right-sizing recommendations (actual × 1.2 headroom)
- ✅ Cost savings calculation (CPU/Memory reclamation)
- ✅ System namespace exclusion (platform components filtered)
- ✅ Teams integration (daily optimization reports)
- ✅ Missing resource requests detection
- ✅ Runs daily at 6 AM UTC

## Quick Start

### 1. Update Configuration
Edit Secret in `cost-optimization-operator.yaml`:
```yaml
stringData:
  TEAMS_WEBHOOK_URL: "https://your-webhook-url"
```

Edit CronJob environment:
```yaml
env:
  - name: CLUSTER_NAME
    value: "your-cluster-name"
```

### 2. Deploy
```bash
kubectl apply -f cost-optimization-operator.yaml
```

### 3. Test Manually
```bash
kubectl create job cost-test --from=cronjob/cost-optimization -n gt-operators
kubectl logs -n gt-operators job/cost-test
```

## Pod Categories

| Category | Criteria | Action |
|----------|----------|--------|
| **✅ Optimized** | ≥50% CPU AND ≥50% Memory usage | No action needed |
| **📊 Over-Provisioned** | <50% CPU OR <50% Memory usage | Reduce requests (actual × 1.2) |
| **💤 Idle** | <10m CPU AND <50Mi Memory | Scale down or remove |
| **⚠️ No Requests** | Missing CPU/Memory requests | Add requests immediately |

## Analysis Logic

### Right-Sizing Formula
```
Recommended Request = Actual Usage × 1.2 (20% headroom)

Example:
  Actual CPU: 30m
  Current Request: 10000m (10 cores)
  Recommended: 36m (30m × 1.2)
  Savings: 9964m (9.96 cores)
```

### System Namespace Exclusion
Auto-excluded namespaces (platform components):
- `kube-system`, `kube-public`, `kube-node-lease`
- `tkg-system`, `vmware-system-*`, `tanzu-*`
- `avi-system`, `secretgen-controller`

## Sample Output

```
=== Cost Optimization Summary ===
Total Pods Analyzed: 10
Over-Provisioned: 1 (10%)
Idle Pods: 0 (0%)
Pods Without Requests: 0

Potential Savings:
  CPU: 9964m (9.96 cores)
  Memory: 0Mi

=== Top Over-Provisioned ===
📊 myapp/frontend-abc123
   Current: CPU:30m/10000m(0%), Memory:100Mi/512Mi(19%)
   Recommend: CPU=36m, Memory=120Mi
   Savings: CPU=9964m, Memory=392Mi
```

### Interpreting Results

**Format**: `Actual/Requested (Percentage)`

**Action Guide**:
- **<50% usage**: Over-provisioned → Reduce requests
- **50-90% usage**: Well-sized → No action
- **>90% usage**: Under-provisioned → Increase requests

**Examples**:
```
Over-Provisioned (reduce):
  CPU:20m/1000m(2%) → Reduce to 24m

Well-Sized (no action):
  CPU:60m/100m(60%) → Keep as-is

Under-Provisioned (increase):
  CPU:950m/1000m(95%) → Increase to 1200m
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| CPU_OVERPROVISIONED_THRESHOLD | 50 | % usage for over-provisioning detection |
| MEMORY_OVERPROVISIONED_THRESHOLD | 50 | % usage for over-provisioning detection |
| IDLE_CPU_THRESHOLD | 10 | CPU (millicores) for idle detection |
| IDLE_MEMORY_THRESHOLD | 50 | Memory (Mi) for idle detection |
| EXCLUDED_NAMESPACES | (see above) | System namespaces to skip |

### Schedule Configuration
```yaml
schedule: "0 6 * * *"     # Daily at 6 AM (default)
schedule: "0 */12 * * *"  # Every 12 hours
schedule: "0 0 * * 1"     # Weekly on Monday
```

## Teams Alert Format

```
💰 Cost Optimization Report

Summary:
- Total Pods: 10
- Over-Provisioned: 1 pods
- Idle: 0 pods

Potential Savings:
- CPU: 9964m
- Memory: 392Mi

Top Over-Provisioned:
- myapp/frontend: Recommend:CPU=36m,Memory=120Mi

⚠️ Review and right-size resources.
```

## Troubleshooting

**No metrics available:**
- Verify metrics-server is running: `kubectl get deployment metrics-server -n kube-system`
- Check pod metrics: `kubectl top pods -A`

**No over-provisioned pods found:**
- Resources are well-sized ✅
- Lower thresholds for more sensitive detection
- Check excluded namespaces aren't hiding workloads

**Pods without requests:**
- High priority issue - add requests immediately
- Use recommendations from report to set initial values