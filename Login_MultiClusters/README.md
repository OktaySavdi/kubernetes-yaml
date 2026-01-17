```shell
test_cluster_list=(
  #cluster_name,supervisor_name
  my_test_cluster1,my_supervisor_name1
  my_test_cluster2,my_supervisor_name2
  my_test_cluster3,my_supervisor_name3
)

prod_cluster_list=(
  #cluster_name,supervisor_name
  my_prod_cluster1,my_supervisor_name1
  my_prod_cluster2,my_supervisor_name2
  my_prod_cluster3,my_supervisor_name3
)

aks_cluster_list=(
  #cluster_name,resource_group,subscription
  azgwc-aks-nonprod-01,azgwc-rg-aks-nonprod-01,xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx
  azgwc-aks-prod-01,azgwc-rg-aks-prod-01,xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx
  azgwc-aks-dev-01,azgwc-rg-dev-01,xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx
)

function tkguser () {
	echo 'enter user - a-osavd'
	IFS= read -r  tkg_user < /dev/tty
}

function tkgpass () {
	echo 'enter pass'
	IFS= read -rs tkg_pass < /dev/tty
}

function aksuser () {
	echo 'enter aks user'
	IFS= read -r  aks_user < /dev/tty
}
function akspass () {
	echo 'enter aks pass'
	IFS= read -rs aks_pass < /dev/tty
}

function login-tkg-test () {
	[[ -z "${tkg_user}" ]] && tkguser
	[[ -z "${tkg_pass}" ]] && tkgpass
  export KUBECTL_VSPHERE_PASSWORD="${tkg_pass}"
  for cluster in ${test_cluster_list[@]}; do
		 echo "Logging in $(echo $cluster | cut -d"," -f1)"
     kubectl-vsphere login \
     --server=mysupervisor_cluster_test_name  \
     --vsphere-username="${tkg_user}@mydomain.com" \
     --tanzu-kubernetes-cluster-namespace="$(echo $cluster | cut -d"," -f2)" \
     --tanzu-kubernetes-cluster-name="$(echo $cluster | cut -d"," -f1)" --insecure-skip-tls-verify 2>&1 | grep -E "Logged in successfully|Error"
	done
}

function login-tkg-prod () {
	[[ -z "${tkg_user}" ]] && tkguser
	[[ -z "${tkg_pass}" ]] && tkgpass
  export KUBECTL_VSPHERE_PASSWORD="${tkg_pass}"
	for cluster in ${prod_cluster_list[@]}; do
		 echo "Logging in $(echo $cluster | cut -d"," -f1)"
     kubectl-vsphere login \
     --server=mysupervisor_cluster_prod_name \
     --vsphere-username="${tkg_user}@mydomain2.com" \
     --tanzu-kubernetes-cluster-namespace="$(echo $cluster | cut -d"," -f2)" \
     --tanzu-kubernetes-cluster-name="$(echo $cluster | cut -d"," -f1)" --insecure-skip-tls-verify 2>&1 | grep -E "Logged in successfully|Error"
	done
}

function login-aks () {
  [[ -z "${aks_user}" ]] && aksuser
	[[ -z "${aks_pass}" ]] && akspass
  az login -u "${aks_user}" -p "${aks_pass}" --tenant "xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx"
	for cluster in ${aks_cluster_list[@]}; do
		 echo "Logging in $(echo $cluster | cut -d"," -f1)"
     az account set --subscription "$(echo $cluster | cut -d"," -f3)"
     az aks get-credentials --resource-group "$(echo $cluster | cut -d"," -f2)" --name "$(echo $cluster | cut -d"," -f1)" --admin
	done
}
```
