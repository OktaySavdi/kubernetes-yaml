```yaml
apiVersion: v1
kind: Pod
metadata:
  name: auth-rest
  namespace: dev
spec:
  containers:
  - image: nginx:1.19.1
    imagePullPolicy: IfNotPresent
    name: nginx
    resources: {}
    securityContext:
      allowPrivilegeEscalation: false #set to false
      readOnlyRootFilesystem: true #change to false
      runAsUser: 0 #delete
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/cache/nginx
      name: cache
    - mountPath: /var/run
      name: run
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-hkv4m
      readOnly: true
  dnsPolicy: ClusterFirst
  enableServiceLinks: true
  nodeName: k8s-worker1
  preemptionPolicy: PreemptLowerPriority
  priority: 0
  restartPolicy: Always
  schedulerName: default-scheduler
  securityContext: {}
  serviceAccount: default
  serviceAccountName: default
  terminationGracePeriodSeconds: 30
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  volumes:
  - emptyDir: {}
    name: cache
  - emptyDir: {}
    name: run
  - name: kube-api-access-hkv4m
    projected:
      defaultMode: 420
      sources:
      - serviceAccountToken:
          expirationSeconds: 3607
          path: token
      - configMap:
          items:
          - key: ca.crt
            path: ca.crt
          name: kube-root-ca.crt
      - downwardAPI:
          items:
          - fieldRef:
              apiVersion: v1
              fieldPath: metadata.namespace
            path: namespace
```
