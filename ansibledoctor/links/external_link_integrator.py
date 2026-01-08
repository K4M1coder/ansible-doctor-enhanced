"""
External link integration for Ansible documentation and resources.

This module provides automatic linking to official Ansible documentation,
Galaxy pages, and best practices guides.

Spec: 013-links-cross-references
Phase: 6 (User Story 4 - Access External Resources)
Tasks: T062-T068
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.link import Link, LinkType


# Best practices keyword mapping
BEST_PRACTICES_KEYWORDS = {
    "security": "https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html#best-practices-for-security",
    "vault": "https://docs.ansible.com/ansible/latest/user_guide/playbooks_vault.html",
    "secrets": "https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html#best-practices-for-security",
    "testing": "https://docs.ansible.com/ansible/latest/dev_guide/testing.html",
    "molecule": "https://molecule.readthedocs.io/en/latest/",
    "ci/cd": "https://docs.ansible.com/ansible/latest/dev_guide/testing_integration.html",
    "performance": "https://docs.ansible.com/ansible/latest/user_guide/playbooks_strategies.html",
    "optimization": "https://docs.ansible.com/ansible/latest/user_guide/playbooks_strategies.html",
}


class ExternalLinkIntegrator:
    """
    Integrates external resource links into Ansible documentation.
    
    Features:
    - Module documentation linking (docs.ansible.com)
    - Galaxy collection/role linking (galaxy.ansible.com)
    - Best practices guide linking
    - Version-specific URL generation
    - HTML attribute management (target="_blank")
    
    Example:
        >>> integrator = ExternalLinkIntegrator(ansible_version="2.15")
        >>> link = integrator.generate_module_doc_link("ansible.builtin.copy")
        >>> print(link.target)
        https://docs.ansible.com/ansible/2.15/collections/ansible/builtin/copy_module.html
    """

    def __init__(
        self,
        ansible_version: str = "latest",
        ansible_docs_base: str = "https://docs.ansible.com",
        galaxy_base: str = "https://galaxy.ansible.com",
    ):
        """
        Initialize external link integrator.
        
        Args:
            ansible_version: Ansible version for docs links (e.g., "2.15", "latest")
            ansible_docs_base: Base URL for Ansible documentation
            galaxy_base: Base URL for Ansible Galaxy
        """
        self.ansible_version = ansible_version
        self.ansible_docs_base = ansible_docs_base
        self.galaxy_base = galaxy_base

    @classmethod
    def from_config(cls, config_path: Path) -> "ExternalLinkIntegrator":
        """
        Create integrator from .ansibledoctor.yml configuration.
        
        Args:
            config_path: Path to .ansibledoctor.yml file
            
        Returns:
            Configured ExternalLinkIntegrator instance
        """
        if not config_path.exists():
            return cls()
            
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            
        ansible_version = config.get("ansible_version", "latest")
        external_links = config.get("external_links", {})
        
        return cls(
            ansible_version=ansible_version,
            ansible_docs_base=external_links.get("ansible_docs_base", "https://docs.ansible.com"),
            galaxy_base=external_links.get("galaxy_base", "https://galaxy.ansible.com"),
        )

    def generate_module_doc_link(self, module_fqcn: str, source_file: Optional[Path] = None) -> Link:
        """
        Generate documentation link for an Ansible module.
        
        Args:
            module_fqcn: Fully qualified module name (e.g., "ansible.builtin.copy")
            source_file: Source file where module is used (optional)
            
        Returns:
            Link to module documentation
            
        Example:
            >>> integrator = ExternalLinkIntegrator(ansible_version="2.15")
            >>> link = integrator.generate_module_doc_link("ansible.builtin.copy")
            >>> print(link.target)
            https://docs.ansible.com/ansible/2.15/collections/ansible/builtin/copy_module.html
        """
        # Parse FQCN: namespace.collection.module_name
        parts = module_fqcn.split(".")
        
        if len(parts) < 3:
            # Invalid FQCN - use legacy format
            module_name = module_fqcn
            url = f"{self.ansible_docs_base}/ansible/{self.ansible_version}/modules/{module_name}_module.html"
        else:
            namespace = parts[0]
            collection = parts[1]
            module_name = ".".join(parts[2:])
            
            # Modern collection-based URL
            url = f"{self.ansible_docs_base}/ansible/{self.ansible_version}/collections/{namespace}/{collection}/{module_name}_module.html"
        
        # Use provided source_file or fallback to absolute dummy path
        if source_file is None:
            source_file = Path.cwd() / "external_links.md"
        
        return Link(
            source_file=source_file.resolve(),
            target=url,
            link_type=LinkType.EXTERNAL_URL,
            text=f"{module_fqcn} module documentation",
            line_number=1,
        )

    def extract_module_links(self, role_dir: Path) -> List[Link]:
        """
        Extract module documentation links from role tasks.
        
        Parses YAML task files to find module usage and generates
        documentation links for each unique module.
        
        Args:
            role_dir: Path to role directory
            
        Returns:
            List of module documentation links
        """
        links: List[Link] = []
        modules_seen: set[str] = set()
        
        tasks_dir = role_dir / "tasks"
        if not tasks_dir.exists():
            return links
            
        for task_file in tasks_dir.glob("**/*.yml"):
            try:
                with open(task_file, encoding="utf-8") as f:
                    tasks = yaml.safe_load(f) or []
                    
                if not isinstance(tasks, list):
                    continue
                    
                for task in tasks:
                    if not isinstance(task, dict):
                        continue
                        
                    # Find module name (any key that's not a task attribute)
                    task_attrs = {"name", "when", "tags", "vars", "notify", "register", "changed_when", "failed_when"}
                    
                    for key in task.keys():
                        if key not in task_attrs and "." in key:
                            # This is likely a module FQCN
                            if key not in modules_seen:
                                modules_seen.add(key)
                                link = self.generate_module_doc_link(key, source_file=task_file)
                                links.append(link)
                                
            except (yaml.YAMLError, OSError):
                continue
                
        return links

    def generate_galaxy_link(self, collection: AnsibleCollection) -> Link:
        """
        Generate Ansible Galaxy link for a collection.
        
        Args:
            collection: AnsibleCollection instance
            
        Returns:
            Link to Galaxy collection page
            
        Example:
            >>> from ansibledoctor.models.galaxy import GalaxyMetadata
            >>> from ansibledoctor.models.collection import AnsibleCollection
            >>> metadata = GalaxyMetadata(namespace="community", name="general", version="1.0.0", authors=["Test"], dependencies={})
            >>> collection = AnsibleCollection(metadata=metadata)
            >>> integrator = ExternalLinkIntegrator()
            >>> link = integrator.generate_galaxy_link(collection)
            >>> print(link.target)
            https://galaxy.ansible.com/ui/repo/published/community/general/
        """
        namespace = collection.metadata.namespace
        name = collection.metadata.name
        url = f"{self.galaxy_base}/ui/repo/published/{namespace}/{name}/"
        
        # Use collection path if available, otherwise use current directory
        if hasattr(collection, 'path') and collection.path:
            source_file = Path(collection.path).resolve() / "galaxy.yml"
        else:
            source_file = Path.cwd() / "galaxy.yml"
        
        return Link(
            source_file=source_file,
            target=url,
            link_type=LinkType.EXTERNAL_URL,
            text=f"Ansible Galaxy: {namespace}.{name}",
            line_number=1,
        )

    def generate_role_galaxy_link(self, role_dir: Path) -> Link:
        """
        Generate Ansible Galaxy link for a role.
        
        Reads galaxy_info from meta/main.yml to construct Galaxy URL.
        
        Args:
            role_dir: Path to role directory
            
        Returns:
            Link to Galaxy role page
        """
        meta_file = role_dir / "meta" / "main.yml"
        
        if not meta_file.exists():
            # Fallback to generic Galaxy search
            role_name = role_dir.name
            url = f"{self.galaxy_base}/search?keywords={role_name}"
        else:
            try:
                with open(meta_file, encoding="utf-8") as f:
                    meta = yaml.safe_load(f) or {}
                    
                galaxy_info = meta.get("galaxy_info", {})
                namespace = galaxy_info.get("namespace", galaxy_info.get("author", ""))
                role_name = galaxy_info.get("role_name", role_dir.name)
                
                if namespace:
                    url = f"{self.galaxy_base}/{namespace}/{role_name}"
                else:
                    url = f"{self.galaxy_base}/search?keywords={role_name}"
                    
            except (yaml.YAMLError, OSError):
                role_name = role_dir.name
                url = f"{self.galaxy_base}/search?keywords={role_name}"
        
        source_file = meta_file if meta_file.exists() else role_dir / "README.md"
        
        return Link(
            source_file=source_file.resolve(),
            target=url,
            link_type=LinkType.EXTERNAL_URL,
            text=f"Ansible Galaxy: {role_dir.name}",
            line_number=1,
        )

    def extract_best_practice_links(self, content: str, source_file: Optional[Path] = None) -> List[Link]:
        """
        Extract best practices guide links from documentation content.
        
        Searches for keywords related to Ansible best practices and
        generates links to relevant official guides.
        
        Args:
            content: Documentation text content
            source_file: Source file containing the content (optional)
            
        Returns:
            List of best practices links
            
        Example:
            >>> integrator = ExternalLinkIntegrator()
            >>> content = "This role uses Ansible Vault for security."
            >>> links = integrator.extract_best_practice_links(content)
            >>> assert any("vault" in link.target for link in links)
        """
        links: List[Link] = []
        content_lower = content.lower()
        
        if source_file is None:
            source_file = Path.cwd() / "best_practices.md"
        
        for keyword, url in BEST_PRACTICES_KEYWORDS.items():
            if keyword in content_lower:
                link = Link(
                    source_file=source_file.resolve(),
                    target=url,
                    link_type=LinkType.EXTERNAL_URL,
                    text=f"Ansible Best Practices: {keyword.title()}",
                    line_number=1,
                )
                links.append(link)
                
        return links

    def render_link_html(self, link: Link) -> str:
        """
        Render link as HTML with appropriate attributes.
        
        External links get target="_blank" and security attributes.
        Internal links stay in the same tab.
        
        Args:
            link: Link to render
            
        Returns:
            HTML anchor tag string
            
        Example:
            >>> integrator = ExternalLinkIntegrator()
            >>> link = Link(
            ...     source_file=Path(""),
            ...     target="https://docs.ansible.com/",
            ...     link_type=LinkType.EXTERNAL_URL,
            ...     text="Docs",
            ... )
            >>> html = integrator.render_link_html(link)
            >>> assert 'target="_blank"' in html
            >>> assert 'rel="noopener noreferrer"' in html
        """
        if link.link_type == LinkType.EXTERNAL_URL:
            # External links open in new tab with security attributes
            return f'<a href="{link.target}" target="_blank" rel="noopener noreferrer">{link.text}</a>'
        else:
            # Internal links stay in same tab
            return f'<a href="{link.target}">{link.text}</a>'

    def integrate_links(self, content: str, context: Dict[str, Any]) -> str:
        """
        Integrate external resource links into documentation content.
        
        This is the main entry point for automatic link integration.
        Scans content for linkable items and injects external resource links.
        
        Args:
            content: Documentation content (Markdown, HTML, RST)
            context: Generation context (role, collection, config, etc.)
            
        Returns:
            Content with integrated external links
        """
        # Extract role/collection from context
        role_dir = context.get("role_dir")
        collection = context.get("collection")
        
        # Collect all external links
        all_links: List[Link] = []
        
        if role_dir:
            all_links.extend(self.extract_module_links(role_dir))
            
        if collection:
            all_links.append(self.generate_galaxy_link(collection))
            
        all_links.extend(self.extract_best_practice_links(content))
        
        # Append external resources section if links found
        if all_links:
            content += "\n\n## External Resources\n\n"
            for link in all_links:
                content += f"- [{link.text}]({link.target})\n"
                
        return content
