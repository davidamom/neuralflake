# NeuralFlake

A RAG-powered (Retrieval-Augmented Generation) AI agent specialized in Data Engineering, capable of querying Snowflake metadata, Git repositories, dbt YAML files, and other relevant resources for data engineers.

![alt text](<assets/NeuralFlake - Components of a NeuralFlake AI Agent.svg>)

## Overview
This project implements an intelligent agent that combines:
- RAG capabilities for querying and retrieving technical information
- Autonomous operation to perform analyses and suggest actions
- Specialized knowledge in data engineering tools and concepts

## Tech Stack

### Agent Core
- **Python 3.9+**: Base language
- **LangChain/LlamaIndex**: Agent orchestration framework
- **FastAPI**: For RESTful API exposure
- **Pydantic**: For data validation and schemas

### Language Model
- **OpenAI API** (GPT-4) or **Anthropic Claude**
- Option for open-source models like **Llama 3** or **Mistral AI**

### RAG Component
- **Vector Database**: Chroma, Pinecone, or FAISS
- **Embeddings**: OpenAI Embeddings or Sentence-Transformers
- **Document Processing**: Unstructured.io, PyPDF, Markdown

### Connectors
- **Snowflake**: Snowflake Connector for Python
- **Git**: GitPython or PyGithub
- **dbt**: dbt-core package and PyYAML

### Infrastructure
- **Docker**: For containerization
- **Redis**: For caching and state management (optional)
- **Poetry**: Dependency management
- **Uvicorn/Gunicorn**: ASGI servers

### UI/Interaction
- **Streamlit** or **Gradio**: For web interface (optional)
- **Rich**: For enhanced CLI interface

### Security
- **Python-dotenv**: Environment variable management
- **Python-jose** or **PyJWT**: For JWT authentication

![alt text](<assets/NeuralFlake - Comprehensive Tech Stack for Software Development.svg>)

## Development Roadmap

### Phase 1: Foundation (MVP)
- [x] Project structure definition
- [x] Core agent implementation with basic capabilities
- [x] Simple RAG system with a single data source (e.g., local documents)
- [x] LLM integration (OpenAI GPT-4)
- [x] Basic CLI for agent interaction
- [x] Unit test configuration
- [x] Initial documentation

### Phase 2: Main Connectors
- [ ] Snowflake connector implementation
  - [ ] Metadata queries
  - [ ] Simple query execution
- [ ] Git connector implementation
  - [ ] Repository analysis
  - [ ] File queries
- [ ] dbt connector implementation
  - [ ] YAML parser
  - [ ] Dependency analysis
- [ ] Integration tests for connectors

### Phase 3: RAG Enhancement
- [ ] Advanced chunking implementation
- [ ] Optimized embedding strategies
- [ ] Support for multiple vector databases
- [ ] Query caching system
- [ ] Technical documentation indexer

### Phase 4: Agent Capabilities
- [ ] Memory and history system
- [ ] Action planning (planner)
- [ ] Specialized tools (SQL generator, code reviewer)
- [ ] Feedback and self-learning system
- [ ] Security and validation mechanisms

### Phase 5: Interface and Integration
- [ ] Complete RESTful API
- [ ] Web interface with Streamlit
- [ ] Integration with communication tools (Slack, Teams)
- [ ] Logging and monitoring system
- [ ] Comprehensive documentation and examples

### Phase 6: Production and Extensibility
- [ ] Performance optimization
- [ ] Complete containerization (Docker)
- [ ] End-to-end demonstrations
- [ ] Framework for extensions and plugins
- [ ] Contribution guidelines

## Usage Guide

### Setting Up the Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/davidamom/neuralflake.git
   cd neuralflake
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Using venv
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Alternative with Poetry:
   ```bash
   poetry install
   ```

### Configuration

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
2. **Edit the `.env` file** to add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Running NeuralFlake

1. **Verify the installation:**
   ```bash
   python -m data_agent.cli --help
   ```
   This will display all available commands.

2. **Index documents** (required for RAG functionality):
   ```bash
   # Index the NeuralFlake codebase itself
   python -m data_agent.cli index ./data_agent
   ```
   This indexes the source code for context-aware responses.

3. **Start an interactive chat session:**
   ```bash
   python -m data_agent.cli chat
   ```
   
   Or, if using Poetry:
   ```bash
   poetry run neuralflake chat
   ```

### Usage Examples

1. **Basic chat (without RAG):**
   ```bash
   python -m data_agent.cli chat --no-rag
   ```
   Try asking general questions about data engineering.

2. **Chat with RAG capabilities:**
   ```bash
   python -m data_agent.cli chat
   ```
   Try questions about the codebase, such as:
   - "How does the chunking system work?"
   - "Explain the structure of the agent"
   - "What are the main classes in the RAG system?"

3. **Single query mode:**
   ```bash
   python -m data_agent.cli query "How does ChromaVectorStore work?"
   ```

### Special Commands in Chat Mode

- `/help` - Display available commands
- `/clear` - Clear conversation history
- `/save <filename>` - Save conversation to file
- `/load <filename>` - Load conversation from file
- `exit`, `quit`, `q`, `bye` - End the conversation

## How it Works

### Indexing Process

When you run `index` command, NeuralFlake processes your documents through these steps:

1. **Document Collection**:
   - The `DocumentProcessor` reads files from the specified directory
   - Identifies file types (.py, .md, .json, etc.)
   - Extracts raw text content from each file

2. **Chunking (Text Splitting)**:
   - Each document is divided into smaller "chunks" (~1000 characters by default)
   - Chunks have overlap to preserve context between divisions
   - Metadata is added to each chunk (file source, file type, chunk position)

3. **Embedding Generation**:
   - Each text chunk is sent to the OpenAI API
   - The API returns an embedding vector (1536 dimensions for ada-002)
   - These vectors capture the semantic meaning of the text

4. **Chroma Storage**:
   - The Chroma vector database creates a collection in `./data/chroma` (configurable)
   - For each chunk, it stores:
     - The original text
     - The embedding vector
     - Associated metadata
   - All data is persisted locally on disk

![alt text](<assets/NeuralFlake - NeuralFlake Indexing Process.svg>)

### Retrieval Process

When you ask questions in `chat` mode, NeuralFlake follows these steps:

1. **Query Processing**:
   - Your question is converted to an embedding using the same API
   - This embedding represents the semantic meaning of your question

2. **Similarity Search**:
   - `ChromaVectorStore` calculates cosine similarity between your question's embedding and all stored embeddings
   - Selects the most similar documents (top_k=4 by default)

3. **Context Assembly**:
   - Retrieved chunks are concatenated
   - This relevant context is added to the prompt sent to the LLM

4. **Response Generation**:
   - The LLM (OpenAI) receives your original question + the relevant context
   - Generates a response informed by the retrieved documents
   - The response is displayed in the console

5. **Conversation Management**:
   - Your question and the agent's response are added to conversation history
   - This history maintains context between interactions

![alt text](<assets/NeuralFlake - NeuralFlake Retrieval Process.svg>)

### Data Flow

```
[Your Files] → DocumentProcessor → Text Chunks → EmbeddingProvider → Vectors → ChromaVectorStore

[Your Question] → Embedding → ChromaVectorStore → Relevant Documents → Augmented Prompt → LLM → Response
```

This RAG process allows NeuralFlake to provide responses informed by your documents, without having been pre-trained on them.

## Requirements

### Functional Requirements
1. Query and analyze Snowflake metadata (tables, schemas, jobs)
2. Analyze source code in Git repositories
3. Interpret dbt YAML files (models, sources, macros)
4. Generate natural language responses to technical queries
5. Suggest optimizations and improvements in data pipelines
6. Maintain interaction history for future reference
7. Execute on-demand analyses with user approval

### Non-Functional Requirements
1. Adequate response time (<5s for simple queries)
2. Security in handling credentials and sensitive information
3. High accuracy in technical responses
4. Traceability (citation of sources)
5. Modularity and extensibility
6. Clear and comprehensive documentation
7. Automated testing (>80% coverage)

## Initial Project Structure

```
data_agent/
│
├── core/                     # Core agent components
│   ├── __init__.py
│   ├── agent.py              # Main agent implementation
│   ├── memory.py             # Memory/history system
│   ├── planner.py            # Action planning component
│   └── config.py             # Global configurations
│
├── rag/                      # RAG component
│   ├── __init__.py
│   ├── document_processor.py # Document processing
│   ├── embeddings.py         # Embeddings generation and handling
│   ├── chunking.py           # Chunking strategies
│   ├── retriever.py          # Retrieval system
│   └── vector_store/         # Vector database adapters
│       ├── __init__.py
│       ├── base.py           # Base interface
│       ├── chroma.py
│       └── pinecone.py
│
├── connectors/               # Data source connectors
│   ├── __init__.py
│   ├── base.py               # Base connector class
│   ├── snowflake/
│   │   ├── __init__.py
│   │   ├── connector.py
│   │   └── metadata.py       # Metadata handling
│   ├── git/
│   │   ├── __init__.py
│   │   ├── connector.py
│   │   └── parser.py
│   └── dbt/
│       ├── __init__.py
│       ├── connector.py
│       └── yaml_parser.py
│
├── llm/                      # Language model interface
│   ├── __init__.py
│   ├── provider.py           # Provider factory
│   ├── openai.py
│   ├── anthropic.py
│   └── prompt_templates/     # Organized prompt templates
│       ├── __init__.py
│       ├── snowflake.py
│       ├── git.py
│       └── dbt.py
│
├── tools/                    # Agent tools
│   ├── __init__.py
│   ├── sql_generator.py
│   ├── code_reviewer.py
│   └── dbt_analyzer.py
│
├── api/                      # API interface
│   ├── __init__.py
│   ├── routes.py
│   ├── middleware.py
│   └── schemas.py            # Pydantic schemas
│
├── ui/                       # User interface
│   ├── __init__.py
│   ├── app.py                # Streamlit/Gradio
│   └── components/
│
├── security/                 # Security components
│   ├── __init__.py
│   ├── auth.py
│   └── credentials.py        # Secure credentials management
│
├── utils/                    # Common utilities
│   ├── __init__.py
│   ├── logging.py
│   └── helpers.py
│
├── tests/                    # Tests
│   ├── __init__.py
│   ├── test_connectors/
│   ├── test_rag/
│   └── test_agent.py
│
├── scripts/                  # Utility scripts
│   ├── setup_vector_db.py
│   └── index_documents.py
│
├── examples/                 # Usage examples
│   ├── snowflake_analysis.py
│   └── dbt_review.py
│
├── docs/                     # Documentation
│   └── ...
│
├── .env.example              # Environment variables template
├── pyproject.toml            # Project configuration (Poetry)
├── setup.py                  # Traditional setup (alternative)
├── requirements.txt          # Dependencies
├── Dockerfile                # For containerization
├── docker-compose.yml        # For complete environment
└── README.md                 # Main documentation
```

## How to Contribute

TBD - Will be defined as the project progresses.

## License

This project is licensed under [insert license].

[tool.poetry.scripts]
neuralflake = "data_agent.cli:app" 