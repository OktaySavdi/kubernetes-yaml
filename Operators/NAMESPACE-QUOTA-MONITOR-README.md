# Namespace Quota Monitor

## Overview
Monitors ResourceQuota usage across all namespaces with ServiceNow/Teams alerts.

## Features
- ✅ Monitors CPU, Memory, Pods, PVCs, Services quotas
- ✅ ServiceNow P1 tickets at ≥95% quota
- ✅ Teams alerts at ≥90% quota
- ✅ Top 3 resource consumers included
- ✅ Runs hourly
- ✅ ConfigMap-based configuration

## Quick Start

### 1. Update Configuration
Edit ConfigMap in `namespace-quota-monitor.yaml`:
```yaml
data:
  CLUSTER_NAME: "your-cluster-name"
  CRITICAL_THRESHOLD: "95"
  WARNING_THRESHOLD: "90"
  ENABLE_SERVICENOW: "true"
  ENABLE_TEAMS_ALERTS: "true"
```

### 2. Update Credentials
Edit Secret in `namespace-quota-monitor.yaml`:
```yaml
stringData:
  TEAMS_WEBHOOK_URL: "https://your-webhook-url"
  SERVICENOW_INSTANCE: "your-instance.service-now.com"
  SERVICENOW_USER: "api_user"
  SERVICENOW_PASS: "api_password"
```

### 3. Deploy
```bash
kubectl apply -f namespace-quota-monitor.yaml
```

### 4. Test Manually
```bash
kubectl create job quota-test --from=cronjob/namespace-quota-monitor -n gt-operators
kubectl logs -n gt-operators job/quota-test
```

## Alert Levels

| Threshold | Action | Alert Type |
|-----------|--------|------------|
| **≥95%** | ServiceNow P1 + Teams | 🔴 CRITICAL (RED) |
| **≥90%** | Teams only | 🟠 WARNING (ORANGE) |
| **<90%** | No alert | ✅ OK |

## Monitored Resources

### Compute
- `requests.cpu`, `requests.memory`
- `limits.cpu`, `limits.memory`

### Objects
- `count/pods`, `count/services`, `count/configmaps`
- `count/secrets`, `count/persistentvolumeclaims`
- `count/deployments.apps`, `count/statefulsets.apps`

### Storage
- `requests.storage`

## ServiceNow Integration
- **P1 tickets** at ≥95% quota usage
- **24h deduplication** - updates existing tickets
- Includes namespace, resource type, usage details, top consumers

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| CLUSTER_NAME | (required) | Cluster identifier |
| CRITICAL_THRESHOLD | 95 | % for ServiceNow tickets |
| WARNING_THRESHOLD | 90 | % for Teams alerts |
| ENABLE_SERVICENOW | true | Enable ServiceNow integration |
| ENABLE_TEAMS_ALERTS | true | Enable Teams notifications |

## Sample Output

### Critical Alert
```
=== Checking ResourceQuota: compute-quota in namespace: production ===
  requests.cpu: 7200m / 8000m (90%)
  🔴 CRITICAL: requests.cpu at 90%
  📤 Sending Teams notification...
  ✅ Teams notification sent successfully
  🎫 Creating ServiceNow ticket...
  ✅ ServiceNow ticket: INC0123456

Top CPU Consumers:
  - api-server-abc123: 1200m
  - worker-def456: 800m
  - scheduler-ghi789: 600m
```

## Teams Alert Format

```
🔴 CRITICAL: Namespace Quota at 90%

Namespace: production
Quota: compute-quota
Resource: requests.cpu
Used: 7200m / 8000m (90%)

Top Consumers:
  - api-server-abc123: 1200m
  - worker-def456: 800m
  - scheduler-ghi789: 600m

⚠️ Action Required: Increase quota or reduce usage!

Cluster: tkg-test-01
Time: 2025-11-08 22:30:00 UTC
```

## Creating ResourceQuotas

### Compute Quota
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: production
spec:
  hard:
    requests.cpu: "8"
    requests.memory: 16Gi
    limits.cpu: "12"
    limits.memory: 20Gi
```

### Object Count Quota
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: object-quota
  namespace: production
spec:
  hard:
    count/pods: "100"
    count/services: "50"
    count/configmaps: "100"
    persistentvolumeclaims: "20"
```

## Taking Action on Alerts

### Option 1: Increase Quota
```bash
kubectl edit resourcequota compute-quota -n production
```

### Option 2: Reduce Usage
```bash
# Scale down non-critical apps
kubectl scale deployment non-critical-app -n production --replicas=1

# Delete unused resources
kubectl delete pod old-job-xyz -n production
```

### Option 3: Optimize Requests
```yaml
# Before (over-requested)
resources:
  requests:
    cpu: 2000m
    memory: 4Gi

# After (right-sized)
resources:
  requests:
    cpu: 500m
    memory: 1Gi
```

## Troubleshooting

**No ResourceQuotas found:**
```bash
# Check if quotas exist
kubectl get resourcequota -A

# Create test quota
kubectl create quota test --hard=cpu=2,memory=2Gi,pods=10 -n default
```

**No alerts:**
```bash
# Check quota usage
kubectl describe resourcequota -n <namespace>

# View logs
kubectl logs -n gt-operators -l app=namespace-quota-monitor --tail=50
```

**No ServiceNow ticket:**
- Verify `ENABLE_SERVICENOW: "true"` in ConfigMap
- Check SERVICENOW_INSTANCE is not placeholder
- Validate credentials in Secret

**Unable to get pod metrics:**
- Install metrics-server: `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`
