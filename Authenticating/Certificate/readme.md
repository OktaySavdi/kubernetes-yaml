# Give Access To Your Cluster With A Client Certificate
````
ca.key: openssl genrsa -out ca.key 2048
ca.csr: openssl req -new -key ca.key -subj "/CN=KUBERNETES-CA" -out ca.csr
ca.crt: openssl x509 -req -in ca.csr -signkey ca.key -out ca.crt
    
admin.key: openssl genrsa -out admin.key 2048
admin.csr: openssl req -new -key admin.key -subj "/CN=kube-admin" -out admin.csr
admin.crt: openssl x509 -req -in admin.csr -CA ca.crt -CAkey ca.key -out admin.crt
or
openssl genrsa -out oktay.key 2048
openssl req -new -key oktay.key -out oktay.csr
openssl x509 -req -in oktay.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out oktay.crt -days 500
or
# Root CA
openssl genrsa -out ca.key 2048 > /dev/null 2>&1
openssl req -x509 -new -nodes -key ca.key -days 3650 -out ca.crt -subj "/CN=mycluster" > /dev/null 2>&1

# Typha server
openssl genrsa -out typha-server.key 2048 > /dev/null 2>&1
openssl req -new -key typha-server.key -out typha-server.csr -subj "/CN=typha-server" > /dev/null 2>&1
openssl x509 -req -in typha-server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out typha-server.crt -days 3650 -extensions ssl_client > /dev/null 2>&1

# Typha client
openssl genrsa -out typha-client.key 2048 > /dev/null 2>&1
openssl req -new -key typha-client.key -out typha-client.csr -subj "/CN=typha-client" -config ${CONFIG} > /dev/null 2>&1
openssl x509 -req -in typha-client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out typha-client.crt -days 3650 -extensions ssl_client > /dev/null 2>&1

openssl x509 -in /etc/kubernetes/pki/ca.crt -text -noout
````
Exmple
````
openssl genrsa -out oktay.key 2048
openssl req -new -key oktay.key -subj "/CN=oktay" -out oktay.csr
````
````
openssl x509 -in ./oktay.crt -noout -text
````
````
curl https://kube-api-server:6443/api/v1/pods --key admin.key --cert admin.crt --cacert ca.crt
````
------------------

**1- Create a Normal User with X.509 Client Certificate**
````
openssl req -newkey rsa:2048 -nodes -keyout oktay.key -out oktay.csr -subj "/CN=oktay"
````
````
openssl x509 -req -in oktay.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out oktay.crt -days 1000
````
**2-Create a CertificateSigningRequest and submit it to a Kubernetes Cluster via kubectl. Below is a script to generate the CertificateSigningRequest.**
````
cat oktay.csr | base64 -w 0
cat oktay.csr | base64 | tr -d "\n"
````
````yaml
cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: oktay
spec:
  groups:
  - system:authenticated
  request: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURSBSRVFVRVNULS0tLS0KTUlJQ1ZUQ0NBVDBDQVFBd0VERU9NQXdHQTFVRUF3d0ZiMnQwWVhrd2dnRWlNQTBHQ1NxR1NJYjNEUUVCQVFVQQpBNElCRHdBd2dnRUtBb0lCQVFDOTVyL0pzdFhDWC9hamhJY1ZSb2tJdEpJMXhTNExjL2t4Z1IvQnFKWTdQOTNuCitqL0tEV2ZqdCt5bEo2bXBzWDVHcmdJU1JyWlBJUGlFazQzUUN0Y29RV3FBTG5JeDZ6NlZUZGJUeVV2VkQ4WjgKZjc4SXVlQzFpTUdoNWR0UStsSXAzQUhUbVBuQVBXUUd0Y01qdW8rK1Q0WDlZekRRd2c5dGxrN2RMa3M2TGVYVApNVVZ4ZXh0azRzeDRVTDM2dTlsdHBDajV1WStmSXk5d1JrdFEwQjlPUkFHSW91Qm9obGhrdVlYSGx3aFltQ1VyCkpnKzZKTGxKYTk4L1paTEc3OXllTlRTSkJnY3hnWklReHVZbTJVa1lkK0lXdmU5b0JLTVN0clhJVlAzN2lZVWEKcXBpNmgveklwQWUrZlFncktoOWhkVnAreThrbmtZNWNhbjZhNGFDZkFnTUJBQUdnQURBTkJna3Foa2lHOXcwQgpBUXNGQUFPQ0FRRUFxMGxxZzllYVowd3RXTnhWQW93K09zcng2a1BjMzdCZi9Ua3BSZzNRaDhuc3dyUzhsK0gxCit0bUQxZ2NHS3FIRFJ2SXJhdXltYldmQWovTkR2R0xaWFJtai9OaG1FYnlDTEZwOFJ1OE9VRU4zUC9IVFVnRGMKL3VhTkRnbG92VEU0MXBGZjAwSVM5UFYwS21VVXhmaFZtNkxlTDFtd0JuejBQa3NpQUpDOHFzd2hqRzBlemw5RwphQlZwM0ptcmJENmhIYWtpdVgya2R3U05Ga3licjZ1SGc5MTNzNDY0TnNOUXpCSDFpa0hOZ2M5T1lhQURBNlgrClpmNm54SkZzVXF0NW5PR2NPeGI3VVBVUG5jR2pDck04WjFDcFBQVzNSa1hkMjNUL3RiYVdNaGVydlNxajZ3SzcKa1JXWEZud1FjbkdaS1pKSGY4SEFTR0M2UitvOHR6MDJrZz09Ci0tLS0tRU5EIENFUlRJRklDQVRFIFJFUVVFU1QtLS0tLQo=  #signerName: kubernetes.io/kube-apiserver-client
  signerName: kubernetes.io/kube-apiserver-client
  usages:
  - digital signature
  - key encipherment
  - server auth
  - client auth
EOF
````
**3-Get the list of CSRs:**
````
kubectl get csr
````
Approve the CSR:
````
kubectl certificate approve oktay 
````
Retrieve the certificate from the CSR:
````
kubectl get csr oktay -o yaml
````

**4-This is a sample script to create a Role for this new user:**
````yaml
cat <<EOF | kubectl apply -f -
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
 namespace: development
 name: oktayrole
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["create", "get", "update", "list", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["create", "get", "update", "list", "delete"]
EOF
````
**5-This is a sample command to create a RoleBinding for this new user:**
````yaml
cat <<EOF | kubectl apply -f -
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
 name: oktayrolebinding
 namespace: development
subjects:
- kind: User
  name: oktay
  apiGroup: rbac.authorization.k8s.io
roleRef:
 kind: Role
 name: oktayrole
 apiGroup: rbac.authorization.k8s.io
EOF
````
**6-Check Permissions**
````
kubectl auth can-i list pods -n development
kubectl auth can-i list pods -n development --as oktay
kubectl auth can-i list nodes --as oktay
kubectl auth can-i list deployments --as system:serviceaccount:ns1:pipeline -n ns1
kubectl auth can-i update deployments --as system:serviceaccount:ns1:pipeline -n ns1
````
**7-Then, you need to add the context:**
````
kubectl config set-context oktay --cluster=kubernetes --user=oktay
````
**8-To test it, change the context to oktay:**
````
kubectl config use-context oktay
````
**9-We have to set the credentials in the kubeconfig file to get the Kube cluster access for that run a below command**
````
kubectl config set-credentials oktay --client-certificate=oktay.crt --client-key=oktay.key --embed-certs
````
**10-List Kubermetes users** 
````
kubectl config get-context
````
