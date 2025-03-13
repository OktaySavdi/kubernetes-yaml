# Copyright (c) 2024-2025 Broadcom. All Rights Reserved.
# Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.

import requests
import json
import subprocess
import re
import os
import logging
import argparse
usage = """
This script is designed to identify and clean up older container images
after a successful Supervisor upgrade. It ensures that the latest
images associated with the current release are retained by comparing the
images in the manifests (used as the source of truth) from location
/usr/lib/vmware-wcp/ with the existing images in the system.

Note: Ensure the Supervisor upgrade is fully completed before executing this script
to avoid removing images that might still be required.
"""


DEFAULT_REGISTRY = "http://localhost:5002"
DEFAULT_TMP_FILE = "/tmp/image_manifest.tmp"
# Bug: https://bugzilla-vcf.lvn.broadcom.net/show_bug.cgi?id=3471149
MANDATORY_SKIPPED_IMAGES = ["kubectl-plugin-vsphere"]
# Compile regex to match strings starting with "<" and ending with ">"
UNREPLACED_TAG_REGEX = re.compile(r"^<.*>$")

# Set up logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("remove_stale_images")


class ImageCleaner:
    def __init__(self, registry, tmp_file):
        self.used_images = {}
        self.registry = registry
        self.tmpFile = tmp_file
        self.init_used_images_from_kubernetes()

    def init_used_images_from_kubernetes(self):
        """
        Fetch and preprocess the list of used images in the Kubernetes cluster.
        """
        try:
            logger.info("Fetching Kubernetes images...")
            result = subprocess.run(
                ["kubectl", "get", "pods", "-A", "-o",
                    "jsonpath={.items[*].spec.containers[*].image}"],
                capture_output=True,
                text=True,
                check=True
            )
            used_images = set(result.stdout.split())
            self.used_images = used_images
        except subprocess.CalledProcessError as e:
            logger.warning('Failed to preload used images: {e}')

    def normalize_image_name(self, image) -> str:
        """Normalize the image name by removing the registry prefix, including localhost:5000."""
        if isinstance(image, str):
            return re.sub(r'^[^/]+/', '', image)
        return image

    def extract_image_name(self, image) -> str:
        """Extract the image name from the full image string."""
        match = re.match(r'^(.*)/([^:]+):([^@]+).*', image)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
        return None

    def extract_image_tag(self, image) -> str:
        """Extract the image tag from the full image string."""
        match = re.match(r'^.*:([^@]+).*', image)
        if match:
            return match.group(1)
        return None

    def is_image_used(self, image):
        """
        Check if the given image exists as a substring in any of the used images.
        """
        for used_image in self.used_images:
            if image in used_image:
                logger.debug(
                    'Image %s found as a substring in %s, marking it as in use.', image, used_image)
                return True
        logger.debug('Image %s is not a substring of any used images.', image)
        return False

    def fetch_containerd_images(self) -> set:
        """Fetch and filter containerd images that start with 'localhost'."""
        logger.info("Fetching containerd images...")
        result = subprocess.check_output(['crictl', 'images', '--output', 'json'])
        images_json = json.loads(result)
        images = []
        for image in images_json.get('images', []):
            for tag in image.get('repoTags', []):
                if tag.startswith('localhost'):
                    images.append(tag)

        return sorted(set(images))

    def fetch_manifest_images(self, manifest_dir):
        """Extract images from manifest files."""
        logger.info("Extracting images from manifests...")
        with open(self.tmpFile, 'w') as temp_file:
            subprocess.run(['find', manifest_dir, '-type', 'f', '(', '-name', '*.yaml',
                            '-o', '-name', '*.yml', ')', '-exec', 'grep', 'image:', '{}', ';'], stdout=temp_file)
        with open(self.tmpFile, 'r') as temp_file:
            manifest_images = re.findall(r'image: (localhost.*)', temp_file.read())
        return sorted(set(manifest_images))

    def get_digest(self, image) -> str:
        """Get the image digest from the registry."""
        repository, tag = image.split(":", 1)
        url = self.registry + "/v2/" + repository + "/manifests/" + tag
        headers = {
            "Accept": "application/vnd.docker.distribution.manifest.v2+json"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.headers.get("Docker-Content-Digest")
        else:
            logger.error(
                'Failed to get digest for %s: %s. HTTP %s: %s', repository, tag, response.status_code, response.text)
            return None

    def fetch_tags_and_digests_from_registry(self, image):
        """Fetch a map of tags and their digests for a specific image from the Docker registry."""
        url = f"{self.registry}/v2/{image}/tags/list"
        tags_response = requests.get(url)
        tags_response.raise_for_status()
        tags_data = tags_response.json()
        tags = tags_data.get("tags", [])

        # Fetch the digest for each tag
        tag_digest_map = {}
        for tag in tags:
            tag_digest_map[tag] = self.get_digest(f"{image}:{tag}")

        return tag_digest_map

    def delete_image_from_registry(self, image, digest) -> bool:
        """Delete the image using its digest."""
        repository, tag = image.split(":", 1)
        url = self.registry + "/v2/" + repository + "/manifests/" + digest
        try:
            response = requests.delete(url)
            response.raise_for_status()
            logger.info(
                'Successfully deleted image %s from registry', image)
            return True
        except requests.RequestException as e:
            logger.error('Failed to delete image %s: %s', image, e)
            return False

    def delete_image_from_containerd(self, image) -> bool:
        """Delete the image from containerd."""
        try:
            command = ["crictl", "rmi", image]
            subprocess.run(
                command, check=True, capture_output=True, text=True)
            logger.info(
                'Successfully deleted image %s from containerd', image)
            return True
        except subprocess.CalledProcessError as e:
            logger.error('Failed to delete image %s: %s', image, e)
            return False

    def get_nodename(self) -> str:
        """Fetch the hostname dynamically."""
        try:
            result = subprocess.run(["hostname"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to fetch hostname: {e}")
            return None

    def run_garbage_collect(self):
        """Run the garbage-collect command on the registry pod."""
        nodename = self.get_nodename()
        if not nodename:
            return
        pod_name = f"docker-registry-{nodename}"
        command = [
            "kubectl", "exec", "-n", "kube-system", pod_name, "--",
            "registry", "garbage-collect", "/etc/docker/registry/config.yaml"
        ]

        logger.info(f"Running garbage-collect in pod: {pod_name}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            logger.debug(f"Garbage collection output:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Garbage collection failed: {e.stderr}")

    def get_unused_image_tags(self, image_name, manifest_tags):
        """Return unused image tags by comparing the registry tag digest with manifest tag digest andg
        checking if mismatched tag exists in running pods"""
        unused_tags = []  # list of unused tags
        manifest_digest = []  # list of manifest digest considered as used image
        used_tags = [s for s in manifest_tags if not UNREPLACED_TAG_REGEX.match(s)]  # Filter out unreplaced tags
        normalized_image_name = self.normalize_image_name(image_name)

        logger.debug("normalized_image_name %s having used tags %s", normalized_image_name, used_tags)
        # creating manifest digest list
        manifest_digest.extend(self.get_digest(f"{normalized_image_name}:{tag}") for tag in used_tags)

        # fetching registry tags and its digest
        registry_tags = self.fetch_tags_and_digests_from_registry(normalized_image_name)
        logger.debug("image %s manifest_digest %s", normalized_image_name, manifest_digest)
        logger.debug("image %s registry_tags %s", normalized_image_name, registry_tags)
        for tag in registry_tags:
            digest = registry_tags[tag]
            # checking if registry image digest is not present in manifest digest list
            if digest not in manifest_digest:
                image = f"{image_name}:{tag}"
                # checking if image tag is in-use in Kubernetes pod
                if self.is_image_used(image):
                    logger.info('Skipping deletion for %s as it is used in pod', image)
                    continue
                # If the image tag digest is not found in any manifest and
                # is not being used in any pod, it is marked as an unused tag.
                unused_tags.append(tag)
        return unused_tags

    def delete_images(self, containerd_images_map, manifest_images_map, skip_images, dry_run):
        """Delete images from containerd and local registry that have different tags than in the manifest."""
        count = 0
        for image_name, containerd_tags in containerd_images_map.items():
            # skipping images mentioned in skip list
            if self.normalize_image_name(image_name) in skip_images:
                logger.info("Skipping image %s", image_name)
                continue

            # checking image exists in manifests
            if image_name in manifest_images_map:
                manifest_tags = manifest_images_map[image_name]
                unused_tags = self.get_unused_image_tags(image_name, manifest_tags)
                logger.debug('Containerd image: %s, containerd-tags: %s, manifest-tags: %s unused_tags: %s',
                             image_name, containerd_tags, manifest_tags, unused_tags)
                for tag in unused_tags:
                    image = f"{image_name}:{tag}"
                    count += 1
                    if dry_run:
                        logger.info(f"Dry run: {count}) Manifest tags: {manifest_tags}. "
                                    f"Deleting image: {image}")
                    else:
                        logger.info(f"{count}) Manifest tags: {manifest_tags}. "
                                    f"Deleting image: {image}")
                        normalized_image = self.normalize_image_name(image)
                        digest = self.get_digest(normalized_image)
                        if digest:
                            if self.delete_image_from_registry(normalized_image, digest):
                                if tag in containerd_tags:
                                    self.delete_image_from_containerd(image)
        if not dry_run:
            self.run_garbage_collect()

    def run(self, manifest_dir, skip_images, dry_run):
        """Clean unused images from local registry and containerd"""
        # Fetch containerd images and manifest images
        containerd_images = self.fetch_containerd_images()
        manifest_images = self.fetch_manifest_images(manifest_dir)

        # Build maps of containerd and manifest images
        containerd_images_map = {}
        manifest_images_map = {}

        for image in containerd_images:
            image_name = self.extract_image_name(image)
            image_tag = self.extract_image_tag(image)
            if image_name:
                if image_name not in containerd_images_map:
                    containerd_images_map[image_name] = set()
                containerd_images_map[image_name].add(image_tag)

        for manifest_image in manifest_images:
            image_name = self.extract_image_name(manifest_image)
            image_tag = self.extract_image_tag(manifest_image)
            if image_name:
                if image_name not in manifest_images_map:
                    manifest_images_map[image_name] = set()
                manifest_images_map[image_name].add(image_tag)

        self.delete_images(containerd_images_map, manifest_images_map, skip_images, dry_run)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('--run', action='store_true', help="Run the script to delete images instead of dry-run.")
    parser.add_argument(
        '--skip-image',
        action='append',
        help="Specify this flag multiple times to skip specific images.",
        default=[]
    )
    parser.add_argument(
        '--manifest-dir', type=str, default='/usr/lib/vmware-wcp/',
        help='Directory to search for manifest files (default: /usr/lib/vmware-wcp/).')
    return parser.parse_args()


def clean_stale_images():
    """
    Cleans up older container images that are no longer needed after a Supervisor upgrade.

    Note: This function compares the images listed in the manifests (used as the source of truth)
    with the images in the system. It should only be executed after the Supervisor upgrade
    has been confirmed successful to prevent deleting in-use images.
    """

    # Parse command line arguments
    args = parse_arguments()
    # Dry run is default, unless --run is passed
    dry_run = not args.run
    # Parse the skip images from comma-separated string into a list
    skip_images = args.skip_image if args.skip_image else []
    skip_images.extend(MANDATORY_SKIPPED_IMAGES)
    logger.debug("skipped image list %s", skip_images)
    manifest_dir = args.manifest_dir

    try:
        ImageCleaner(DEFAULT_REGISTRY, DEFAULT_TMP_FILE).run(manifest_dir, skip_images, dry_run)
    except Exception as e:
        logger.warning('Error while cleaning stale images %s', e)
    finally:
        if os.path.exists(DEFAULT_TMP_FILE):
            os.remove(DEFAULT_TMP_FILE)


clean_stale_images()
