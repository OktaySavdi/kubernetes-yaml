# Copyright (c) 2024 Broadcom. All Rights Reserved.
# Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.

"""
This script identifies and removes stale ReplicaSets from the Supervisor cluster.
It also saves the YAML of the deleted ReplicaSets to a file.

The script should be executed on one of the master nodes, and the
'deleted_replicasets_{timestamp}.yaml' file needs to be copied to VC. Afterward,
roll out the EAM agencies sequentially to recreate the new CPVMs.

Note: Ensure the Supervisor upgrade is fully completed before executing this script
to avoid removing replicasets that might still be required.
"""

import subprocess
import json
import argparse
import logging
import re
from datetime import datetime

NAMESPACE_REGEX = re.compile('^(kube-system|vmware-system-.*|svc-.*)$')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_replicasets():
    """Fetch ReplicaSets from all namespaces."""
    cmd = ["kubectl", "get", "replicasets", "--all-namespaces", "-o", "json"]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        logging.error(f"Failed to fetch ReplicaSets: {result.stderr}")
        return []

    try:
        rs = []
        for item in json.loads(result.stdout)['items']:
            # skip non kubernetes cluster resources
            if not NAMESPACE_REGEX.match(item['metadata']['namespace']):
                continue
            rs.append(item)
        return rs
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
        return []


def get_deployment_revisions():
    """Fetch the latest revision for each deployment."""
    cmd = ["kubectl", "get", "deployments", "--all-namespaces", "-o", "json"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        logging.error(f"Failed to fetch deployments: {result.stderr}")
        return {}

    deployments = {}
    try:
        items = json.loads(result.stdout)["items"]
        for dep in items:
            name = dep["metadata"]["name"]
            namespace = dep["metadata"]["namespace"]
            if not NAMESPACE_REGEX.match(namespace):
                continue
            latest_revision = int(dep["metadata"]["annotations"].get("deployment.kubernetes.io/revision", 0))
            deployments[(namespace, name)] = latest_revision
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON for deployments: {e}")

    return deployments


def get_image(rs):
    """Extract the image from a ReplicaSet."""
    containers = rs.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
    return [container.get("image") for container in containers]


def filter_redundant_replicasets(replicasets, deployment_revisions):
    """Filter out redundant ReplicaSets that have 0 replicas."""
    rs_by_ns_deployment = {}
    latest_rs_by_ns_deployment = {}

    for rs in replicasets:
        revision = int(rs.get("metadata", {}).get("annotations", {}).get("deployment.kubernetes.io/revision", 0))
        replicas = rs.get("spec", {}).get("replicas", 0)

        # Get the deployment name from ownerReferences
        owner_references = rs.get("metadata", {}).get("ownerReferences", [])
        deployment = owner_references[0].get("name")
        namespace = rs["metadata"]["namespace"]

        if (namespace, deployment) not in rs_by_ns_deployment:
            rs_by_ns_deployment[(namespace, deployment)] = []

        rs_details = {
            "name": rs["metadata"]["name"],
            "namespace": namespace,
            "deployment": deployment,
            "replicas": replicas,
            "revision": revision,
            "image": get_image(rs)
        }
        rs_by_ns_deployment[(namespace, deployment)].append(rs_details)

        # Get latest ReplicaSet revision number
        latest_revision = deployment_revisions.get((rs["metadata"]["namespace"], deployment))
        # Storing latest revision details of the deployment
        if revision == latest_revision and replicas > 0:
            latest_rs_by_ns_deployment[(namespace, deployment)] = rs_details

    to_delete = []
    latest_revisions = {}
    for (namespace, deployment), rs_list in rs_by_ns_deployment.items():
        # Skip deployments with only one ReplicaSet
        if len(rs_list) <= 1:
            continue

        latest_active_rs = latest_rs_by_ns_deployment[(namespace, deployment)]

        if latest_active_rs:
            latest_revisions[(namespace, deployment)] = latest_active_rs
            # Mark all older ReplicaSets with 0 replicas for deletion
            for rs in rs_list:
                if rs["replicas"] == 0 and rs["revision"] != latest_active_rs["revision"]:
                    to_delete.append(rs)

    return to_delete, latest_revisions


def dump_replicaset_yaml(replicaset, dump_file):
    """Dump the full YAML of the ReplicaSet into the specified file."""
    cmd = ["kubectl", "get", "replicaset", replicaset["name"], "-n", replicaset["namespace"], "-o", "yaml"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        logging.error(f"Failed to get YAML for ReplicaSet {replicaset['name']}: {result.stderr}")
        return None

    # Write the full YAML of the ReplicaSet to the file with a separator
    with open(dump_file, "a") as f:
        f.write(f"# YAML of ReplicaSet {replicaset['name']} in namespace {replicaset['namespace']}\n")
        f.write(result.stdout + "\n---\n")


def delete_replicasets(replicasets, dump_file):
    """Delete the specified ReplicaSets and dump their YAML to a file."""
    for rs in replicasets:
        dump_replicaset_yaml(rs, dump_file)
        cmd = ["kubectl", "delete", "replicaset", rs["name"], "-n", rs["namespace"]]
        logging.info(f"Deleting ReplicaSet {rs['name']} in namespace {rs['namespace']}")

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logging.error(f"Failed to delete ReplicaSet {rs['name']}: {result.stderr}")
        else:
            logging.info(f"Successfully deleted ReplicaSet {rs['name']}")


def main():
    """Main function to execute the script."""
    parser = argparse.ArgumentParser(description=(
        "This script identifies and removes stale ReplicaSets from the Supervisor cluster. "
        "It also saves the YAML of the deleted ReplicaSets to a file. "

        "The script should be executed on one of the master nodes, and the"
        "'deleted_replicasets_{timestamp}.yaml' file needs to be copied to VC. Afterward,"
        "roll out the EAM agencies sequentially to recreate the new CPVMs. "

        "Note: Ensure the Supervisor upgrade is fully completed before executing this script"
        "to avoid removing replicasets that might still be required."
    ))
    parser.add_argument("--run", action="store_true",
                        default=False, help="Actually delete the ReplicaSets (default: dry-run)")

    # File to dump YAML of deleted ReplicaSets
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_file = f"deleted_replicasets_{timestamp}.yaml"

    args = parser.parse_args()

    replicasets = get_replicasets()
    deployment_revisions = get_deployment_revisions()
    redundant_replicasets, latest_revisions = filter_redundant_replicasets(replicasets, deployment_revisions)
    if not redundant_replicasets:
        logging.info("No redundant ReplicaSets found")
        return
    # If in dry-run mode, log the details and exit
    if not args.run:
        logging.info("Dry-run: The following ReplicaSets would be deleted:")

        for rs in redundant_replicasets:
            logging.info(
                f" - ReplicaSet: {rs['name']}, Namespace: {rs['namespace']}, "
                f"Deployment: {rs['deployment']}, Image: {rs['image']}")

        logging.info("Latest revisions of ReplicaSets:")
        for (namespace, deployment), info in latest_revisions.items():
            logging.info(f" - Latest ReplicaSet: {info['name']}, "
                         f"Namespace: {namespace}, Deployment: {deployment}, "
                         f"Image: {info['image']}")
        return

    delete_replicasets(redundant_replicasets, dump_file)


if __name__ == "__main__":
    main()
