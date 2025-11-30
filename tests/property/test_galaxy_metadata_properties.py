"""Property-based tests for GalaxyMetadata model using Hypothesis.

These tests verify that GalaxyMetadata behaves correctly with randomly
generated valid and invalid inputs, exploring edge cases automatically.

Following Constitution Article III (TDD): Property-based testing complements
example-based tests by exploring a wider input space.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from packaging.version import Version
from pydantic import ValidationError

from ansibledoctor.models.galaxy import GalaxyMetadata

# Valid namespace/name strategy: lowercase alphanumeric with underscores
valid_namespace_strategy = st.from_regex(r"^[a-z0-9_]{1,20}$", fullmatch=True)

# Valid semantic version strategy (strict: exactly 3 numeric parts)
valid_semver_strategy = st.builds(
    lambda major, minor, patch: f"{major}.{minor}.{patch}",
    major=st.integers(min_value=0, max_value=999),
    minor=st.integers(min_value=0, max_value=999),
    patch=st.integers(min_value=0, max_value=999),
)

# Invalid version strategy: strings that are NOT valid versions
# Note: packaging.version is VERY lenient (accepts "v1.0.0", "1.0.a", "1.2.3.4.5")
# So we test only truly invalid ones
invalid_version_strategy = st.one_of(
    st.just(""),  # Empty
    st.just("invalid"),
    st.just("1.x.0"),
    st.just(".."),
    st.just("!!!"),
    st.just("   "),  # Whitespace
)


class TestGalaxyMetadataProperties:
    """Property-based tests for GalaxyMetadata model."""

    @given(
        namespace=valid_namespace_strategy,
        name=valid_namespace_strategy,
        version=valid_semver_strategy,
        authors=st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=5),
    )
    def test_valid_galaxy_metadata_always_constructs(
        self,
        namespace: str,
        name: str,
        version: str,
        authors: list[str],
    ) -> None:
        """
        Property: Valid namespace, name, and version always create GalaxyMetadata.

        Given any valid namespace, name (matching pattern), and semantic version,
        GalaxyMetadata should successfully construct without raising errors.
        """
        metadata = GalaxyMetadata(
            namespace=namespace,
            name=name,
            version=version,
            authors=authors,
            dependencies={},
        )

        # Invariants
        assert metadata.namespace == namespace
        assert metadata.name == name
        assert metadata.version == version
        assert metadata.authors == authors
        assert metadata.fqcn == f"{namespace}.{name}"

        # Verify version is valid semantic version
        parsed_version = Version(version)
        assert isinstance(parsed_version, Version)

    @given(
        namespace=valid_namespace_strategy,
        name=valid_namespace_strategy,
    )
    def test_fqcn_property_always_matches_pattern(
        self,
        namespace: str,
        name: str,
    ) -> None:
        """
        Property: FQCN always follows "namespace.name" format.

        Given any valid namespace and name, the fqcn property should
        always be "{namespace}.{name}".
        """
        metadata = GalaxyMetadata(
            namespace=namespace,
            name=name,
            version="1.0.0",
            authors=[],
            dependencies={},
        )

        assert metadata.fqcn == f"{namespace}.{name}"
        assert "." in metadata.fqcn
        assert metadata.fqcn.count(".") == 1
        assert metadata.fqcn.startswith(namespace)
        assert metadata.fqcn.endswith(name)

    @given(
        namespace=st.one_of(
            st.from_regex(r"^[A-Z][a-z0-9_]*$", fullmatch=True),  # Starts uppercase
            st.just("Invalid-Name"),  # Hyphen
            st.just("invalid name"),  # Space
            st.just("invalid.name"),  # Dot
            st.just(""),  # Empty
        ),
    )
    def test_invalid_namespace_always_raises_validation_error(
        self,
        namespace: str,
    ) -> None:
        """
        Property: Invalid namespaces (uppercase, special chars) always rejected.

        Given any namespace that doesn't match the pattern ^[a-z0-9_]+$,
        GalaxyMetadata construction should fail with ValidationError.
        """
        with pytest.raises(ValidationError) as exc_info:
            GalaxyMetadata(
                namespace=namespace,
                name="valid_name",
                version="1.0.0",
                authors=[],
                dependencies={},
            )

        # Verify error is about namespace validation
        errors = exc_info.value.errors()
        assert any("namespace" in str(e).lower() for e in errors)

    @given(
        name=st.one_of(
            st.from_regex(r"^[A-Z][a-z0-9_]*$", fullmatch=True),  # Starts uppercase
            st.just("Invalid-Name"),  # Hyphen
            st.just("invalid name"),  # Space
            st.just("invalid.name"),  # Dot
            st.just(""),  # Empty
        ),
    )
    def test_invalid_name_always_raises_validation_error(
        self,
        name: str,
    ) -> None:
        """
        Property: Invalid names (uppercase, special chars) always rejected.

        Given any name that doesn't match the pattern ^[a-z0-9_]+$,
        GalaxyMetadata construction should fail with ValidationError.
        """
        with pytest.raises(ValidationError) as exc_info:
            GalaxyMetadata(
                namespace="valid_namespace",
                name=name,
                version="1.0.0",
                authors=[],
                dependencies={},
            )

        # Verify error is about name validation
        errors = exc_info.value.errors()
        assert any("name" in str(e).lower() for e in errors)

    @given(version=invalid_version_strategy)
    def test_invalid_version_always_raises_validation_error(
        self,
        version: str,
    ) -> None:
        """
        Property: Invalid semantic versions always rejected.

        Given any version string that is not a valid semantic version,
        GalaxyMetadata construction should fail with ValidationError.
        """
        with pytest.raises(ValidationError) as exc_info:
            GalaxyMetadata(
                namespace="valid_namespace",
                name="valid_name",
                version=version,
                authors=[],
                dependencies={},
            )

        # Verify error is about version validation
        errors = exc_info.value.errors()
        assert any("version" in str(e).lower() for e in errors)

    @given(
        namespace=valid_namespace_strategy,
        name=valid_namespace_strategy,
        version=valid_semver_strategy,
    )
    def test_galaxy_metadata_is_immutable(
        self,
        namespace: str,
        name: str,
        version: str,
    ) -> None:
        """
        Property: GalaxyMetadata is immutable (frozen).

        Given any valid GalaxyMetadata, attempting to modify fields
        should raise ValidationError (frozen model).
        """
        metadata = GalaxyMetadata(
            namespace=namespace,
            name=name,
            version=version,
            authors=[],
            dependencies={},
        )

        # Attempt to modify namespace
        with pytest.raises(ValidationError):
            metadata.namespace = "different_namespace"  # type: ignore

        # Attempt to modify name
        with pytest.raises(ValidationError):
            metadata.name = "different_name"  # type: ignore

        # Attempt to modify version
        with pytest.raises(ValidationError):
            metadata.version = "2.0.0"  # type: ignore

    @given(
        namespace=valid_namespace_strategy,
        name=valid_namespace_strategy,
        version=valid_semver_strategy,
        deps=st.dictionaries(
            keys=st.from_regex(r"^[a-z0-9_]+\.[a-z0-9_]+$", fullmatch=True),
            values=st.from_regex(r"^>=?\d+\.\d+\.\d+$", fullmatch=True),
            min_size=0,
            max_size=5,
        ),
    )
    def test_dependencies_always_stored_correctly(
        self,
        namespace: str,
        name: str,
        version: str,
        deps: dict[str, str],
    ) -> None:
        """
        Property: Dependencies are always stored as provided.

        Given any valid dependencies dictionary, GalaxyMetadata should
        store them exactly as provided without modification.
        """
        metadata = GalaxyMetadata(
            namespace=namespace,
            name=name,
            version=version,
            authors=[],
            dependencies=deps,
        )

        assert metadata.dependencies == deps
        assert len(metadata.dependencies) == len(deps)

        # Verify each dependency is preserved
        for dep_fqcn, version_constraint in deps.items():
            assert metadata.dependencies[dep_fqcn] == version_constraint

    @given(
        namespace=valid_namespace_strategy,
        name=valid_namespace_strategy,
        version=valid_semver_strategy,
    )
    def test_str_and_repr_always_contain_fqcn_and_version(
        self,
        namespace: str,
        name: str,
        version: str,
    ) -> None:
        """
        Property: __str__ and __repr__ always include FQCN and version.

        Given any valid GalaxyMetadata, the string representations should
        always contain the FQCN and version for identifiability.
        """
        metadata = GalaxyMetadata(
            namespace=namespace,
            name=name,
            version=version,
            authors=[],
            dependencies={},
        )

        str_repr = str(metadata)
        repr_repr = repr(metadata)

        # Verify FQCN appears in both
        assert namespace in str_repr
        assert name in str_repr
        assert namespace in repr_repr
        assert name in repr_repr

        # Verify version appears in both
        assert version in str_repr
        assert version in repr_repr
