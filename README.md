# ask-vfb

A Claude Code workspace for querying [Virtual Fly Brain (VFB)](https://virtualflybrain.org) and Drosophila neuroscience resources using natural language.

Ask questions about neurons, neuroanatomy, synaptic connectivity, gene expression, transcriptomics and the literature — and get back structured answers, tables, and image reports, all linked directly to VFB.

---

## What can ask-vfb do?

### Neuron and anatomy lookup
> *"What is MBON-γ3?"*
> *"Show me term info for the mushroom body"*
> *"Find all GABAergic neurons in VFB with images"*

Retrieves term info (description, classification, relationships) from the VFB knowledge graph and hyperlinks all results to the VFB browser.

### Image reports
> *"Show me thumbnails for 5 MBON neurons"*
> *"Make a markdown report with images of Kenyon cells"*

Fetches neuron morphology thumbnails from VFB and produces markdown reports with embedded images and 3D browser links.

### Synaptic connectivity (`/vfb-connectivity`)
> *"What are the downstream targets of Kenyon cells with weight ≥ 10?"*
> *"Show class-level connectivity from DANs to MBONs"*
> *"What inputs does the mushroom body output neuron receive?"*

Queries the VFB connectomics graph via `vfb-connect` for upstream/downstream partners, synapse weights, and class-level aggregations. Supports filtering by weight threshold and database source.

### Ontology queries
> *"What is the FBbt term for the mushroom body calyx?"*
> *"Show me subclasses of sensory neuron"*

Searches and traverses the Drosophila anatomy ontology (FBbt) and other OBO ontologies via the OLS4 MCP.

### Literature search
> *"Find recent papers on MBON function in memory"*
> *"Get the full text of PMC3737249"*

Searches Europe PMC and retrieves full-text content or PDF-converted markdown for use in analysis.

---

## Setup

### Prerequisites

- [Claude Code](https://github.com/anthropics/claude-code) (CLI)
- Python 3.9–3.13
- The following MCP servers configured in your Claude Code settings:
  - `virtual-fly-brain`
  - `artl-mcp`
  - `ols4`

### 1. Clone the repo

```bash
git clone https://github.com/your-org/ask-vfb.git
cd ask-vfb
```

### 2. Easy install for Claude Code (recommended)

This repo is already configured as a Claude Code “skills” workspace. To install the skills globally so they are available from any Claude Code workspace, run:

```bash
./install_claude_skills.sh
```

> If the script is not executable, run: `chmod +x install_claude_skills.sh`

### 3. Create the Python virtual environment

```bash
bash setup_venv.sh
```

This auto-detects your highest available Python (3.9–3.13), creates `.venv/`, and installs:
- `vfb-connect` — VFB Python client for connectomics queries
- `psycopg` — PostgreSQL adapter

### 3. Configure MCP servers

Ensure the following MCP servers are registered in your Claude Code MCP settings (`~/.claude/mcp_settings.json` or equivalent):

| Server name | Purpose |
|---|---|
| `virtual-fly-brain` | Neuron/anatomy search, term info, connectivity |
| `artl-mcp` | Europe PMC literature retrieval |
| `ols4` | OBO ontology search and traversal |

### 4. Open in Claude Code

```bash
claude
```

The `CLAUDE.md` in this directory configures the assistant's persona and output conventions automatically.

---

## Skills

Skills are slash commands that implement multi-step workflows.

### `/vfb-connectivity`

Query synaptic connectivity between neuron classes.

**Examples:**
```
/vfb-connectivity what does the Kenyon cell connect to downstream?
/vfb-connectivity inputs to mushroom body output neuron, weight >= 10
/vfb-connectivity class-level summary of DAN → MBON connectivity
```

Supports:
- Upstream / downstream / bidirectional queries
- Minimum synapse weight threshold (default: 5)
- Per-neuron or class-aggregated output
- Database filtering (e.g. exclude Hemibrain)

---

## Output conventions

- All neurons and anatomy terms are hyperlinked to the VFB browser
- Image reports embed morphology thumbnails with links to the 3D viewer
- Connectivity results include VFB IDs for every neuron listed

---

## Data sources

Results are drawn from:

| Source | Content |
|---|---|
| [Virtual Fly Brain](https://virtualflybrain.org) | Neuron morphology, anatomy ontology, connectomics |
| [FAFB](https://fafb.catmaid.virtualflybrain.org) | Full adult female brain EM (Otto et al. 2020) |
| [Europe PMC](https://europepmc.org) | Literature and full-text articles |
| [OLS4](https://www.ebi.ac.uk/ols4) | OBO ontologies (FBbt, GO, etc.) |
