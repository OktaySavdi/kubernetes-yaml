# Pod Cleanup CronJob

## Overview
Automated cleanup of unwanted pods (Succeeded, Failed, Evicted, Terminating) with Teams notifications.

## Features
- ✅ Runs nightly at 3 AM (configurable)
- ✅ Cleans Succeeded, Failed, Evicted, Terminating pods
- ✅ Teams notifications with breakdown
- ✅ ConfigMap-based configuration
- ✅ Optional success notifications

## Quick Start

### 1. Update Configuration
Edit ConfigMap in `pod-cleanup-cronjob.yaml`:
```yaml
data:
  CLUSTER_NAME: "your-cluster-name"
  ENABLE_TEAMS_ALERTS: "true"
  ENABLE_SUCCESS_NOTIFICATIONS: "false"
```

### 2. Update Webhook
Edit Secret in `pod-cleanup-cronjob.yaml`:
```yaml
stringData:
  TEAMS_WEBHOOK_URL: "https://your-webhook-url"
```

### 3. Deploy
```bash
kubectl apply -f pod-cleanup-cronjob.yaml
```

### 4. Test Manually
```bash
kubectl create job pod-cleanup-test --from=cronjob/pod-cleanup -n gt-operators
kubectl logs -n gt-operators job/pod-cleanup-test
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| CLUSTER_NAME | (required) | Cluster identifier |
| ENABLE_TEAMS_ALERTS | true | Enable Teams notifications |
| ENABLE_SUCCESS_NOTIFICATIONS | false | Notify when no cleanup needed |

## What Gets Cleaned

| State | Reason | Example |
|-------|--------|---------|
| **Succeeded** | Completed jobs | `etcd-backup-xxx` after completion |
| **Failed** | Failed jobs/containers | Failed backup jobs, crashed init containers |
| **Evicted** | Resource pressure | Pods evicted due to OOM/disk limits |
| **Terminating** | Stuck pods | Pods that won't delete cleanly (force deleted) |

## Teams Notification

```
🧹 Pod Cleanup Completed
Cluster: your-cluster-name
Total Deleted: 5 pods

Breakdown:
- Succeeded: 2
- Failed: 1
- Evicted: 1
- Terminating: 1
```

## Sample Output

```
======================================
Starting Pod Cleanup
Time: 2025-11-08 03:00:15
======================================

Checking for Succeeded pods...
  Deleting pod: etcd-backup-28345678 in gt-operators
    ✅ Successfully deleted

Checking for Failed pods...
  Deleting pod: backup-failed-xyz in backup
    ✅ Successfully deleted

Checking for Evicted pods...
  Deleting pod: nginx-evicted-abc in web
    ✅ Successfully deleted

Checking for Terminating pods...
  Force deleting pod: stuck-pod-def in kube-system
    ✅ Successfully deleted

======================================
Cleanup Summary
Total Deleted: 5 pods
  Succeeded: 2
  Failed: 1
  Evicted: 1
  Terminating: 1
======================================
```

## Troubleshooting

**No pods cleaned:**
```bash
# Check for pods to cleanup
kubectl get pods -A --field-selector=status.phase=Succeeded
kubectl get pods -A --field-selector=status.phase=Failed
kubectl get pods -A | grep Evicted
kubectl get pods -A | grep Terminating
```

**No Teams notification:**
- Check `ENABLE_TEAMS_ALERTS: "true"` in ConfigMap
- Verify TEAMS_WEBHOOK_URL in Secret
- Set `ENABLE_SUCCESS_NOTIFICATIONS: "true"` for notifications even when no cleanup

**Permission errors:**
```bash
# Verify RBAC
kubectl get clusterrole pod-cleanup-role
kubectl get clusterrolebinding pod-cleanup-rolebinding
```

**CronJob not running:**
```bash
# Check if suspended
kubectl get cronjob pod-cleanup -n gt-operators -o yaml | grep suspend

# Un-suspend
kubectl patch cronjob pod-cleanup -n gt-operators -p '{"spec":{"suspend":false}}'
```
