# ETCD Backup CronJob

## Overview
Automated etcd backup from all control plane nodes with Teams/ServiceNow notifications on failures.

## Features
- ✅ Nightly backups at 2 AM (configurable)
- ✅ Backs up all control plane nodes simultaneously (3 pods)
- ✅ Keeps 10 most recent backups per node
- ✅ Teams notifications on failures only
- ✅ ServiceNow P1 ticket creation for critical failures
- ✅ ConfigMap-based configuration
- ✅ Auto-detects cluster name from kubectl context
- ✅ Node hostname in backup filenames

## Quick Start

### 1. Update Configuration
Edit ConfigMap in `etcd-backup-cronjob.yaml`:
```yaml
data:
  CLUSTER_NAME: "your-cluster-name"
  BACKUP_DIR: "/opt/backup"
  MAX_BACKUPS: "10"
  ENABLE_SERVICENOW: "true"
  ENABLE_TEAMS_ALERTS: "true"
  ENABLE_SUCCESS_NOTIFICATIONS: "false"
```

### 2. Update Credentials
Edit Secret in `etcd-backup-cronjob.yaml`:
```yaml
stringData:
  TEAMS_WEBHOOK_URL: "https://your-webhook-url"
  SERVICENOW_INSTANCE: "your-instance.service-now.com"
  SERVICENOW_USER: "api_user"
  SERVICENOW_PASS: "api_password"
```

### 3. Deploy
```bash
kubectl apply -f etcd-backup-cronjob.yaml
```

### 4. Test Manually
```bash
kubectl create job etcd-backup-test --from=cronjob/etcd-backup -n etcd-backup
kubectl logs -n etcd-backup job/etcd-backup-test -f
```

## ServiceNow Integration
- Creates **P1 tickets** for backup failures
- **24h ticket deduplication** - updates existing tickets
- Includes backup details, error messages, node information

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| CLUSTER_NAME | (required) | Cluster identifier |
| BACKUP_DIR | /opt/backup | Backup storage location |
| MAX_BACKUPS | 10 | Number of backups to retain per node |
| ENABLE_SERVICENOW | true | Enable ServiceNow tickets |
| ENABLE_TEAMS_ALERTS | true | Enable Teams notifications |
| ENABLE_SUCCESS_NOTIFICATIONS | false | Notify on successful backups |

## Multi-Node Backup

### How It Works
- **3 pods created simultaneously** (one per control plane node)
- Each pod backs up its own etcd instance independently
- Backups stored on respective node's `/opt/backup`
- Node hostname included in filename for identification

### Backup Filename Format
```
etcd-backup-<cluster-name>-<node-hostname>-<timestamp>.tar.gz

Examples:
etcd-backup-tkg-test-01-cxfs5-ltx94-20251108-190025.tar.gz
etcd-backup-tkg-test-01-cxfs5-qk4ht-20251108-190025.tar.gz
etcd-backup-tkg-test-01-cxfs5-zjh4b-20251108-190025.tar.gz
```

### Verify Backups
```bash
# List control plane nodes
kubectl get nodes -l node-role.kubernetes.io/control-plane

# Check backups on a node
kubectl debug node/<control-plane-node> -it --image=alpine
chroot /host
ls -lh /opt/backup/

# Count backups per node (using node hostname suffix)
ls -1 /opt/backup/etcd-backup-*-ltx94-*.tar.gz | wc -l
```

## Restore Process

### Standard Kubernetes
```bash
# 1. Stop API servers and etcd on all control plane nodes

# 2. Copy backup to restore location
cp /opt/backup/etcd-backup-YYYYMMDD-HHMMSS.tar.gz /tmp/
cd /tmp
tar -xzf etcd-backup-YYYYMMDD-HHMMSS.tar.gz

# 3. Restore snapshot
mv /var/lib/etcd /var/lib/etcd.backup
ETCDCTL_API=3 etcdctl snapshot restore etcd-snapshot.db \
  --data-dir=/var/lib/etcd \
  --name=<node-name> \
  --initial-cluster=<cluster-definition> \
  --initial-advertise-peer-urls=https://<node-ip>:2380

# 4. Start etcd and API server
```

## Schedule Customization

```bash
# Daily at 2 AM (default)
kubectl patch cronjob etcd-backup -n etcd-backup -p '{"spec":{"schedule":"0 2 * * *"}}'

# Every 6 hours
kubectl patch cronjob etcd-backup -n etcd-backup -p '{"spec":{"schedule":"0 */6 * * *"}}'

# Weekly on Sunday at 3 AM
kubectl patch cronjob etcd-backup -n etcd-backup -p '{"spec":{"schedule":"0 3 * * 0"}}'
```

## Troubleshooting

**Backup fails:**
```bash
# Check pod logs
kubectl logs -n etcd-backup -l app=etcd-backup --tail=100

# Verify etcd certificates
kubectl exec -n etcd-backup <pod> -- ls -la /etc/kubernetes/pki/etcd/
```

**No ServiceNow ticket:**
- Verify `ENABLE_SERVICENOW: "true"` in ConfigMap
- Check SERVICENOW_INSTANCE is not placeholder
- Validate credentials in Secret

**No Teams notification:**
- Verify `ENABLE_TEAMS_ALERTS: "true"` in ConfigMap
- Check TEAMS_WEBHOOK_URL is set correctly
- Test webhook: `curl -X POST -H 'Content-Type: application/json' -d '{"text":"Test"}' "YOUR-WEBHOOK-URL"`

**Node selector mismatch:**
```bash
# Check control plane labels
kubectl get nodes --show-labels | grep control-plane

# Should have: node-role.kubernetes.io/control-plane=
```

**Permission denied on /opt/backup:**
```bash
# Debug into control plane node
kubectl debug node/<control-plane-node> -it --image=alpine
chroot /host
mkdir -p /opt/backup
chmod 755 /opt/backup
```

## Monitoring

```bash
# View recent jobs
kubectl get jobs -n etcd-backup

# Check CronJob status
kubectl get cronjob -n etcd-backup

# View logs from all pods in latest job
kubectl logs -n etcd-backup -l app=etcd-backup -f

# Check failed jobs
kubectl get jobs -n etcd-backup --field-selector status.successful!=1
```

## Security Notes
- Pod runs privileged (required for etcd access)
- Backups contain **sensitive cluster data** - secure `/opt/backup`
- Consider encrypting backups at rest
- Store webhook URLs in Secrets
- Implement off-cluster backup replication for DR

## Cleanup

```bash
# Delete all components
kubectl delete namespace etcd-backup
kubectl delete clusterrole etcd-backup-role
kubectl delete clusterrolebinding etcd-backup-rolebinding

# Clean backup files from nodes
kubectl debug node/<control-plane-node> -it --image=alpine
chroot /host
rm -rf /opt/backup/etcd-backup-*
```
