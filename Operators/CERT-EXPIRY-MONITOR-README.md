# Certificate Expiry Monitor Operator

## Overview
Production-ready certificate monitoring for **managed Kubernetes clusters** (Tanzu, AKS, EKS, GKE). Focuses on application certificates you actually control, with Teams notifications before expiry.

## What It Monitors (Actionable Alerts)
- ✅ **Application TLS Secrets** - All `kubernetes.io/tls` secrets across namespaces
- ✅ **Custom CA Certificates** - Custom CAs in ConfigMaps
- ✅ **cert-manager Certificates** - Auto-detected if installed
- ✅ **Service Mesh Certificates** - Istio/Linkerd certificates
- ✅ **Ingress TLS Certificates** - nginx-ingress, traefik, contour
- ✅ Alerts at **60, 45, 30, 14, 7 days** before expiry
- ✅ Immediate alerts for **expired** certificates
- ✅ Identifies **self-signed** vs **CA-signed** certificates
- ✅ Teams notifications with color-coded severity
- ✅ Runs daily at 4:00 AM automatically

## What It Skips (Platform-Managed)
- ℹ️ **Kubernetes CA** - Auto-renewed by platform (informational only)
- ℹ️ **API Server** - Managed by Tanzu/AKS/EKS/GKE
- ℹ️ **etcd** - Externally managed
- ℹ️ **Kubelet** - Auto-renewed by platform

## Alert Levels

| Days Until Expiry | Alert Level | Color | Description |
|-------------------|-------------|-------|-------------|
| Expired | 🚨 EXPIRED | Red | Certificate already expired |
| ≤ 7 days | 🔴 CRITICAL | Red | Immediate action required |
| ≤ 14 days | 🟠 WARNING | Orange | Action needed soon |
| ≤ 30 days | 🟡 NOTICE | Yellow | Plan renewal |
| ≤ 45 days | 🟢 INFO | Green | Advance notice |
| ≤ 60 days | ℹ️ INFO | Blue | Early warning |

## Quick Start

### 1. Configure Teams Webhook

**First, update the Teams webhook URL:**

```bash
# Edit the secret and replace with your actual Teams webhook URL
kubectl edit secret cert-teams-webhook -n gt-operators
```

Or create it directly:
```bash
kubectl create secret generic cert-teams-webhook \
  -n gt-operators \
  --from-literal=webhook-url='https://your-actual-teams-webhook-url' \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 2. Deploy the Monitor

```bash
kubectl apply -f cert-expiry-monitor.yaml
```

### 3. Verify Deployment

```bash
# Check CronJob
kubectl get cronjob cert-expiry-monitor -n gt-operators

# Check ServiceAccount and RBAC
kubectl get sa cert-expiry-monitor-sa -n gt-operators
kubectl get clusterrole cert-expiry-monitor-role
```

### 4. Test Immediately

```bash
# Don't wait for 9 AM - run it now
kubectl create job --from=cronjob/cert-expiry-monitor cert-test -n gt-operators

# Watch the job
kubectl get job cert-test -n gt-operators --watch

# Check logs
kubectl logs -n gt-operators -l app=cert-expiry-monitor --tail=100
```

## What Gets Monitored

### 1. Application TLS Secrets
All secrets of type `kubernetes.io/tls` across all namespaces - **your application certificates**.

**Example:**
```yaml
apiVersion: v1
kind: Secret
type: kubernetes.io/tls
metadata:
  name: my-app-tls
  namespace: production
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
```

### 2. Custom CA Certificates
CA certificates stored in ConfigMaps (e.g., `ca.crt`, `ca-bundle.crt`, `root-ca.crt`).

### 3. cert-manager Certificates
Auto-detected if cert-manager is installed. Monitors certificates managed by cert-manager.

### 4. Service Mesh Certificates
- Istio certificates (if Istio is installed)
- Linkerd certificates (if Linkerd is installed)

### 5. Ingress Controller Certificates
Scans TLS secrets in common ingress namespaces:
- `ingress-nginx`
- `nginx-ingress`
- `traefik`
- `contour`

### 6. Kubernetes Platform Certificates (Informational Only)
- Kubernetes CA certificate - displayed but **not alerted** (auto-managed by platform)

## Sample Output

### Console Output
```
==========================================
Certificate Expiry Monitor Starting
Time: 2025-11-08 04:00:00
==========================================

=== Scanning Application TLS Certificates ===
Checking TLS secret: antrea-controller-tls in namespace: kube-system

=== Scanning Custom CA Certificates ===
Checking custom CA from ConfigMap: kube-root-ca.crt in namespace: default
Checking custom CA from ConfigMap: antrea-ca in namespace: kube-system

=== Scanning cert-manager Certificates ===
  ℹ️  cert-manager not installed, skipping cert-manager certificates

=== Scanning Service Mesh Certificates ===
  ℹ️  Istio not detected, skipping service mesh certificates

=== Scanning Ingress Controller Certificates ===
(No ingress controllers found)

=== Informational: Kubernetes Platform Certificates ===
ℹ️  Platform certificates (API server, etcd, kubelet) are auto-renewed by Tanzu/managed platform
  Kubernetes CA expires: Sep 27 11:04:24 2035 GMT (auto-managed, no action needed)

==========================================
Certificate Scan Complete
==========================================

Certificate: antrea-controller-tls (Namespace: kube-system, Type: Application TLS Secret)
  Expires: Sep 29 10:08:22 2026 GMT (324 days)
  Issuer: CN = antrea-ca@1759144102
  Self-Signed: No
  Alert Level: 

Certificate: kube-root-ca.crt-ca (Namespace: default, Type: Custom CA (ConfigMap))
  Expires: Sep 27 11:04:24 2035 GMT (3609 days)
  Issuer: CN = kubernetes
  Self-Signed: Yes (Self-Signed)
  Alert Level: 
```

### Teams Notification Example
```
🟠 WARNING Certificate Expiring Soon!

Certificate: app-tls
Namespace: staging
Type: TLS Secret
Expires in: 14 days
Expiry Date: Nov 20 09:00:00 2025 GMT
Self-Signed: Yes (Self-Signed)

2025-11-08 09:00:00 UTC
```

## Configuration

### Change Schedule
Default: Every day at **4:00 AM**

```bash
# Run every 12 hours
kubectl patch cronjob cert-expiry-monitor -n gt-operators \
  -p '{"spec":{"schedule":"0 */12 * * *"}}'

# Run weekly on Mondays at 8 AM
kubectl patch cronjob cert-expiry-monitor -n gt-operators \
  -p '{"spec":{"schedule":"0 8 * * 1"}}'
```

### Customize Alert Thresholds

Edit the ConfigMap to change alert days:

```bash
kubectl edit configmap cert-expiry-script -n gt-operators
```

Find this line and modify:
```bash
THRESHOLDS=(60 45 30 14 7)  # Change to your preferred days
```

Example custom thresholds:
```bash
THRESHOLDS=(90 60 30 7)     # 90, 60, 30, 7 days
THRESHOLDS=(30 14 7 3 1)    # More frequent alerts
```

### Disable Teams Notifications (Testing)

To run without sending Teams alerts:
```bash
kubectl patch secret cert-teams-webhook -n gt-operators \
  -p '{"stringData":{"webhook-url":"https://your-teams-webhook-url-here"}}'
```

The script will detect this and skip sending notifications while still logging everything.

## Monitoring

### View CronJob Status
```bash
kubectl get cronjob cert-expiry-monitor -n gt-operators
```

### View Recent Jobs
```bash
kubectl get jobs -n gt-operators -l app=cert-expiry-monitor
```

### Check Last Run Logs
```bash
kubectl logs -n gt-operators -l app=cert-expiry-monitor --tail=200
```

### View Real-time Logs
```bash
kubectl logs -n gt-operators -l app=cert-expiry-monitor -f
```

## Troubleshooting

### No Certificates Found
```bash
# Verify you have TLS secrets
kubectl get secrets -A --field-selector type=kubernetes.io/tls

# Check RBAC permissions
kubectl auth can-i list secrets --as=system:serviceaccount:gt-operators:cert-expiry-monitor-sa -A
```

### Teams Notifications Not Sending
```bash
# Verify webhook URL is configured
kubectl get secret cert-teams-webhook -n gt-operators -o jsonpath='{.data.webhook-url}' | base64 -d

# Test webhook manually
curl -H "Content-Type: application/json" \
  -d '{"text":"Test from cert monitor"}' \
  YOUR_WEBHOOK_URL
```

### Permission Errors
```bash
# Check ServiceAccount
kubectl get sa cert-expiry-monitor-sa -n gt-operators

# Check ClusterRole
kubectl get clusterrole cert-expiry-monitor-role -o yaml

# Check ClusterRoleBinding
kubectl get clusterrolebinding cert-expiry-monitor-rolebinding -o yaml
```

### Job Keeps Failing
```bash
# Check pod status
kubectl get pods -n gt-operators -l app=cert-expiry-monitor

# Check pod events
kubectl describe pod -n gt-operators -l app=cert-expiry-monitor

# View full logs
kubectl logs -n gt-operators -l app=cert-expiry-monitor --previous
```

## Security

- ✅ **Non-root**: Runs as user 1001
- ✅ **Read-only**: Only list/get permissions, cannot modify secrets
- ✅ **Minimal RBAC**: Only reads secrets, configmaps, namespaces, and cert-manager CRDs
- ✅ **No privilege escalation**: `allowPrivilegeEscalation: false`
- ✅ **Dropped capabilities**: All Linux capabilities dropped
- ✅ **Resource limits**: CPU and memory limited
- ✅ **Secret protection**: Teams webhook stored in Kubernetes secret

## FAQ

**Q: Why don't I see API server/etcd/kubelet certificates?**  
A: These are auto-managed by your platform (Tanzu/AKS/EKS/GKE). The monitor shows them as "informational only" and doesn't alert on them.

**Q: Will this work with cert-manager?**  
A: Yes! It auto-detects cert-manager and monitors all cert-manager issued certificates.

**Q: What if I don't have ingress yet?**  
A: The monitor will skip ingress scanning. When you deploy ingress later, it will automatically start monitoring ingress TLS certificates.

**Q: Can I monitor certificates in specific namespaces only?**  
A: Currently scans all namespaces. You can modify the script to filter by namespace if needed.

**Q: Does it send alerts for every certificate every day?**  
A: No - alerts are only sent at specific thresholds (60, 45, 30, 14, 7 days before expiry).

## Important Notes

### Managed vs Self-Hosted Clusters
- **Tanzu/AKS/EKS/GKE**: Platform certificates (API server, etcd, kubelet) are auto-renewed - this monitor focuses on **your application certificates**
- **Self-hosted clusters**: Same focus on application certificates, platform certificates shown as informational only

### What This Monitor Does
- ✅ **Alerts** on certificates you manage and control
- ✅ **Reports** platform certificates for visibility (no alerts)
- ✅ **Tracks** all TLS secrets across all namespaces
- ❌ **Does NOT renew** certificates - use cert-manager for auto-renewal

## Integration with cert-manager

If using cert-manager, certificates are auto-renewed. This monitor will:
- ✅ Track cert-manager managed certificates
- ✅ Alert if cert-manager fails to renew
- ✅ Verify new certificates are issued correctly

**Best Practice**: Use cert-manager for auto-renewal + this monitor for alerting on any issues.

## Uninstall

```bash
kubectl delete -f cert-expiry-monitor.yaml
```

This removes:
- CronJob: `cert-expiry-monitor`
- ServiceAccount: `cert-expiry-monitor-sa`
- ClusterRole: `cert-expiry-monitor-role`
- ClusterRoleBinding: `cert-expiry-monitor-rolebinding`
- ConfigMap: `cert-expiry-script`
- Secret: `cert-teams-webhook`
