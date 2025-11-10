# Node Resource Monitor

## Overview
Monitors node CPU/Memory usage and pressure conditions with ServiceNow/Teams alerts.

## Features
- ✅ Real-time monitoring every 5 minutes
- ✅ ServiceNow P1 tickets at ≥95% usage
- ✅ Teams alerts at ≥90% usage
- ✅ Pressure condition detection (Memory, Disk, PID)
- ✅ Top 3 resource consumers included
- ✅ ConfigMap-based configuration

## Quick Start

### 1. Update Configuration
Edit ConfigMap in `node-resource-monitor.yaml`:
```yaml
data:
  CLUSTER_NAME: "your-cluster-name"
  CPU_CRITICAL_THRESHOLD: "95"
  CPU_WARNING_THRESHOLD: "90"
  MEMORY_CRITICAL_THRESHOLD: "95"
  MEMORY_WARNING_THRESHOLD: "90"
  ENABLE_SERVICENOW: "true"
  ENABLE_TEAMS_ALERTS: "true"
```

### 2. Update Credentials
Edit Secret in `node-resource-monitor.yaml`:
```yaml
stringData:
  TEAMS_WEBHOOK_URL: "https://your-webhook-url"
  SERVICENOW_INSTANCE: "your-instance.service-now.com"
  SERVICENOW_USER: "api_user"
  SERVICENOW_PASS: "api_password"
```

### 3. Deploy
```bash
kubectl apply -f node-resource-monitor.yaml
```

### 4. Test Manually
```bash
kubectl create job node-test --from=cronjob/node-resource-monitor -n gt-operators
kubectl logs -n gt-operators job/node-test
```

## Alert Levels

| Threshold | Action | Alert Type |
|-----------|--------|------------|
| **≥95%** | ServiceNow P1 + Teams | 🔴 CRITICAL (RED) |
| **≥90%** | Teams only | 🟠 WARNING (ORANGE) |
| **<90%** | No alert | ✅ OK |

### Node Pressure Conditions
- ⚠️ **MemoryPressure**: Node low on memory
- ⚠️ **DiskPressure**: Node low on disk space
- ⚠️ **PIDPressure**: Too many processes

## ServiceNow Integration
- **P1 tickets** at ≥95% CPU or Memory
- **24h deduplication** - updates existing tickets
- Includes node details and top resource consumers

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| CLUSTER_NAME | (required) | Cluster identifier |
| CPU_CRITICAL_THRESHOLD | 95 | CPU % for ServiceNow tickets |
| CPU_WARNING_THRESHOLD | 90 | CPU % for Teams alerts |
| MEMORY_CRITICAL_THRESHOLD | 95 | Memory % for ServiceNow tickets |
| MEMORY_WARNING_THRESHOLD | 90 | Memory % for Teams alerts |
| ENABLE_SERVICENOW | true | Enable ServiceNow integration |
| ENABLE_TEAMS_ALERTS | true | Enable Teams notifications |

## Sample Output

### Critical Alert
```
=== Checking Node: worker-3 ===
  Status: True
  ⚠️  Node under pressure: MemoryPressure
  Capacity: 4 CPU, 16384Mi Memory
  Current Usage: 3600m CPU (90%), 14745Mi Memory (90%)
  🔴 CRITICAL: CPU usage at 90%
   CRITICAL: Memory usage at 90%
  📤 Sending Teams notification...
  ✅ Teams notification sent successfully
  🎫 Creating ServiceNow ticket...
  ✅ ServiceNow ticket: INC0123456

Top CPU Consumers:
  - monitoring/prometheus-0: 1200m
  - logging/elasticsearch-0: 800m
  - kube-system/coredns-abc123: 400m

Top Memory Consumers:
  - logging/elasticsearch-0: 4096Mi
  - monitoring/prometheus-0: 3072Mi
  - default/app-backend-xyz: 2048Mi
```

## Teams Alert Format

```
🔴 CRITICAL: Node CPU at 92%

Node: worker-3
CPU Usage: 3680m / 4 (92%)
Status: True

Top CPU Consumers:
  - monitoring/prometheus-0: 1200m
  - logging/elasticsearch-0: 800m
  - kube-system/coredns-abc123: 400m

⚠️ Action Required: Investigate high CPU usage!

Cluster: tkg-test-01
Time: 2025-11-08 22:05:30 UTC
```

## Taking Action on Alerts

### Critical CPU (≥95%)
1. **Immediate**: Identify top consumers (shown in alert), scale down non-critical workloads
2. **Short-term**: Add nodes, optimize app CPU, implement HPA
3. **Long-term**: Right-size capacity, cluster autoscaling

### Critical Memory (≥95%)
1. **Immediate**: Check for memory leaks, restart problematic pods
2. **Short-term**: Add nodes with more memory, optimize apps
3. **Long-term**: Implement memory limits, use VPA

### Node Pressure
- **MemoryPressure**: Evict low-priority pods, increase memory
- **DiskPressure**: Clean images (`docker system prune`), increase disk
- **PIDPressure**: Check for fork bombs, increase PID limits

## Troubleshooting

**No metrics available:**
```bash
# Install metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify it's working
kubectl top nodes
```

**No alerts:**
```bash
# Check node usage
kubectl top nodes

# View logs
kubectl logs -n gt-operators -l app=node-resource-monitor --tail=50
```

**No ServiceNow ticket:**
- Verify `ENABLE_SERVICENOW: "true"` in ConfigMap
- Check SERVICENOW_INSTANCE is not placeholder
- Validate credentials in Secret

**Permission errors:**
```bash
# Verify RBAC
kubectl get clusterrole node-resource-monitor-role
kubectl get clusterrolebinding node-resource-monitor-rolebinding
```
