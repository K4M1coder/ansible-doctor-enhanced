import importlib


def test_collection_slug_format():
    slug_module = importlib.import_module("ansibledoctor.utils.slug")
    # Namespace and collection name with spaces and mixed case
    ns = "My Namespace"
    name = "My Collection"
    result = slug_module.collection_slug(ns, name)
    assert result.startswith("collection_"), "collection_slug must start with 'collection_'"
    # Expect lowercase and spaces replaced with hyphens, dot separator
    assert result == "collection_my-namespace.my-collection"


def test_role_slug_format():
    slug_module = importlib.import_module("ansibledoctor.utils.slug")
    ns = "my_namespace"
    name = "WebServer"
    result = slug_module.role_slug(ns, name)
    assert result.startswith("role_"), "role_slug must start with 'role_'"
    assert result == "role_my_namespace.webserver"


def test_project_slug_format():
    slug_module = importlib.import_module("ansibledoctor.utils.slug")
    name = "My Project"
    result = slug_module.project_slug(name)
    assert result.startswith("ansibleproject_"), "project_slug must start with 'ansibleproject_'"
    assert result == "ansibleproject_my-project"


def test_slug_hierarchy_join():
    slug_module = importlib.import_module("ansibledoctor.utils.slug")
    p = slug_module.project_slug("My Project")
    c = slug_module.collection_slug("My Namespace", "My Collection")
    r = slug_module.role_slug("my_namespace", "webserver")
    # Expect the hierarchical path join to include slugs and preserve dots
    joined = slug_module.join_hierarchy(p, c, r)
    assert "ansibleproject_my-project" in joined
    assert "collection_my-namespace.my-collection" in joined
    assert "role_my_namespace.webserver" in joined
    # Example path
    assert joined == "ansibleproject_my-project/collections/collection_my-namespace.my-collection/role_my_namespace.webserver"
