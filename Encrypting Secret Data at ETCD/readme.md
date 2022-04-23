
##  Encrypting Secret Data at Rest

1.  Generate a 32 byte random key and base64 encode it.  
```
head -c 32 /dev/urandom | base64
```    
Your output will look something similar to the following example. Keep note of the output, as we will be using it in a config file.
```
WxaW1k22mu3M/WYMIWYVOkAOrOTJ17+Q5+McAIqK3bM=
```
3.  Create a new file called 
```
/etc/kubernetes/pki/encrypt-etcd-secrets.yml
```
5.  Add the following to its contents.  
```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: WxaW1k22mu3M/WYMIWYVOkAOrOTJ17+Q5+McAIqK3bM=
    - identity: {}
```
Replace the secret value for key1 with the base64 encoded key we created earlier.

### Add Encryption Provider Config to Kubernetes’ API Controller

1.  Open the configuration file for the Kubernetes API server.  
```
vi /etc/kubernetes/manifests/kube-apiserver.yaml
```    
2.  Find the following section
```yaml 
spec:
   containers:
   - command:
     - kube-apiserver
     - --authorization-mode=Node,RBAC
     [...]
```
And add add the following line somewhere under  `- kube-apiserver`.
```   
- --encryption-provider-config=/etc/kubernetes/pki/encrypt-etcd-secrets.yml
```   
3.  Changes saved to the manifest will automatically be loaded by the API controller. There is no need restart an services.

4.	 Create a new secret called `secret1` in the `default` namespace: 
```shell
kubectl create secret generic secret1 -n default --from-literal=mykey=mydata
```   
5. Using the etcdctl commandline, read that secret out of etcd:
```   
ETCDCTL_API=3 etcdctl --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/apiserver-etcd-client.crt --key=/etc/kubernetes/pki/apiserver-etcd-client.key get /registry/secrets/default/secret1 
```   

![image](https://user-images.githubusercontent.com/3519706/120084998-5cabcb00-c0dd-11eb-8303-2cce8740436e.png)
