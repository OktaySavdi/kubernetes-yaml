# Kubernetes Operators Suite

## Overview
Automated monitoring and management for Kubernetes clusters with Teams notifications and ServiceNow integration.

## Operators Summary

| Operator | Purpose | Schedule | Alerts |
|----------|---------|----------|--------|
| **Cluster Intelligence** | AI-powered anomaly detection (CPU/Memory spikes, pod restarts) | Every 15 min | ServiceNow P1/P2/P3 + Teams |
| **Cost Optimization** | Resource right-sizing recommendations and savings calculations | Daily 8 AM | Teams (Info) |
| **ETCD Backup** | Automated etcd snapshots to NFS (3 control plane nodes) | Daily 2 AM | ServiceNow P1 on failure |
| **Namespace Quota** | ResourceQuota monitoring (CPU/Memory/Storage/Objects) | Every 30 min | 95% Critical, 90% Warning |
| **Node Resource** | Node CPU/Memory/Pressure monitoring with top consumers | Every 5 min | 95% Critical, 90% Warning |
| **Pod Cleanup** | Auto-cleanup Succeeded/Failed/Evicted/Terminating pods | Daily 3 AM | Teams (Summary) |
| **PVC Storage** | PVC disk usage monitoring via `df` command | Hourly | 95% Critical, 90% Warning |
| **Certificate Expiry** | TLS certificate expiration tracking | Daily 4 AM | 60/45/30/14/7 days + Expired |

## Quick Start

```bash
# 1. Create namespace
kubectl create -f namespace.yaml

# 2. Configure Teams webhooks
kubectl create secret generic teams-webhook -n gt-operators \
  --from-literal=webhook-url='https://your-teams-webhook-url'

kubectl create secret generic cert-teams-webhook -n gt-operators \
  --from-literal=webhook-url='https://your-teams-webhook-url'

kubectl create secret generic pvc-teams-webhook -n gt-operators \
  --from-literal=webhook-url='https://your-teams-webhook-url'

# 3. Deploy operators
kubectl apply -f cluster-intelligence-cronjob.yaml
kubectl apply -f cost-optimization-cronjob.yaml
kubectl apply -f etcd-backup-cronjob.yaml
kubectl apply -f namespace-quota-monitor.yaml
kubectl apply -f node-resource-monitor.yaml
kubectl apply -f pod-cleanup-cronjob.yaml
kubectl apply -f pvc-storage-monitor.yaml
kubectl apply -f cert-expiry-monitor.yaml

# 4. Verify
kubectl get cronjob,deployment -n gt-operators
```

## Common Operations

```bash
# View all operators
kubectl get cronjob -n gt-operators

# Check logs
kubectl logs -n gt-operators -l app=<operator-name> --tail=100

# Manual trigger
kubectl create job --from=cronjob/<cronjob-name> test-job -n gt-operators

# Change schedule
kubectl patch cronjob <cronjob-name> -n gt-operators \
  -p '{"spec":{"schedule":"*/10 * * * *"}}'
```

## Configuration

**Set cluster name** in each operator:
```yaml
env:
  - name: CLUSTER_NAME
    value: "your-cluster-name"
```

**ServiceNow integration** (optional):
```yaml
ENABLE_SERVICENOW: "true"
SERVICENOW_INSTANCE: "your-instance.service-now.com"
SERVICENOW_USERNAME: "your-username"
SERVICENOW_PASSWORD: "your-password"
```

## Documentation

Detailed documentation for each operator:

- [Cluster Intelligence](CLUSTER-INTELLIGENCE-README.md) - AI anomaly detection with baseline comparison
- [Cost Optimization](COST-OPTIMIZATION-README.md) - Over-provisioned resource identification
- [ETCD Backup](ETCD-BACKUP-README.md) - Multi-node backup with restore procedures
- [Namespace Quota Monitor](NAMESPACE-QUOTA-MONITOR-README.md) - ResourceQuota tracking
- [Node Resource Monitor](NODE-RESOURCE-MONITOR-README.md) - Node health and pressure monitoring
- [Pod Cleanup](POD-CLEANUP-README.md) - Automated pod cleanup
- [PVC Storage Monitor](PVC-STORAGE-MONITOR-README.md) - PVC disk usage monitoring
- [Certificate Expiry Monitor](CERT-EXPIRY-MONITOR-README.md) - TLS certificate tracking
