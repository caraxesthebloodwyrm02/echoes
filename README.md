# Glimpse: Integrated Cognition Framework

This repository contains the source code and documentation for the Glimpse project, a research initiative focused on building an Integrated Cognition Framework. Our goal is to bridge the gap between empirical (fact-based) and experiential (intuition-based) knowledge through a novel Retrieval-Augmented Generation (RAG) system.

For a deep dive into the project's purpose and architecture, please see [FOUNDATIONAL_GROUND.md](FOUNDATIONAL_GROUND.md).

## Key Features

This project includes several advanced, self-aware systems designed to improve robustness and developer interaction.

### 1. RAG Orbit: The Core Engine

The heart of the Glimpse project is **RAG Orbit**, a custom-built RAG pipeline designed for reproducibility and auditability. It consists of four main components:

-   **Chunking (`src/rag_orbit/chunking.py`):** Intelligently segments documents.
-   **Embeddings (`src/rag_orbit/embeddings.py`):** Translates text into semantic vectors.
-   **Retrieval (`src/rag_orbit/retrieval.py`):** Provides efficient, FAISS-based similarity search.
-   **Provenance (`src/rag_orbit/provenance.py`):** Creates a complete, verifiable audit trail of all operations.


### 2. End-to-End Validation

The entire RAG Orbit pipeline is validated through a comprehensive end-to-end test suite, which you can find at `tests/test_e2e_flow.py`. This suite confirms that the system can:

1.  Process both `empirical` and `experiential` data.
2.  Retrieve the correct information for a given query.
3.  Maintain a verifiable provenance trail.

A practical demonstration can be run via the `demo_glimpse_initialization.py` script.

---

## 📋 Project Status (October 2025)

-   ✅ **Foundation Established:** The project's purpose, architecture, and workflows are clearly defined in `FOUNDATIONAL_GROUND.md`.
-   ✅ **Terminology Refactored:** The project has been consistently renamed to "Glimpse."
-   ✅ **Core Implementation Complete:** The `RAG Orbit` system is fully implemented.
-   ✅ **End-to-End Testing in Place:** A full test suite validates the entire pipeline.

For a detailed project plan, see the [Project Charter](GLIMPSE_PROJECT_CHARTER.md).

---

## 🚀 Getting Started

1.  **Set up the environment:**
    ```bash
    # Activate virtual environment
    .\.venv\Scripts\Activate.ps1
    ```

2.  **Run the demonstration:**
    ```bash
    python demo_glimpse_initialization.py
    ```

3.  **Run the tests:**
    ```bash
    pytest
    ```

License: MIT
