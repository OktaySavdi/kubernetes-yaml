
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
