"""Property-based tests for collection structure validation using Hypothesis.

These tests verify that AnsibleCollection behaves correctly with randomly
generated collection structures (varying numbers of roles and plugins).

Following Constitution Article III (TDD): Property-based testing explores
edge cases like empty collections, many roles/plugins, etc.
"""

from hypothesis import given, strategies as st
from pydantic import ValidationError
import pytest

from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.galaxy import GalaxyMetadata
from ansibledoctor.models.plugin import PluginType


# Valid role name strategy
valid_role_name_strategy = st.from_regex(r"^[a-z][a-z0-9_]{0,19}$", fullmatch=True)

# Valid plugin filename strategy (Python files)
valid_plugin_filename_strategy = st.from_regex(
    r"^[a-z][a-z0-9_]{0,15}\.py$",
    fullmatch=True
)

# Galaxy metadata strategy
def galaxy_metadata_strategy():
    """Generate valid GalaxyMetadata for testing."""
    return st.builds(
        lambda ns, name, ver: GalaxyMetadata(
            namespace=ns,
            name=name,
            version=f"{ver[0]}.{ver[1]}.{ver[2]}",
            authors=["Test Author"],
            dependencies={},
        ),
        ns=st.from_regex(r"^[a-z0-9_]{1,10}$", fullmatch=True),
        name=st.from_regex(r"^[a-z0-9_]{1,10}$", fullmatch=True),
        ver=st.tuples(
            st.integers(min_value=0, max_value=10),
            st.integers(min_value=0, max_value=10),
            st.integers(min_value=0, max_value=10),
        ),
    )


class TestCollectionStructureProperties:
    """Property-based tests for AnsibleCollection structure."""
    
    @given(
        metadata=galaxy_metadata_strategy(),
        num_roles=st.integers(min_value=0, max_value=10),
        num_modules=st.integers(min_value=0, max_value=20),
    )
    def test_collection_with_random_structure_always_constructs(
        self,
        metadata: GalaxyMetadata,
        num_roles: int,
        num_modules: int,
    ) -> None:
        """
        Property: Collection with any valid role/plugin count constructs.
        
        Given any number of roles (0-10) and plugins (0-20), AnsibleCollection
        should successfully construct.
        """
        # Generate unique role names
        roles = [f"role_{i}" for i in range(num_roles)]
        
        # Generate unique module names
        plugins = {
            PluginType.MODULE: [f"module_{i}.py" for i in range(num_modules)]
        }
        
        collection = AnsibleCollection(
            metadata=metadata,
            roles=roles,
            plugins=plugins,
        )
        
        # Invariants
        assert collection.fqcn == metadata.fqcn
        assert len(collection.list_roles()) == num_roles
        assert len(collection.list_plugins_by_type(PluginType.MODULE)) == num_modules
        assert collection.metadata == metadata
    
    @given(
        metadata=galaxy_metadata_strategy(),
        role_count=st.integers(min_value=0, max_value=10),
    )
    def test_list_roles_returns_all_roles(
        self,
        metadata: GalaxyMetadata,
        role_count: int,
    ) -> None:
        """
        Property: list_roles() always returns all roles.
        
        Given any collection with N roles, list_roles() should return
        exactly N role names.
        """
        roles = [f"role_{i}" for i in range(role_count)]
        
        collection = AnsibleCollection(
            metadata=metadata,
            roles=roles,
            plugins={},
        )
        
        result = collection.list_roles()
        assert len(result) == role_count
        assert result == roles
    
    @given(
        metadata=galaxy_metadata_strategy(),
    )
    def test_empty_collection_is_valid(
        self,
        metadata: GalaxyMetadata,
    ) -> None:
        """
        Property: Empty collections (no roles, no plugins) are valid.
        
        Given any valid metadata, a collection with zero roles and plugins
        should successfully construct.
        """
        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={},
        )
        
        assert collection.fqcn == metadata.fqcn
        assert len(collection.list_roles()) == 0
        assert collection.plugins == {}
    
    @given(
        metadata=galaxy_metadata_strategy(),
        plugin_counts=st.fixed_dictionaries({
            "modules": st.integers(min_value=0, max_value=10),
            "filters": st.integers(min_value=0, max_value=10),
            "lookups": st.integers(min_value=0, max_value=10),
        }),
    )
    def test_multiple_plugin_types_construct_correctly(
        self,
        metadata: GalaxyMetadata,
        plugin_counts: dict,
    ) -> None:
        """
        Property: Collections with multiple plugin types construct correctly.
        
        Given any combination of plugin type counts, the collection should
        store them correctly.
        """
        plugins = {
            PluginType.MODULE: [f"mod_{i}.py" for i in range(plugin_counts["modules"])],
            PluginType.FILTER: [f"filt_{i}.py" for i in range(plugin_counts["filters"])],
            PluginType.LOOKUP: [f"look_{i}.py" for i in range(plugin_counts["lookups"])],
        }
        
        # Remove empty plugin types
        plugins = {k: v for k, v in plugins.items() if v}
        
        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins=plugins,
        )
        
        # Verify each plugin type count
        assert len(collection.list_plugins_by_type(PluginType.MODULE)) == plugin_counts["modules"]
        assert len(collection.list_plugins_by_type(PluginType.FILTER)) == plugin_counts["filters"]
        assert len(collection.list_plugins_by_type(PluginType.LOOKUP)) == plugin_counts["lookups"]
    
    @given(
        metadata=galaxy_metadata_strategy(),
        role_count=st.integers(min_value=1, max_value=10),
    )
    def test_collection_fqcn_always_delegates_to_metadata(
        self,
        metadata: GalaxyMetadata,
        role_count: int,
    ) -> None:
        """
        Property: Collection FQCN always equals metadata FQCN.
        
        Given any collection, its fqcn property should always match
        the metadata's fqcn (delegation pattern).
        """
        roles = [f"role_{i}" for i in range(role_count)]
        
        collection = AnsibleCollection(
            metadata=metadata,
            roles=roles,
            plugins={},
        )
        
        assert collection.fqcn == metadata.fqcn
        assert "." in collection.fqcn
        assert collection.fqcn == f"{metadata.namespace}.{metadata.name}"
    
    @given(
        namespace=st.from_regex(r"^[a-z0-9_]{1,10}$", fullmatch=True),
        name=st.from_regex(r"^[a-z0-9_]{1,10}$", fullmatch=True),
    )
    def test_self_dependency_always_raises_validation_error(
        self,
        namespace: str,
        name: str,
    ) -> None:
        """
        Property: Collections cannot depend on themselves (circular reference).
        
        Given any collection metadata with a self-dependency, construction
        should fail with ValidationError.
        """
        fqcn = f"{namespace}.{name}"
        
        # Create metadata with self-dependency
        metadata = GalaxyMetadata(
            namespace=namespace,
            name=name,
            version="1.0.0",
            authors=["Test"],
            dependencies={fqcn: ">=1.0.0"},  # Self-dependency!
        )
        
        with pytest.raises(ValidationError) as exc_info:
            AnsibleCollection(
                metadata=metadata,
                roles=[],
                plugins={},
            )
        
        # Verify error mentions self-dependency
        error_msg = str(exc_info.value)
        assert "itself" in error_msg.lower() or "self" in error_msg.lower()
    
    @given(
        metadata=galaxy_metadata_strategy(),
        plugin_type=st.sampled_from(list(PluginType)),
        plugin_count=st.integers(min_value=0, max_value=20),
    )
    def test_list_plugins_by_type_returns_correct_count(
        self,
        metadata: GalaxyMetadata,
        plugin_type: PluginType,
        plugin_count: int,
    ) -> None:
        """
        Property: list_plugins_by_type() returns correct plugin count.
        
        Given a collection with N plugins of a specific type,
        list_plugins_by_type() should return exactly N plugin names.
        """
        plugins = {
            plugin_type: [f"plugin_{i}.py" for i in range(plugin_count)]
        }
        
        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins=plugins,
        )
        
        result = collection.list_plugins_by_type(plugin_type)
        assert len(result) == plugin_count
        
        # For other plugin types, should return empty list
        other_types = [pt for pt in PluginType if pt != plugin_type]
        for other_type in other_types:
            assert len(collection.list_plugins_by_type(other_type)) == 0
    
    @given(
        metadata=galaxy_metadata_strategy(),
        roles=st.lists(valid_role_name_strategy, min_size=0, max_size=10, unique=True),
        modules=st.lists(valid_plugin_filename_strategy, min_size=0, max_size=20, unique=True),
    )
    def test_collection_str_and_repr_contain_fqcn(
        self,
        metadata: GalaxyMetadata,
        roles: list[str],
        modules: list[str],
    ) -> None:
        """
        Property: __str__ and __repr__ always contain FQCN.
        
        Given any collection, string representations should include
        the FQCN for identifiability.
        """
        plugins = {PluginType.MODULE: modules} if modules else {}
        
        collection = AnsibleCollection(
            metadata=metadata,
            roles=roles,
            plugins=plugins,
        )
        
        str_repr = str(collection)
        repr_repr = repr(collection)
        
        # Verify FQCN appears in both
        assert metadata.namespace in str_repr
        assert metadata.name in str_repr
        assert metadata.namespace in repr_repr or metadata.fqcn in repr_repr
    
    @given(
        metadata=galaxy_metadata_strategy(),
        role_count=st.integers(min_value=0, max_value=10),
        module_count=st.integers(min_value=0, max_value=20),
    )
    def test_large_collections_perform_reasonably(
        self,
        metadata: GalaxyMetadata,
        role_count: int,
        module_count: int,
    ) -> None:
        """
        Property: Large collections (10 roles, 20 plugins) construct quickly.
        
        Given a collection with maximum tested size, construction and
        method calls should complete without performance issues.
        """
        roles = [f"role_{i}" for i in range(role_count)]
        plugins = {
            PluginType.MODULE: [f"module_{i}.py" for i in range(module_count)]
        }
        
        # Construction should be fast
        collection = AnsibleCollection(
            metadata=metadata,
            roles=roles,
            plugins=plugins,
        )
        
        # Method calls should be fast
        assert len(collection.list_roles()) == role_count
        assert len(collection.list_plugins_by_type(PluginType.MODULE)) == module_count
        assert collection.fqcn == metadata.fqcn
        
        # String conversion should work
        str(collection)
        repr(collection)
