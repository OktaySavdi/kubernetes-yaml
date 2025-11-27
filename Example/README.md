```yaml
---
# Deployment with Production Best Practices
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: gt-operators
  labels:
    app: web
    version: v1
spec:
  replicas: 2  # HA: 2 replicas for availability
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Only 1 additional pod during update
      maxUnavailable: 1  # Maximum 1 pod unavailable during update
  selector:
    matchLabels:
      app: web
      version: v1
  template:
    metadata:
      labels:
        app: web
        version: v1
    spec:           
      # Anti-affinity for spreading pods across nodes (soft rule - won't block scheduling)
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100  # Prefer spreading, but will schedule on same node if needed
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - web
              topologyKey: kubernetes.io/hostname
        # Node affinity (adjust based on your cluster)
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 1
            preference:
              matchExpressions:
              - key: node-role.kubernetes.io/worker
                operator: Exists
      # Security Context at Pod level
      securityContext:
        runAsUser: 1001
        runAsGroup: 0
        fsGroup: 1001
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      volumes:
      - name: tmp
        emptyDir: {}
      containers:
      - name: istioproject
        image: quay.io/oktaysavdi/istioproject:latest
        imagePullPolicy: Always
        # Security Context at Container level
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        # Resource limits and requests
        resources:
          requests:
            memory: "128Mi"
            cpu: "10m"
          limits:
            memory: "256Mi"
            cpu: "50m"
        # Ports
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP        
        # Liveness probe - restart if unhealthy
        livenessProbe:
          httpGet:
            path: /istio
            port: http
            scheme: HTTP
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
        # Readiness probe - remove from service if not ready
        readinessProbe:
          httpGet:
            path: /istio
            port: http
            scheme: HTTP
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3        
        # Lifecycle hooks
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
             #command: ["/bin/sh", "-c", "curl -X POST http://localhost:8080/shutdown && sleep 5"]
      # Restart policy
      restartPolicy: Always
      # Termination grace period
      terminationGracePeriodSeconds: 30
---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
  namespace: gt-operators
  labels:
    app: web
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2  # Minimum 2 replicas
  maxReplicas: 10 # Maximum 10 replicas
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 minutes before scaling down
      policies:
      - type: Percent
        value: 50          # Scale down by max 50% of current pods
        periodSeconds: 60  # ... per minute
      - type: Pods
        value: 2           # OR scale down by max 2 pods
        periodSeconds: 60  # ... per minute
      selectPolicy: Min    # Use the SMALLER of the two policies (more conservative)
    scaleUp:
      stabilizationWindowSeconds: 0    # No waiting, scale up immediately
      policies:
      - type: Percent
        value: 100         # Scale up by max 100% (double pods)
        periodSeconds: 30  # ... every 30 seconds
      - type: Pods
        value: 4           # OR scale up by max 4 pods
        periodSeconds: 30  # ... every 30 seconds
      selectPolicy: Max    # Use the LARGER of the two policies (more aggressive)
---
# Pod Disruption Budget for HA
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
  namespace: gt-operators
  labels:
    app: web
spec:
  maxUnavailable: 1  # Allow 1 pod to be unavailable during disruptions (won't block upgrades/drains)
  selector:
    matchLabels:
      app: web

---
# Resource Quota for namespace
# Based on 2 nodes with 8 CPU and 32GB RAM total
# Reserves ~15% for system (1 CPU, 4GB RAM)
# Allows 70-80% cluster utilization to prevent overcommit
apiVersion: v1
kind: ResourceQuota
metadata:
  name: gt-operators-quota
  namespace: gt-operators
spec:
  hard:
    # CPU: Allow up to 5.5 CPU (70% of available 7 CPU)
    requests.cpu: "5500m"     # Guaranteed CPU
    limits.cpu: "7"           # Max burst CPU
    
    # Memory: Allow up to 20GB (70% of available 28GB)
    requests.memory: "20Gi"   # Guaranteed RAM
    limits.memory: "28Gi"     # Max burst RAM
---
apiVersion: v1
kind: LimitRange
metadata:
  name: gt-operators-limits
  namespace: gt-operators
spec:
  limits:
  - type: Container
    max:
      cpu: "2"        # No container can request more than 2 CPU
      memory: "2Gi"   # No container can request more than 2GB RAM
    min:
      cpu: "10m"      # Every container must request at least 10m CPU
      memory: "32Mi"  # Every container must request at least 32Mi RAM
    default:
      cpu: "200m"     # Auto-assigned if no limits.cpu specified
      memory: "512Mi" # Auto-assigned if no limits.memory specified
    defaultRequest:
      cpu: "100m"     # Auto-assigned if no requests.cpu specified
      memory: "256Mi" # Auto-assigned if no requests.memory specified
```
