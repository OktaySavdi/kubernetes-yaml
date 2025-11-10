# PVC Storage Monitor

## Overview
Monitors PersistentVolumeClaim (PVC) disk usage across all namespaces and sends Teams alerts when storage reaches critical levels.

## Features
- ✅ Monitors all PVCs via `df` command in pods
- ✅ Multi-level alerts: 95% (Critical), 90% (Warning), 80% (Info)
- ✅ Teams notifications with top consumers
- ✅ Automatic pod detection per PVC
- ✅ Runs hourly (configurable)

## Alert Levels

| Usage | Alert Level | Action |
|-------|-------------|--------|
| ≥ 95% | 🔴 CRITICAL | Immediate action - Expand PVC or cleanup now |
| ≥ 90% | 🟠 WARNING | Action recommended - Plan expansion soon |
| ≥ 80% | ℹ️ INFO | Logged only - No alert sent |
| < 80% | ✅ OK | Healthy - No action needed |

## Quick Start

### 1. Configure Webhook
```bash
kubectl edit secret pvc-teams-webhook -n gt-operators
# Update webhook-url with your Teams incoming webhook URL
```

### 2. Verify Deployment
```bash
kubectl get cronjob pvc-storage-monitor -n gt-operators
kubectl get sa pvc-storage-monitor-sa -n gt-operators
```

### 3. Test Manually
```bash
kubectl create job --from=cronjob/pvc-storage-monitor pvc-test -n gt-operators
kubectl logs -n gt-operators -l app=pvc-storage-monitor --tail=200
```

## How It Works

1. **PVC Discovery**: Scans all namespaces for PVCs
2. **Pod Detection**: Finds pods using each PVC
3. **Disk Check**: Executes `df -h` inside pod at mount path
4. **Alert Decision**: Compares usage % against thresholds and sends Teams alert

## How It Works

1. **PVC Discovery**: Scans all namespaces for PVCs
2. **Pod Detection**: Finds pods using each PVC
3. **Disk Check**: Executes `df -h` inside pod at mount path
4. **Alert Decision**: Compares usage % against thresholds and sends Teams alert

## Sample Output

```
==========================================
PVC Storage Monitor Starting
Time: 2025-11-08 09:00:00
Cluster: tkg-test-01
==========================================

Checking PVC: postgres-data in namespace: database (Capacity: 100Gi)
  Pod: postgres-0, Mount: /var/lib/postgresql/data
  Used: 92G / Available: 6.1G / Usage: 94%
  🟠 WARNING ALERT SENT (94% used)

Checking PVC: elasticsearch-data in namespace: logging (Capacity: 200Gi)
  Pod: elasticsearch-0, Mount: /usr/share/elasticsearch/data
  Used: 195G / Available: 2.8G / Usage: 98%
  🔴 CRITICAL ALERT SENT (98% used)

=== Top Storage Consumers ===
  elasticsearch-data (logging): 98%
  postgres-data (database): 94%
  redis-data (cache): 75%
```

## Teams Alert Format

```
🔴 CRITICAL: PVC Storage at 98%

Cluster: tkg-test-01
Time: 2025-11-08 09:00:00 UTC

🚨 CRITICAL: PVC Almost Full

PVC: elasticsearch-data
Namespace: logging
Capacity: 200Gi
Used: 195G / Available: 2.8G
Usage: 98%
Pod: elasticsearch-0

⚠️ Action Required: Expand PVC or cleanup data immediately!
```

## Configuration

### Change Schedule
Default: Every hour
```bash
# Every 30 minutes
kubectl patch cronjob pvc-storage-monitor -n gt-operators \
  -p '{"spec":{"schedule":"*/30 * * * *"}}'

# Every 2 hours
kubectl patch cronjob pvc-storage-monitor -n gt-operators \
  -p '{"spec":{"schedule":"0 */2 * * *"}}'
```

### Customize Thresholds
```bash
kubectl edit configmap pvc-storage-monitor-script -n gt-operators
```
```bash
CRITICAL_THRESHOLD=95  # Change to 98 for higher tolerance
WARNING_THRESHOLD=90   # Change to 85 for earlier warnings
INFO_THRESHOLD=80      # Change to 70 for more info logs
```

### Set Cluster Name
```bash
kubectl edit cronjob pvc-storage-monitor -n gt-operators
```
```yaml
env:
  - name: CLUSTER_NAME
    value: "your-cluster-name"
```

## Taking Action on Alerts

### Critical Alert (≥95%)

**Option 1: Expand PVC** (requires StorageClass with allowVolumeExpansion: true)
```bash
kubectl edit pvc <pvc-name> -n <namespace>
# Update spec.resources.requests.storage to larger size
spec:
  resources:
    requests:
      storage: 200Gi  # Increase from 100Gi
```

**Option 2: Cleanup Data**
```bash
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh
# Inside pod
du -sh /path/to/mount/* | sort -hr | head -20
rm -rf /path/to/old/data
```

**Option 3: Add New PVC**
- Create additional PVC for new data
- Reconfigure application to use multiple volumes

### Warning Alert (90-94%)

1. **Plan expansion** during maintenance window
2. **Review retention** policies (logs/backups)
3. **Archive old data** to object storage
4. **Monitor closely** - increase check frequency

## Troubleshooting

**No PVCs found:**
```bash
kubectl get pvc -A
# If no PVCs exist, monitor reports: "No PVC usage data collected"
```

**Cannot execute df in pod:**
- Issue: Minimal container images lack `df` command
- Monitor skips with warning: "⚠️ Could not get disk usage from pod"
- Workaround: Use alpine/busybox-based images

**Permission denied:**
```bash
kubectl auth can-i create pods/exec --as=system:serviceaccount:gt-operators:pvc-storage-monitor-sa -A
kubectl get clusterrole pvc-storage-monitor-role -o yaml
```

**No Teams notifications:**
```bash
# Verify webhook
kubectl get secret pvc-teams-webhook -n gt-operators -o jsonpath='{.data.webhook-url}' | base64 -d

# Test webhook
curl -H "Content-Type: application/json" \
  -d '{"text":"Test from PVC monitor"}' \
  YOUR_WEBHOOK_URL
```
