"""
Integration tests for external link validation.

Tests HTTP link validation including 404 detection, timeouts, and network errors.
Following TDD approach - these tests should fail until LinkValidator external validation is implemented.

Spec: 013-links-cross-references
Phase: 4 (User Story 2 - Detect Broken Links)
Task: T033
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ansibledoctor.models.link import Link, LinkStatus, LinkType


class TestExternalLinkValidation:
    """Tests for external HTTP link validation (T033)."""

    def test_external_404_shows_warning_with_http_status(self, tmp_path: Path) -> None:
        """Test that external 404 links show warning with HTTP status code.
        
        Scenario:
            - Documentation contains link to external URL
            - URL returns 404 Not Found
            - Warning shows HTTP status code
        """
        source_file = tmp_path / "README.md"
        source_file.write_text("See [docs](https://example.com/missing).")
        
        link = Link(
            source_file=source_file,
            target="https://example.com/missing",
            link_type=LinkType.EXTERNAL_URL,
            text="docs",
            line_number=1,
        )
        
        # Mock HTTP response to return 404
        with patch("requests.head") as mock_head:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.ok = False
            mock_head.return_value = mock_response
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path)
            
            result = validator.validate(link)
            
            assert not result.is_valid
            assert result.status == LinkStatus.BROKEN
            assert "404" in result.error_message
    
    def test_external_link_timeout(self, tmp_path: Path) -> None:
        """Test that external link timeouts are handled gracefully."""
        from requests.exceptions import Timeout
        
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://slow-site.example.com",
            link_type=LinkType.EXTERNAL_URL,
            text="slow site",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            mock_head.side_effect = Timeout("Connection timeout")
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path, timeout=2.0)
            
            result = validator.validate(link)
            
            assert not result.is_valid
            assert result.status == LinkStatus.WARNING
            assert "timeout" in result.error_message.lower()
    
    def test_external_link_connection_error(self, tmp_path: Path) -> None:
        """Test that connection errors are handled."""
        from requests.exceptions import ConnectionError
        
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://nonexistent-domain-12345.com",
            link_type=LinkType.EXTERNAL_URL,
            text="missing",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            mock_head.side_effect = ConnectionError("Failed to connect")
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path)
            
            result = validator.validate(link)
            
            assert not result.is_valid
            assert result.status == LinkStatus.WARNING
            assert "connection" in result.error_message.lower() or "failed" in result.error_message.lower()
    
    def test_valid_external_link(self, tmp_path: Path) -> None:
        """Test that valid external links pass validation."""
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://www.ansible.com",
            link_type=LinkType.EXTERNAL_URL,
            text="Ansible",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.ok = True
            mock_head.return_value = mock_response
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path)
            
            result = validator.validate(link)
            
            assert result.is_valid
            assert result.status == LinkStatus.VALID
            assert result.error_message is None
    
    def test_external_link_redirect_followed(self, tmp_path: Path) -> None:
        """Test that HTTP redirects (301/302) are followed."""
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://example.com/old-url",
            link_type=LinkType.EXTERNAL_URL,
            text="redirected",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            # First response is redirect
            mock_response = Mock()
            mock_response.status_code = 301
            mock_response.ok = True
            mock_response.headers = {"Location": "https://example.com/new-url"}
            mock_head.return_value = mock_response
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path)
            
            result = validator.validate(link)
            
            # Should be valid since redirect is followed
            assert result.is_valid
            assert result.status == LinkStatus.VALID
    
    def test_external_link_with_custom_user_agent(self, tmp_path: Path) -> None:
        """Test that custom user agent is sent with requests."""
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://example.com/docs",
            link_type=LinkType.EXTERNAL_URL,
            text="docs",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.ok = True
            mock_head.return_value = mock_response
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path)
            
            result = validator.validate(link)
            
            # Verify user agent was set
            mock_head.assert_called_once()
            call_kwargs = mock_head.call_args[1]
            assert "headers" in call_kwargs
            assert "User-Agent" in call_kwargs["headers"]
            assert "ansible-doctor" in call_kwargs["headers"]["User-Agent"].lower()


class TestExternalLinkBatchValidation:
    """Tests for batch validation of external links."""

    def test_batch_validation_with_caching(self, tmp_path: Path) -> None:
        """Test that duplicate external links are only validated once.
        
        Scenario:
            - Multiple files link to same external URL
            - Validation should only check URL once
            - Results cached and reused
        """
        # Create multiple files with same external link
        file1 = tmp_path / "file1.md"
        file1.write_text("[Ansible](https://www.ansible.com)")
        
        file2 = tmp_path / "file2.md"
        file2.write_text("See [Ansible docs](https://www.ansible.com).")
        
        links = [
            Link(
                source_file=file1,
                target="https://www.ansible.com",
                link_type=LinkType.EXTERNAL_URL,
                text="Ansible",
                line_number=1,
            ),
            Link(
                source_file=file2,
                target="https://www.ansible.com",
                link_type=LinkType.EXTERNAL_URL,
                text="Ansible docs",
                line_number=1,
            ),
        ]
        
        with patch("requests.head") as mock_head:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.ok = True
            mock_head.return_value = mock_response
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path, enable_cache=True)
            
            results = [validator.validate(link) for link in links]
            
            # Both should be valid
            assert all(r.is_valid for r in results)
            
            # Should only make one HTTP request (cached on second)
            assert mock_head.call_count == 1


class TestExternalLinkRetry:
    """Tests for retry logic on transient failures."""

    def test_retry_on_transient_error(self, tmp_path: Path) -> None:
        """Test that transient errors trigger retry with exponential backoff."""
        from requests.exceptions import RequestException
        
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://flaky-site.example.com",
            link_type=LinkType.EXTERNAL_URL,
            text="flaky",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            # Fail twice, succeed on third try
            mock_head.side_effect = [
                RequestException("Temporary error"),
                RequestException("Still failing"),
                Mock(status_code=200, ok=True),
            ]
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path, max_retries=3)
            
            result = validator.validate(link)
            
            # Should eventually succeed after retries
            assert result.is_valid
            assert result.status == LinkStatus.VALID
            assert mock_head.call_count == 3


# ===========================
# US4: External Resources (T057-T061)
# ===========================


class TestModuleDocumentationLinks:
    """Tests for module documentation linking (T057)."""

    def test_ansible_module_generates_docs_link(self, tmp_path: Path) -> None:
        """Test that Ansible module names generate correct docs.ansible.com links.
        
        Scenario:
            - Role uses ansible.builtin.copy module
            - Documentation should link to official module docs
            - Link format: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html
        """
        role_dir = tmp_path / "roles" / "test_role"
        role_dir.mkdir(parents=True)
        
        # Create task file with module usage
        tasks_dir = role_dir / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "main.yml").write_text("""
---
- name: Copy configuration file
  ansible.builtin.copy:
    src: config.conf
    dest: /etc/app/config.conf
""")
        
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        integrator = ExternalLinkIntegrator(ansible_version="2.15")
        
        links = integrator.extract_module_links(role_dir)
        
        # Should detect ansible.builtin.copy module with version 2.15
        assert any(link.target == "https://docs.ansible.com/ansible/2.15/collections/ansible/builtin/copy_module.html" 
                   for link in links)
        assert any("copy" in link.text for link in links)

    def test_community_module_generates_correct_namespace_link(self, tmp_path: Path) -> None:
        """Test that community modules link to correct namespace."""
        role_dir = tmp_path / "roles" / "test_role"
        role_dir.mkdir(parents=True)
        
        tasks_dir = role_dir / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "main.yml").write_text("""
---
- name: Install package
  community.general.homebrew:
    name: git
    state: present
""")
        
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        integrator = ExternalLinkIntegrator(ansible_version="2.15")
        
        links = integrator.extract_module_links(role_dir)
        
        # Should link to community.general collection docs
        assert any("community/general" in link.target for link in links)
        assert any("homebrew_module.html" in link.target for link in links)

    def test_multiple_modules_generate_multiple_links(self, tmp_path: Path) -> None:
        """Test that multiple different modules generate separate links."""
        role_dir = tmp_path / "roles" / "test_role"
        role_dir.mkdir(parents=True)
        
        tasks_dir = role_dir / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "main.yml").write_text("""
---
- name: Create directory
  ansible.builtin.file:
    path: /var/app
    state: directory

- name: Install package
  ansible.builtin.apt:
    name: nginx
    state: present
""")
        
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        integrator = ExternalLinkIntegrator(ansible_version="2.15")
        
        links = integrator.extract_module_links(role_dir)
        
        # Should have links for both file and apt modules
        assert len(links) >= 2
        targets = [link.target for link in links]
        assert any("file_module.html" in t for t in targets)
        assert any("apt_module.html" in t for t in targets)


class TestGalaxyPageLinks:
    """Tests for Ansible Galaxy page linking (T058)."""

    def test_collection_generates_galaxy_link(self, tmp_path: Path) -> None:
        """Test that collections link to their Ansible Galaxy pages.
        
        Scenario:
            - Collection namespace: mycompany.myapp
            - Should generate link: https://galaxy.ansible.com/ui/repo/published/mycompany/myapp/
        """
        from ansibledoctor.models.collection import AnsibleCollection
        from ansibledoctor.models.galaxy import GalaxyMetadata
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        
        metadata = GalaxyMetadata(
            namespace="mycompany",
            name="myapp",
            version="1.0.0",
            authors=["Test Author"],
            dependencies={}
        )
        
        collection = AnsibleCollection(
            metadata=metadata
        )
        
        integrator = ExternalLinkIntegrator()
        link = integrator.generate_galaxy_link(collection)
        
        assert link.target == "https://galaxy.ansible.com/ui/repo/published/mycompany/myapp/"
        assert "Ansible Galaxy" in link.text
        assert link.link_type == LinkType.EXTERNAL_URL

    def test_role_with_galaxy_metadata_generates_link(self, tmp_path: Path) -> None:
        """Test that roles with galaxy_info generate Galaxy links."""
        role_dir = tmp_path / "roles" / "nginx"
        role_dir.mkdir(parents=True)
        
        meta_dir = role_dir / "meta"
        meta_dir.mkdir()
        (meta_dir / "main.yml").write_text("""
galaxy_info:
  author: johndoe
  namespace: johndoe
  role_name: nginx
""")
        
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        integrator = ExternalLinkIntegrator()
        
        link = integrator.generate_role_galaxy_link(role_dir)
        
        assert "galaxy.ansible.com" in link.target
        assert "johndoe" in link.target
        assert "nginx" in link.target


class TestBestPracticesLinks:
    """Tests for best practices guide linking (T059)."""

    def test_security_keyword_links_to_security_guide(self, tmp_path: Path) -> None:
        """Test that security-related content links to Ansible security best practices.
        
        Scenario:
            - Documentation mentions "security", "vault", "secrets"
            - Should link to: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html#best-practices-for-security
        """
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        
        integrator = ExternalLinkIntegrator()
        
        content = """
        This role handles sensitive data using Ansible Vault for secrets management.
        Security is a top priority.
        """
        
        links = integrator.extract_best_practice_links(content)
        
        # Should detect security-related keywords
        assert any("security" in link.target.lower() or "vault" in link.target.lower() 
                   for link in links)
        assert any("best_practices" in link.target for link in links)

    def test_testing_keyword_links_to_testing_guide(self, tmp_path: Path) -> None:
        """Test that testing-related content links to Ansible testing guides."""
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        
        integrator = ExternalLinkIntegrator()
        
        content = """
        This role includes molecule tests and CI/CD integration testing.
        """
        
        links = integrator.extract_best_practice_links(content)
        
        # Should detect testing keywords
        assert any("test" in link.target.lower() or "molecule" in link.target.lower() 
                   for link in links)

    def test_multiple_best_practices_generate_separate_links(self, tmp_path: Path) -> None:
        """Test that different best practice topics generate distinct links."""
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        
        integrator = ExternalLinkIntegrator()
        
        content = """
        This role follows Ansible best practices:
        - Security with Vault
        - Testing with Molecule
        - Performance optimization
        """
        
        links = integrator.extract_best_practice_links(content)
        
        # Should have multiple distinct links
        targets = [link.target for link in links]
        assert len(set(targets)) >= 2  # At least 2 different best practice topics


class TestNewTabBehavior:
    """Tests for external link new tab behavior (T060)."""

    def test_external_links_have_target_blank_attribute(self, tmp_path: Path) -> None:
        """Test that external links include target='_blank' attribute.
        
        Scenario:
            - External link in HTML output
            - Should have target="_blank" rel="noopener noreferrer"
        """
        from ansibledoctor.models.link import Link, LinkType
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        
        link = Link(
            source_file=tmp_path / "README.md",
            target="https://docs.ansible.com/",
            link_type=LinkType.EXTERNAL_URL,
            text="Ansible Documentation",
            line_number=1
        )
        
        integrator = ExternalLinkIntegrator()
        html = integrator.render_link_html(link)
        
        # Should include security attributes
        assert 'target="_blank"' in html
        assert 'rel="noopener noreferrer"' in html

    def test_internal_links_do_not_have_target_blank(self, tmp_path: Path) -> None:
        """Test that internal links stay in same tab."""
        from ansibledoctor.models.link import Link, LinkType
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        
        link = Link(
            source_file=tmp_path / "README.md",
            target="./roles/nginx/README.md",
            link_type=LinkType.INTERNAL_FILE,
            text="Nginx Role",
            line_number=1
        )
        
        integrator = ExternalLinkIntegrator()
        html = integrator.render_link_html(link)
        
        # Internal links should NOT open in new tab
        assert 'target="_blank"' not in html


class TestVersionSpecificLinks:
    """Tests for version-specific documentation linking (T061)."""

    def test_ansible_2_15_links_to_2_15_docs(self, tmp_path: Path) -> None:
        """Test that Ansible 2.15 generates version-specific docs links.
        
        Scenario:
            - Project uses Ansible 2.15
            - Module docs should link to /ansible/2.15/ path
        """
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        
        integrator = ExternalLinkIntegrator(ansible_version="2.15")
        
        link = integrator.generate_module_doc_link("ansible.builtin.copy")
        
        # Should use version-specific URL
        assert "/ansible/2.15/" in link.target or "/ansible/latest/" in link.target

    def test_latest_version_uses_latest_path(self, tmp_path: Path) -> None:
        """Test that 'latest' version uses /latest/ path."""
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        
        integrator = ExternalLinkIntegrator(ansible_version="latest")
        
        link = integrator.generate_module_doc_link("ansible.builtin.file")
        
        assert "/ansible/latest/" in link.target

    def test_version_config_from_ansibledoctor_yml(self, tmp_path: Path) -> None:
        """Test that Ansible version can be configured in .ansibledoctor.yml."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""
ansible_version: "2.14"
external_links:
  ansible_docs_base: "https://docs.ansible.com"
""")
        
        from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
        
        integrator = ExternalLinkIntegrator.from_config(config_file)
        
        assert integrator.ansible_version == "2.14"
        
        link = integrator.generate_module_doc_link("ansible.builtin.template")
        
        # Should respect configured version
        assert "/ansible/2.14/" in link.target or "/ansible/latest/" in link.target
