**Download Elasticserach and Kibana [URL](https://www.elastic.co/guide/en/elasticsearch/reference/7.16/rpm.html#rpm-key)**

**Install Elasticsearch Cluster : [URL](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-production-elasticsearch-cluster-on-centos-7)**

**LogForwarding Configure on Kubernetes: [URL](https://computingforgeeks.com/ship-kubernetes-logs-to-external-elasticsearch/)**


## Step 1: Download Sample Filebeat and Metricbeat files


Log into your Kubernetes master node and run the command below to fetch Filebeat and Metricbeat yaml files provided by Elastic.

```
cd ~
curl -L -O https://raw.githubusercontent.com/elastic/beats/7.16/deploy/kubernetes/filebeat-kubernetes.yaml
curl -L -O https://raw.githubusercontent.com/elastic/beats/7.16/deploy/kubernetes/metricbeat-kubernetes.yaml
```

## Step 2: Edit the files to befit your environment
In both files, we only need to change a few things. Under the ConfigMap, you will find elasticseach output as shown below. Change the ip (192.168.10.123) and port (9200) to that of your Elasticsearch server.

```
    output.elasticsearch:
      hosts: ['${ELASTICSEARCH_HOST:192.168.10.123}:${ELASTICSEARCH_PORT:9200}']
      #username: ${ELASTICSEARCH_USERNAME}
      #password: ${ELASTICSEARCH_PASSWORD}
```

Under DaemonSet within the same file, you will find the following configuration. Note that we are showing the areas to change. Edit the IP (192.168.10.123) and port (9200) to match that of your Elastcsearch server as well. If you have configured username and password for your Elasticsearch, you are free to add them on the commented sections shown.

```
        env:
        - name: ELASTICSEARCH_HOST
          value: "192.168.10.123"
        - name: ELASTICSEARCH_PORT
          value: "9200"
        #- name: ELASTICSEARCH_USERNAME
        #  value: elastic
        #- name: ELASTICSEARCH_PASSWORD
        #  value: changeme
        - name: ELASTIC_CLOUD_ID
```

It should be noted that if you would wish to deploy your Filebeat and Metricbeat resources on another namespace, simply edit all instances of “_**kube-system**_” to the one of your choice.

Under Deployment, you can change the version of Filebeat and Metricbeat to be deployed by editing the image (_docker.elastic.co/beats/metricbeat:7.16.0_) seen on the snippet below. I am going to use version 7.16.0.

```
###For Metricbeat####
    spec:
      serviceAccountName: metricbeat
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
      containers:
      - name: metricbeat
        image: docker.elastic.co/beats/metricbeat:7.16.0
```

Do the same for the filebeat yml file if you would wish to change its version as well.

```
###For Filebeat####
    spec:
      serviceAccountName: metricbeat
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
      containers:
      - name: metricbeat
        image: docker.elastic.co/beats/filebeat:7.16.0
```

### Important thing to note

If you would wish to deploy the beats on the master node, we will have to add tolerations. An example for metricbeat is shown below. That is not the whole DaemonSet config. Just the part we are interested in. You can leave the other parts intact. Add the toleration as shown on the configuration below under spec. The same can apply on filebeat configuration depending on your needs.

```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: metricbeat
  namespace: kube-system
  labels:
    k8s-app: metricbeat
spec:
  selector:
    matchLabels:
      k8s-app: metricbeat
  template:
    metadata:
      labels:
        k8s-app: metricbeat
    spec:
###PART TO EDIT###
      # This toleration is to have the daemonset runnable on master nodes
      # Remove it if your masters can't run pods
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
####END OF EDIT###
      serviceAccountName: metricbeat
      terminationGracePeriodSeconds: 30
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
      containers:
      - name: metricbeat
        image: docker.elastic.co/beats/metricbeat:7.9.0
        args: [
          "-c", "/etc/metricbeat.yml",
          "-e",
```

## Step 4: Deploying to Kubernetes

After we have done all of our edits and our Elasticsearch is well reachable from your Kubernetes cluster, It is time to deploy our beats. Login to your master node and run the commands below:

```
kubectl apply -f metricbeat-kubernetes.yaml
kubectl apply -f filebeat-kubernetes.yaml
```
onfirm that the pods are deployed and running successfully after some time.

```
$ kubectl get pods -n kube-system

NAME                                             READY   STATUS    RESTARTS   AGE
calico-kube-controllers-c9784d67d-k85hf          1/1     Running   0          11d
calico-node-brjnk                                1/1     Running   0          10d
calico-node-nx869                                1/1     Running   0          10d
calico-node-whlzf                                1/1     Running   0          11d
coredns-f9fd979d6-6vztd                          1/1     Running   0          11d
coredns-f9fd979d6-8gz4l                          1/1     Running   0          11d
etcd-kmaster.diab.mfs.co.ke                      1/1     Running   0          11d
filebeat-hlzhc                                   1/1     Running   0          7d23h <==
filebeat-mcs67                                   1/1     Running   0          7d23h <==
kube-apiserver-kmaster.diab.mfs.co.ke            1/1     Running   0          11d
kube-controller-manager-kmaster.diab.mfs.co.ke   1/1     Running   0          11d
kube-proxy-nlrbv                                 1/1     Running   0          11d
kube-proxy-zdcbg                                 1/1     Running   0          10d
kube-proxy-zvf6c                                 1/1     Running   0          10d
kube-scheduler-kmaster.diab.mfs.co.ke            1/1     Running   0          11d
metricbeat-5fw98                                 1/1     Running   0          8d  <==
metricbeat-5zw9b                                 1/1     Running   0          8d  <==
metricbeat-jbppx                                 1/1     Running   0          8d  <==
```

## Step 5: Create Index on Kibana

Once our Pods begin running, they will immediately send an index pattern to Elasticsearch together with the logs. Login to your Kibana and Click “**_Stack Management_**”  **>**  “**_Index Management_**” and you should be able to see your indexes.

![image](https://user-images.githubusercontent.com/3519706/146194868-02c3adbf-d9a4-4e57-a3cc-3df42ae697c1.png)

Click on “_**Index Management**_“

![image](https://user-images.githubusercontent.com/3519706/146194963-a5880bfb-151b-49c8-b93f-2e3acf1d197c.png)

And there are our indexes.

![image](https://user-images.githubusercontent.com/3519706/146195058-47d19c1e-4259-4bc1-8c34-ab3eacdc4030.png)

To create an index pattern, click on “**_Index Pattern_**s” then hit “**_Create Index Pattern_**“.

![image](https://user-images.githubusercontent.com/3519706/146195079-9538352c-d7ca-4540-967f-022eae1560d4.png)

On the next page, type in the name of the index pattern that matches either filebeat or metricbeat and they should show up as already matched.

![image](https://user-images.githubusercontent.com/3519706/146195095-af0242f1-04cc-49bc-9181-592180b3140f.png)

Create the pattern then click “**_Next Step_**“

![image](https://user-images.githubusercontent.com/3519706/146195116-11bcb7cf-14df-455b-a47d-d989561e39ed.png)

Choose “_@timestamp_” on the drop-down then “**_Create Index Pattern_**“

![image](https://user-images.githubusercontent.com/3519706/146195137-6da96b8c-9a29-4cb9-9c55-54bbf433f7fd.png)

## Step 6: Discover your Data

After the index pattern has been created, click on “**_Discover”_**,

![image](https://user-images.githubusercontent.com/3519706/146195167-62e58425-d170-457a-b21e-f39fac1e44cf.png)

Then choose the index pattern we created.

![image](https://user-images.githubusercontent.com/3519706/146195191-d4148991-c372-4485-89c2-ac14f02ae9d7.png)

https://raw.githubusercontent.com/elastic/beats/7.16/deploy/kubernetes/filebeat-kubernetes.yaml
https://raw.githubusercontent.com/elastic/beats/7.16/deploy/kubernetes/metricbeat-kubernetes.yaml

**If the log is not coming, link the relevant directory**
```
ln -s /var/lib/docker/containers /var/log/containers
```
