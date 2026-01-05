import os

from jinja2 import Environment, FileSystemLoader

from ansibledoctor.generator.collection_generator import CollectionTemplateContext
from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.galaxy import GalaxyMetadata


def test_render_license_badge():
    metadata = GalaxyMetadata(namespace="ns", name="coll", version="1.0.0", license=["MIT"])
    collection = AnsibleCollection(metadata=metadata)

    template_dir = os.path.abspath("ansibledoctor/generator/templates/markdown")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("collection.j2")

    context_builder = CollectionTemplateContext(collection=collection, plugins=[])
    context = context_builder.build()

    output = template.render(**context)

    assert "![License](https://img.shields.io/badge/license-MIT-blue.svg)" in output
