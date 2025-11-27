import re
from ansibledoctor.utils.slug import (
    collection_slug,
    role_slug,
    project_slug,
    join_hierarchy,
)
import re
from ansibledoctor.utils.slug import (
    collection_slug,
    role_slug,
    project_slug,
    join_hierarchy,
)


def test_project_slug_basic():
    assert project_slug("My Project") == "ansibleproject_my-project"
    assert project_slug("Café du Monde") == "ansibleproject_cafe-du-monde"


def test_collection_slug_basic():
    assert collection_slug("my-namespace", "my-collection") == "collection_my-namespace.my-collection"
    # underscores are converted to dashes in namespace for collections
    assert collection_slug("my_namespace", "my_collection") == "collection_my-namespace.my-collection"


def test_role_slug_allows_underscore():
    assert role_slug("my_namespace", "web_server") == "role_my_namespace.web-server"
    # role namespace preserves underscore
    assert role_slug("My_Namespace", "webserver") == "role_my_namespace.webserver"


def test_join_hierarchy_simple():
    proj = "ansibleproject_my-project"
    coll = "collection_my-namespace.my-collection"
    role = "role_my_namespace.webserver"

    assert (
        join_hierarchy(proj, coll, role)
        == "ansibleproject_my-project/collections/collection_my-namespace.my-collection/role_my_namespace.webserver"
    )


def test_slug_special_characters_and_spaces():
    assert project_slug("A  B   C") == "ansibleproject_a-b-c"
    assert project_slug("A---B___C") == "ansibleproject_a-b-c"


def test_slug_valid_characters_and_length():
    # Ensure only allowed characters (a-z, 0-9, dash) are present in the slug portion
    s = project_slug("Project Name with € symbols © and emojis 🚀")
    slug_portion = s.replace("ansibleproject_", "")
    assert re.match(r"^[a-z0-9-]+$", slug_portion)
    # confirm hyphenated words
    assert "project-name-with" in slug_portion
    *** End Patch
>>>>>>> 006-project-docs
