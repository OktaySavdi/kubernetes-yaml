
### Enforce the AppArmor Profile

1.  Display the contents of the AppArmor profile config file:
    
    ```
    cat apparmor-k8s-deny-write
    ```

    ```yaml
    #include <tunables/global>
    profile k8s-deny-write flags=(attach_disconnected) {
      #include <abstractions/base>
      file,
      # Deny all file writes.
      deny /** w,
    }
    ```
    
2.  Enable the AppArmor profile, using the password provided on the lab page:
    
    ```bash
    sudo apparmor_parser apparmor-k8s-deny-write
    
    sudo cp apparmor-k8s-deny-write /etc/apparmor.d
    
    sudo chown root:root /etc/apparmor.d/apparmor-k8s-deny-write
    ```
    
3.  Open a new terminal session and log in to the worker node server using the provided lab credentials:
    
    ```bash
    ssh cloud_user@<PUBLIC_IP_ADDRESS>
    ```
    
4.  Enable the AppArmor profile on the working node, using the password provided on the lab page:
    
    ```bash
    sudo apparmor_parser apparmor-k8s-deny-write
    
    sudo cp apparmor-k8s-deny-write /etc/apparmor.d
    
    sudo chown root:root /etc/apparmor.d/apparmor-k8s-deny-write
    ```
    

### Configure the password-db Pod to Run Its Container Using the AppArmor Profile

1.  Return to the control plane session and list the Pods on the  `auth`  namespace:
    
    ```
    kubectl get pods -n auth
    ```
    
2.  View the logs on the  `password-db`  Pod, and note the sensitive password data being written:
    
    ```
    kubectl logs password-db -n auth
    ```
    
3.  Display the contents of our  `password.txt`  file, and note the password being exposed:
    
    ```
    kubectl exec password-db -n auth -- cat password.txt
    ```
    
4.  Edit the existing Pod manifest:
    
    ```bash
    vi password-db-pod.yml
    ```
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: password-db
  namespace: auth
spec:
  containers:
  - name: password-db
    image: radial/busyboxplus:curl
    command: ['sh', '-c', 'while true; do if echo "The password is hunter2" > password.txt; then echo "Password hunter2 logged."; else echo "Password log attempt blocked."; fi; sleep 5; done']
```
    
5.  Under  `metadata:`, add an  `annotations:`  field to apply AppArmor:
    
    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      annotations:
        container.apparmor.security.beta.kubernetes.io/password-db: localhost/k8s-deny-write
    
      ...
    ```
    
6.  To save and exit the file, press  **Escape**  and enter  `:wq`.
    
7.  Delete the  `password-db`  Pod:
    
    ```
    kubectl delete pod password-db -n auth
    ```
    
8.  Re-create the  `password-db`  Pod with the updated manifest:
    
    ```
    kubectl create -f password-db-pod.yml
    ```
    
9.  Verify the Pod is running:
    
    ```
    kubectl get pods -n auth
    ```
    
10.  Check the Pod's logs:
    
```
kubectl logs password-db -n auth
```
    
You should receive a log output:  `can't create password.txt: Permission denied`.
    
11.  Display the contents of the  `password.txt`  file:
    
```
kubectl exec password-db -n auth -- cat password.txt
```
    
You should receive an output:  `can't open 'password.txt': No such file or directory`.
