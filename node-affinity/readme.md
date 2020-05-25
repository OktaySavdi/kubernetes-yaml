# kubernetes node affinity

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test
  labels:
    mylabels: mysamplelable
spec:
  containers:
    - name: myPodName
      image: nginx
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: size
                operator: In
                values:
                  - Large

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: red
spec:
  replicas: 3
  selector:
    matchLabels:
      color: red
  template:
    metadata:
      name: red-pod
      labels:
        color: red
    spec:
      containers:
        - name: nginx
          image: nginx
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: node-role.kubernetes.io/master
                    operator: Exists

---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
 name: blue
spec:
 replicas: 6
 selector:
   matchLabels:
     run: nginx
 template:
   metadata:
     labels:
       run: nginx
   spec:
     containers:
       - image: nginx
         imagePullPolicy: Always
         name: nginx
     affinity:
       nodeAffinity:
         requiredDuringSchedulingIgnoredDuringExecution:
           nodeSelectorTerms:
             - matchExpressions:
                 - key: color
                   operator: In
                   values:
                     - blue
```