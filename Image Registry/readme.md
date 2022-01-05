
When a pod is coming up it fetches a container image by using the `spec.containers.image` field in pod definition. If there isn’t any specific reference in this field image is fetched from `dockerhub`. In this lab we will install an internal image registry in Kubernetes to store either homegrown or 3rd party images. A new namespace `kube-infra` will be created to store this kimd of supported services.

[Docker Registry 2.0](https://hub.docker.com/_/registry) which is maintained by Docker Community will be used. Image registry will be secure and there will be a user definition for authentication.

## Generate Certificates

By default container runtime applications do not accept insecure registries. It is possible to allow insecure connections but we prefer to generate certificates and deploy a secure registry. The certificate authority used here is not the one used to generate kubernetes certificates. Although there is no harm in using the same CA, new authority has been generated for hosted applications. Since this is a self-signed CA, container engine will not trust to it. CA can either be added at system level to worker nodes and can given directly to container engine (in this case containerd). In this lab CA is added at Ubuntu worker nodes.

```bash
# Private key
$ openssl genrsa -out ./image-registry.key 2048
# CSR
$ openssl req -new -key ./image-registry.key -subj "/CN=image-registry/O=infra-services" -out ./image-registry.csr -config ./openssl-8-mega-registry.cnf
# Sign the CSR
$ openssl x509 -req -in ./image-registry.csr -CA ./ca.crt -CAkey ./ca.key -CAcreateserial  -out ./image-registry.crt -extensions v3_req -extfile ./openssl-8-mega-registry.cnf -days 3650

```

All possible addresses are required to be included in the certificate. Kubernetes services can be invoked by different formats. There are also different ingress host names. `openssl-8-mega-registry.cnf` file contains this information as `alt_names.`

```bash
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
[req_distinguished_name]
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = image-registry
DNS.2 = image-registry.kube-infra
DNS.3 = image-registry.kube-infra.svc
DNS.4 = image-registry.kube-infra.svc.cluster.local
DNS.4 = image-registry.8-mega.local
DNS.5 = image-registry.8-mega.io

```

Generate kubernetes secret

```bash
$ kubectl -n kube-infra create secret tls image-registry-certs --cert=./image-registry.crt --key=./image-registry.key

```

## User Authentication

A htpasswd file will be generated to hold username and password within image registry pods. File content will be stored in kubernetes secret. httpd:2 docker image can be used to execute htpasswd command.

```bash
$ sudo docker run --entrypoint htpasswd httpd:2 -Bbn registry Passw0rd > image-registry-auth.htpasswd

```

While `kubectl create secret` command can be used to generate the secret. Following `yaml` file is given to `kubectl apply -f` command.

```yaml
apiVersion: v1
kind: Secret
type: Opaque
metadata:
  name: image-registry-user
  namespace: kube-infra
  labels:
    category: infrastructure
    application: image-registry
    content: user-info
data:
  auth: "<base64 encoded content of htpasswd file>"

```

## Environment Configuration

A Kubernetes `ConfigMap` will be create to store environment variables required by `registry:2` image.

![Ekran Resmi 2022-01-05 18 55 18](https://user-images.githubusercontent.com/3519706/148247937-8d4c946e-da7a-4d86-ba05-65753e96f948.png)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-registry-plain
  namespace: kube-infra
  labels:
    category: infrastructure
    application: image-registry-plain
    resiliency: single
spec:
  replicas: 1
  selector:
    matchLabels:
      category: infrastructure
      application: image-registry-plain
      resiliency: single
  template:
    metadata:
      labels:
        category: infrastructure
        application: image-registry-plain
        resiliency: single
    spec:
      containers:
        - name: image-registry-plain
          image: registry:2
          imagePullPolicy: IfNotPresent
          ports:
            - name: registry
              containerPort: 5000
          env:
           - name: REGISTRY_HTTP_ADDR
             valueFrom:
                configMapKeyRef:
                   name: image-registry-plain
                   key: httpAddr
           - name: REGISTRY_AUTH
             valueFrom:
                configMapKeyRef:
                   name: image-registry-plain
                   key: authType
           - name: REGISTRY_AUTH_HTPASSWD_REALM
             valueFrom:
                configMapKeyRef:
                   name: image-registry-plain
                   key: authHtpasswdRealm
           - name: REGISTRY_AUTH_HTPASSWD_PATH
             valueFrom:
                configMapKeyRef:
                   name: image-registry-plain
                   key: authHtpasswdPath
          volumeMounts:
            - name: image-registry-storage
              mountPath: /var/lib/registry
            - name: image-registry-user
              mountPath: /auth
      volumes:
        - name: image-registry-storage
          emptyDir: {}
        - name: image-registry-user
          secret:
            secretName: image-registry-user

```
The output is

```bash
$ kubectl -n kube-infra get pods
NAME                                    READY   STATUS    RESTARTS   AGE
image-registry-plain-5f866d8d99-m8h44   1/1     Running   1          15h

```

## Expose image-registry

Now that we have the image registry pod up and running we need to expose it for internal and external requests to be able to connect. There are several ways to do this. It is possible to define a `NodePort` service and use it for both internal and external use cases. Instead a `ClusterIP` Service and an `Ingress` will be defined. ClusterIP will expose the application withing the kubernetes cluster, and ingress will allow external requests to reach to our image-registry.

### ClusterIP Service

Follwiong yaml will be used to define the service.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: image-registry-plain
  namespace: kube-infra
  labels:
    category: infrastructure
    application: image-registry-plain
    resiliency: single
spec:
  type: ClusterIP
  ports:
    - name: registry
      port: 5000
      targetPort: 5000
  selector:
    category: infrastructure
    application: image-registry-plain

```

The output is:

```bash
$ kubectl -n kube-infra get svc -o wide
NAME             TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)    AGE   SELECTOR
image-registry-plain ClusterIP 10.32.0.191 <none> 5000/TCP 15h   application=image-registry-plain,category=infrastructure

$ kubectl -n kube-infra get ep -o wide
NAME             ENDPOINTS       AGE
image-registry-plain   10.2.2.30:5000  15h

```
Since service and endpoints are in place. Any pod within this cluster can connect to image-registry.

### Registry ingress

Note that pods are managed by `kubelet` and kubelet is running on worker nodes not in any other pod. As a result it will not be possible to deploy pods by using internal image registry untill defining an ingress for kubelet and containerd running on worker nodes to able to reach.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: image-registry
  namespace: kube-infra
  labels:
     category: infrastructure
     application: image-registry
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: "true"
spec:
  rules:
    - host: image-registry.8-mega.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name:  image-registry-plain
                port:
                  number: 5000
  tls:
          - secretName: image-registry-certs

```
The yaml file given above creates a new secure ingress.

### Verify Image Registry

To test the newly deployed registry a new image (busybox) will be pulled from DockerHub, tagged and then pushed into.

```bash
$ sudo docker login <https://image-registry.8-mega.local> -u registry
Password: 
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
<https://docs.docker.com/engine/reference/commandline/login/#credentials-store>

Login Succeeded

$ sudo docker pull busybox:latest
latest: Pulling from library/busybox
3cb635b06aa2: Pull complete 
Digest: sha256:b5cfd4befc119a590ca1a81d6bb0fa1fb19f1fbebd0397f25fae164abe1e8a6a
Status: Downloaded newer image for busybox:latest
docker.io/library/busybox:latest

$ sudo docker images| grep busybox
busybox                                          latest           ffe9d497c324   3 weeks ago    1.24MB

$ sudo docker tag busybox:latest image-registry.8-mega.local/utils/busybox:latest  

$ sudo docker images| grep busybox                                               
image-registry.8-mega.local/utils/busybox        latest           ffe9d497c324   3 weeks ago    1.24MB
busybox                                          latest           ffe9d497c324   3 weeks ago    1.24MB

$ sudo docker push image-registry.8-mega.local/utils/busybox:latest              
The push refers to repository [image-registry.8-mega.local/utils/busybox]
64cac9eaf0da: Pushed 
latest: digest: sha256:50e44504ea4f19f141118a8a8868e6c5bb9856efa33f2183f5ccea7ac62aacc9 size: 527

```

The output is:

```bash
$ curl <https://registry:Passw0rd@image-registry.8-mega.local/v2/_catalog>   
{"repositories":["utils/busybox"]}

$ curl <https://registry:Passw0rd@image-registry.8-mega.local/v2/utils/busybox/tags/list>
{"name":"utils/busybox","tags":["latest"]}

```

Refarance: [URL](https://8-mega.notion.site/Install-Image-Registry-dddb1226cc464fad836546500f24ad1d)
