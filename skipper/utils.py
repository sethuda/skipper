import glob
import logging
import docker
import requests


def configure_logging(name, level):
    logger = logging.getLogger(name)

    formatter = logging.Formatter('[%(name)s] %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(console_handler)


def get_images_from_dockerfiles():
    dockerfiles = glob.glob('*.Dockerfile')
    images = [dockerfile.replace('.Dockerfile', '') for dockerfile in dockerfiles]
    return images


def get_local_images_info(images, registry=None):
    client = docker.Client()
    images_info = []
    for image in images:
        name = generate_fqdn_image(registry, image, None)
        images_info += [['LOCAL'] + list(fqdn_image.rsplit(':', 1)) for fqdn_image in client.images(name=name)[0]['RepoTags']]

    return images_info


def get_remote_images_info(images, registry):
    requests.packages.urllib3.disable_warnings()
    registry = registry.replace('dc1', 'dc1.strato')   # TODO: remove this
    images_info = []
    for image in images:
        url = 'https://%(registry)s/v2/%(image)s/tags/list' % dict(registry=registry, image=image)
        response = requests.get(url=url, verify=False)
        info = response.json()
        images_info += [['REMOTE', generate_fqdn_image(registry, image, None), tag] for tag in info['tags']]

    return images_info


def generate_fqdn_image(registry, image, tag='latest'):
    fqdn_image = image
    if registry is not None:
        fqdn_image = registry + '/' + fqdn_image
    if tag is not None:
        fqdn_image = fqdn_image + ':' + tag
    return fqdn_image