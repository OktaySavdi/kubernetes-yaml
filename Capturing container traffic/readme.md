### Kubernetes Capturing container traffic

###  #Tcpdump

tcpdump is a powerful and common packet analyzer that runs under the command line. It allows the user to display TCP/IP and other packets being transmitted or received over an attached network interface

**install if there is no tcpdump in the pod**
```bash
#apt update && apt install tcpdump
Or
#kubectl cp tcpdump my-app-pod:/tmp/tcpdump
```
```bash
tcpdump -i eth0 -s 0 -w - /tmp/container.cap
kubectl exec my-app-pod -c nginx -- tcpdump -i eth0 -w - | wireshark -k -i -

kubectl cp my-app-pod:/tmp/container.cap /root/container.pcap
kubectl cp default/my-app-pod:tmp/container.cap /root/container.pcap
```
### #nsenter

Purpose: nsenter is a powerful tool allowing you to enter into any namespaces.

**Docker**
```bash
POD_NAME=nginx-f89759699-s6dgb
cid=$(docker ps | grep $pod_name | head -n 1 | awk '{ print $1 }')
pid=$(ps -ef | grep -v grep | grep -i $cid | awk '{print $2}')
nsenter -n -t $pid -- tcpdump -s 0 -n -i eth0 -w /tmp/$(hostname)-$(date +"%Y-%m-%d-%H-%M-%S").pcap
```
**CRI-O**
```bash
pod_name=nginx-6799fc88d8-n8st4
cid=$(crictl ps | grep $(echo $pod_name | cut -d- -f1) | head -n 1 | awk '{ print $1 }')
pid=$(crictl inspect $cid --output yaml | grep 'pid:' | awk '{ print $2 }')
nsenter -n -t $pid -- tcpdump -s 0 -n -i eth0 -w /tmp/$(hostname)-$(date +"%Y-%m-%d-%H-%M-%S").pcap
```
###  #İperf

Purpose: test networking performance between two containers/hosts.
```bash
iperf -s -p 9999
iperf -c perf-test-a -p 9999
```
🐳  → docker logs ce4ff40a5456
```bash
Server listening on TCP port 9999  
TCP window size: 85.3 KByte (default)  
[  4] local 10.0.3.3 port 9999 connected with 10.0.3.5 port 35102  
[ ID] Interval  Transfer  Bandwidth  
[  4]  0.0-10.0 sec  32.7 GBytes  28.1 Gbits/sec  
[  5] local 10.0.3.3 port 9999 connected with 10.0.3.5 port 35112
```
###  #nmap

nmap ("Network Mapper") is an open source tool for network exploration and security auditing. It is very useful for scanning to see which ports are open between a given set of hosts.

🐳  → nmap -p 12376-12390 -dd 172.31.24.25  
```bash
...  
Discovered closed port 12388/tcp on 172.31.24.25  
Discovered closed port 12379/tcp on 172.31.24.25  
Discovered closed port 12389/tcp on 172.31.24.25  
Discovered closed port 12376/tcp on 172.31.24.25  
...

-   open: the pathway to the port is open and there is an application listening on this port.
-   closed: the pathway to the port is open but there is no application listening on this port.
-   filtered: the pathway to the port is closed, blocked by a firewall, routing rules, or host-based rules.
```
### #drill

Purpose: drill is a tool to designed to get all sorts of information out of the DNS.

🐳  → drill -V 5 perf-test-b  
```bash
;; ->>HEADER<<- opcode: QUERY, rcode: NOERROR, id: 0  
;; flags: rd ; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 0  
;; QUESTION SECTION:  
;; perf-test-b. IN A

;; ANSWER SECTION:

;; AUTHORITY SECTION:

;; ADDITIONAL SECTION:

;; Query time: 0 msec  
;; WHEN: Thu Aug 18 02:08:47 2016  
;; MSG SIZE  rcvd: 0  
;; ->>HEADER<<- opcode: QUERY, rcode: NOERROR, id: 52723  
;; flags: qr rd ra ; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0  
;; QUESTION SECTION:  
;; perf-test-b. IN A

;; ANSWER SECTION:  
perf-test-b. 600 IN A 10.0.3.4 <<<<<<<<<<<<<<<<<<<<<<<<<< Service VIP

;; AUTHORITY SECTION:

;; ADDITIONAL SECTION:

;; Query time: 1 msec  
;; SERVER: 127.0.0.11 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Local resolver  
;; WHEN: Thu Aug 18 02:08:47 2016  
;; MSG SIZE  rcvd: 56
```
