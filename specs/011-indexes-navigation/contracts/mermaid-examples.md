# Mermaid Diagram Examples

**Date**: 2025-12-03  
**Feature**: Spec 011 - Indexes & Navigation

This document provides example Mermaid diagrams for different project structures and use cases.

---

## Example 1: Simple Flowchart (Top-Down)

**Use Case**: Small project with 2 collections and 5 roles

```mermaid
graph TD
    Project["My Ansible Project"]
    Infra["my_namespace.infrastructure"]
    Monitor["my_namespace.monitoring"]
    
    Web["webserver"]
    DB["database"]
    LB["load_balancer"]
    Prom["prometheus"]
    Graf["grafana"]
    
    Project --> Infra
    Project --> Monitor
    
    Infra --> Web
    Infra --> DB
    Infra --> LB
    
    Monitor --> Prom
    Monitor --> Graf
    
    Web -.depends.-> DB
    LB -.depends.-> Web
    
    click Web "./roles/webserver/README.md"
    click DB "./roles/database/README.md"
    click LB "./roles/load_balancer/README.md"
    click Prom "./roles/prometheus/README.md"
    click Graf "./roles/grafana/README.md"
```

**Features**:

- Solid lines: parent-child relationships
- Dashed lines: dependencies
- Clickable nodes linking to documentation

---

## Example 2: Flowchart with Subgraphs

**Use Case**: Medium project with logical grouping

```mermaid
graph TD
    subgraph "Infrastructure Collection"
        Web[webserver]
        DB[database]
        Cache[redis]
    end
    
    subgraph "Monitoring Collection"
        Prom[prometheus]
        Graf[grafana]
        Alert[alertmanager]
    end
    
    subgraph "Security Collection"
        FW[firewall]
        SSL[ssl_certs]
        Audit[audit_logging]
    end
    
    Web -.depends.-> DB
    Web -.depends.-> Cache
    Prom -.monitors.-> Web
    Prom -.monitors.-> DB
    Alert -.notifies.-> Prom
    
    style Web fill:#9cf
    style DB fill:#9cf
    style Prom fill:#fc9
```

**Features**:

- Subgraphs for collections
- Custom styling by importance
- Multiple relationship types (depends, monitors, notifies)

---

## Example 3: Left-Right Layout

**Use Case**: Wide hierarchy, better use of horizontal space

```mermaid
graph LR
    Project --> Infra
    Project --> Monitor
    Project --> Security
    
    Infra --> Web
    Infra --> DB
    Infra --> Cache
    
    Monitor --> Prom
    Monitor --> Graf
    
    Security --> FW
    Security --> SSL
    
    Web -.-> DB
    Web -.-> Cache
```

**Features**:

- Left-to-right layout (LR)
- More compact for wide structures

---

## Example 4: Mindmap Style

**Use Case**: Large project (50+ components), radial layout

```mermaid
mindmap
  root((Project))
    Infrastructure
      Web Servers
        webserver
        nginx_config
      Databases
        postgres
        mysql
        mongodb
      Caching
        redis
        memcached
    Monitoring
      Metrics
        prometheus
        node_exporter
      Visualization
        grafana
        kibana
      Alerting
        alertmanager
        pagerduty
    Security
      Firewalls
        iptables
        ufw
      SSL/TLS
        letsencrypt
        ssl_certs
      Authentication
        ldap
        oauth2
```

**Features**:

- Radial layout handles density better
- Hierarchical grouping by category
- No explicit links (implied by structure)

---

## Example 5: Dependency Graph

**Use Case**: Show complex dependencies between roles

```mermaid
graph TD
    App[application]
    Web[webserver]
    DB[database]
    Cache[cache]
    Common[common]
    SSL[ssl_certs]
    FW[firewall]
    
    App --> Web
    App --> Cache
    Web --> SSL
    Web --> Common
    DB --> Common
    Cache --> Common
    SSL --> FW
    
    style App fill:#f96
    style Common fill:#9f9
    
    click App "./roles/application/README.md"
    click Web "./roles/webserver/README.md"
    click DB "./roles/database/README.md"
    click Cache "./roles/cache/README.md"
    click Common "./roles/common/README.md"
    click SSL "./roles/ssl_certs/README.md"
    click FW "./roles/firewall/README.md"
```

**Features**:

- Focus on dependencies, not hierarchy
- Color-coding: red=application, green=common/shared
- Shows which roles are foundational (common)

---

## Example 6: Collection with Plugins

**Use Case**: Show both roles and plugins in a collection

```mermaid
graph TD
    Coll[my_namespace.infrastructure]
    
    subgraph "Roles"
        Web[webserver]
        DB[database]
    end
    
    subgraph "Plugins"
        Mod1[deploy_app module]
        Mod2[manage_service module]
        Filt1[metric_format filter]
    end
    
    Coll --> Web
    Coll --> DB
    Coll --> Mod1
    Coll --> Mod2
    Coll --> Filt1
    
    Web -.uses.-> Mod1
    DB -.uses.-> Mod2
    
    style Mod1 fill:#fcf
    style Mod2 fill:#fcf
    style Filt1 fill:#cff
```

**Features**:

- Different node colors for plugins vs roles
- Shows plugin usage by roles
- Clear separation of concerns

---

## Example 7: Project with Playbooks

**Use Case**: Show playbooks and which roles they use

```mermaid
graph TD
    Project[Project]
    
    subgraph "Playbooks"
        Site[site.yml]
        Deploy[deploy.yml]
        Rollback[rollback.yml]
    end
    
    subgraph "Roles"
        Web[webserver]
        DB[database]
        Monitor[monitoring]
    end
    
    Project --> Site
    Project --> Deploy
    Project --> Rollback
    
    Site -.uses.-> Web
    Site -.uses.-> DB
    Site -.uses.-> Monitor
    
    Deploy -.uses.-> Web
    Deploy -.uses.-> DB
    
    Rollback -.uses.-> Web
    
    style Site fill:#ffc
    style Deploy fill:#ffc
    style Rollback fill:#ffc
```

**Features**:

- Playbooks shown as distinct type
- "uses" relationships show role usage
- Yellow for playbooks, default for roles

---

## Example 8: Circular Dependency Warning

**Use Case**: Detect and visualize circular dependencies

```mermaid
graph TD
    Web[webserver]
    App[application]
    DB[database]
    
    Web --> App
    App --> DB
    DB -.circular!.-> Web
    
    style DB stroke:#f00,stroke-width:3px
    style Web stroke:#f00,stroke-width:3px
    
    click Web "./roles/webserver/README.md"
    click App "./roles/application/README.md"
    click DB "./roles/database/README.md"
```

**Features**:

- Red border for roles in cycle
- Dashed line with "circular!" label
- Helps identify problematic dependencies

---

## Example 9: Large Project with Clustering

**Use Case**: 100+ components, need to reduce clutter

```mermaid
graph TD
    Project[Project]
    
    Infra[Infrastructure<br/>25 roles]
    Monitor[Monitoring<br/>12 roles]
    Security[Security<br/>18 roles]
    Network[Networking<br/>15 roles]
    Storage[Storage<br/>8 roles]
    
    Project --> Infra
    Project --> Monitor
    Project --> Security
    Project --> Network
    Project --> Storage
    
    click Infra "./collections/infrastructure/README.md"
    click Monitor "./collections/monitoring/README.md"
    click Security "./collections/security/README.md"
    click Network "./collections/networking/README.md"
    click Storage "./collections/storage/README.md"
```

**Features**:

- Collapsed collections showing count
- Links to collection README (expanded view)
- Keeps diagram readable at project level

---

## Example 10: Status Indicators

**Use Case**: Show role maturity/status in diagram

```mermaid
graph TD
    Web["webserver<br/>(stable)"]
    DB["database<br/>(stable)"]
    New["new_feature<br/>(beta)"]
    Dep["old_role<br/>(deprecated)"]
    
    Web --> DB
    Web --> New
    
    style Web fill:#9f9
    style DB fill:#9f9
    style New fill:#ff9
    style Dep fill:#f99,stroke-dasharray: 5 5
```

**Features**:

- Green: stable/production
- Yellow: beta/testing
- Red + dashed: deprecated
- Status in node label

---

## Template Integration

### In Jinja2 Template

```jinja2
## Project Structure

{{ index('collections', format='diagram', diagram_type='flowchart') }}
```

### Generated Output

```markdown
## Project Structure

\`\`\`mermaid
graph TD
    Project["My Ansible Project"]
    Coll1["infrastructure"]
    Coll2["monitoring"]
    
    Project --> Coll1
    Project --> Coll2
    
    click Coll1 "./infrastructure/README.md"
    click Coll2 "./monitoring/README.md"
\`\`\`
```

---

## Mermaid Syntax Reference

### Basic Graph Types

- `graph TD`: Top-down flowchart
- `graph LR`: Left-right flowchart
- `graph BT`: Bottom-top flowchart
- `graph RL`: Right-left flowchart
- `mindmap`: Radial mindmap

### Node Shapes

- `[Text]`: Rectangle
- `(Text)`: Rounded rectangle
- `([Text])`: Stadium (pill shape)
- `[[Text]]`: Subroutine
- `[(Text)]`: Cylindrical (database)
- `((Text))`: Circle
- `{Text}`: Diamond (decision)

### Line Types

- `-->`: Solid arrow
- `-.->`: Dashed arrow
- `==>`: Thick arrow
- `--Text-->`: Arrow with label
- `---`: No arrow

### Styling

```mermaid
graph TD
    A[Node A]
    B[Node B]
    
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style B fill:#bbf,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
```

### Clickable Links

```mermaid
graph TD
    A[Role A]
    click A "./roles/role_a/README.md"
```

---

## Performance Considerations

| Node Count | Recommended Diagram Type | Rationale |
| ------------ | ------------------------- | ----------- |
| 1-20 | Flowchart (TD/LR) | Simple, easy to read |
| 21-50 | Flowchart with subgraphs | Organized by collection |
| 51-100 | Mindmap | Radial layout handles density |
| 100+ | Clustered flowchart | Show collections with counts, link to details |

**Browser Rendering**:

- Mermaid renders on client-side (JavaScript)
- Large diagrams (100+ nodes) may be slow
- Consider splitting into multiple diagrams per collection
