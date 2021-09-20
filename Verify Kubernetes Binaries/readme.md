**Locate and Download the Checksums for the Binary Files**

 1. Verify the binaries on the server:
```bash
cd k8s-binaries/
ls -la
```
 2. Check the Kubernetes version that you will use to locate the
    checksums:

**Note:** Don't try to check the version by running any of the binaries before you have verified them (e.g., with a command like ```kubectl version```)! All of the binaries are the same version.
```bash
cat version.txt
```
 3. Create an environment variable to store the version number:
```bash
VERSION=$(cat version.txt)
echo $VERSION
```
 4. Using the ```$VERSION``` variable, download the checksum files:
```bash
curl -LO "https://dl.k8s.io/$VERSION/bin/linux/amd64/kubectl.sha256"

curl -LO "https://dl.k8s.io/$VERSION/bin/linux/amd64/kubelet.sha256"

curl -LO "https://dl.k8s.io/$VERSION/bin/linux/amd64/kube-apiserver.sha256"
```
**Verify the Binaries and Delete Any That May Contain Malicious Code**

 1. Verify the kubectl binary using the checksum:
```bash
echo "$(<kubectl.sha256) kubectl" | sha256sum --check
```
You should receive an output of ```OK```.

 2. Verify the kubelet binary using the checksum:
```bash
echo "$(<kubelet.sha256) kubelet" | sha256sum --check
```
You should receive an output of ```FAILED```.

 3. Verify the kube-apiserver binary using the checksum:
```bash
echo "$(<kube-apiserver.sha256) kube-apiserver" | sha256sum --check
```
You should receive an output of ```OK```.

 4. Optional: Run the kubelet binary that failed checksum validation:

**Note:** This file does NOT contain malicious code. This example is intended to demonstrate the potential dangers of running unverified or potentially malicious binaries. In a real-world scenario, you would NEVER run a binary file that fails checksum validation.
```
./kubelet
```
 5. Delete the kubelet binary that failed validation:
```
rm kubelet
```
