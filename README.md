# ask-vfb

A Claude Code workspace for querying [Virtual Fly Brain (VFB)](https://virtualflybrain.org) and Drosophila neuroscience resources using natural language.

Ask questions about neurons, neuroanatomy, synaptic connectivity, gene expression, transcriptomics and the literature — and get back structured answers, tables, and image reports, all linked directly to VFB.

---

## What can ask-vfb do?

### Look up neuron details, image, connecitivy, literature, split drivers, gene expression (from tanscriptomics)
> *"Tell me about MBON-γ3?"*
  * Retrieves term info (description, classification, relationships) from the VFB knowledge graph and hyperlinks all results to the VFB browser.
> *"Show me thumbnails for 5 MBON-γ3 neurons"*
  * Fetches neuron morphology thumbnails from VFB and produces markdown reports with embedded images and 3D browser links.
> *"Find split combinations that target MBON-γ3"
> *"Find all types of GABAergic neurons upstream of MBON-γ3"*
> *"Find papers describing these neurons and extract details of their structure and function."* 






### Synaptic connectivity (`/vfb-connectivity`)
> *"What are the downstream targets of Kenyon cells with weight ≥ 10?"*
> *"Show class-level connectivity from DANs to MBONs"*
> *"What inputs do the mushroom body output neurons receive?"*

Queries the VFB connectomics graph via `vfb-connect` for upstream/downstream partners, synapse weights, and class-level aggregations. Supports filtering by weight threshold and database source.

#


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
- **Node.js / npm** — required for the Playwright MCP (web site interaction) and artl-mcp (literature retrieval). Install from [nodejs.org](https://nodejs.org/). The setup script will warn if Node.js is not found.
- The following MCP servers configured in your Claude Code settings:
  - `virtual-fly-brain`
  - `artl-mcp`
  - `ols4`
  - `playwright` (optional — for web browsing)
  - `Asta_semanticscholar` (optional — for Semantic Scholar literature search; requires API key, see below)

### 1. Clone the repo

```bash
git clone https://github.com/your-org/ask-vfb.git
cd ask-vfb
```

### 2. Create the Python virtual environment

```bash
bash setup_venv.sh
```

This auto-detects your highest available Python (3.9–3.13), creates `.venv/`, and installs:
- `vfb-connect` — VFB Python client for connectomics queries
- `psycopg` — PostgreSQL adapter

### 3. Set up environment variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` to add your keys. Currently the only key required is for the **ASTA Semantic Scholar MCP**:

```
ASTA_API_KEY=your_api_key_here
```

> **What is ASTA?** ASTA is the Semantic Scholar API Tools service from the Allen Institute for AI. It provides structured search over the academic literature — paper search by relevance/title, citation graphs, author lookup, and snippet-level semantic search. Details and API key applications: [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api#api-key)

The `.env` file is listed in `.gitignore` and will **not** be committed to the repository. The setup script (`setup_venv.sh`) automatically loads variables from `.env` when it runs.

### 4. Configure MCP servers

Ensure the following MCP servers are registered in your Claude Code MCP settings (`~/.claude/mcp_settings.json` or equivalent):

| Server name | Purpose | Requires |
|---|---|---|
| `virtual-fly-brain` | Neuron/anatomy search, term info, connectivity | — (remote HTTP) |
| `artl-mcp` | Europe PMC literature retrieval | Node.js/npm |
| `ols4` | OBO ontology search and traversal | — (remote HTTP) |
| `playwright` | Web site interaction and browsing | Node.js/npm |
| `Asta_semanticscholar` | Semantic Scholar literature search | `ASTA_API_KEY` in `.env` |

### 5. Open in Claude Code

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
| [Semantic Scholar / ASTA](https://www.semanticscholar.org/product/api) | Literature search, citations, snippet search |
| [OLS4](https://www.ebi.ac.uk/ols4) | OBO ontologies (FBbt, GO, etc.) |
