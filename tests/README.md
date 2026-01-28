# Test Suite for Word Analysis Service

## Overview

This test suite provides comprehensive coverage for the Word Analysis Service, including:
- Unit tests for individual components
- Integration tests for API endpoints
- Database CRUD operation tests
- Document parser tests
- Configuration and logging tests

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_config.py           # Configuration tests
├── test_logger.py           # Logging system tests
├── test_crud.py             # Database CRUD tests
├── test_api_routes.py       # API endpoint tests
└── test_parser.py           # Document parser tests
```

## Running Tests

### Run All Tests

```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py
```

### Run Specific Test Files

```bash
pytest tests/test_config.py
pytest tests/test_parser.py -v
```

### Run Specific Test Classes or Functions

```bash
# Run specific class
pytest tests/test_parser.py::TestDocxParser -v

# Run specific test
pytest tests/test_parser.py::TestDocxParser::test_parse_by_heading_simple -v
```

### Run with Coverage

```bash
# Using pytest
pytest --cov=src/doc_analysis --cov-report=html

# Using test runner
python run_tests.py --cov
```

### Filter by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Fixtures

### Database Fixtures

- `db_engine`: In-memory SQLite database
- `db_session`: Database session for testing
- `mock_db_session`: Mock database session

### API Fixtures

- `client`: FastAPI test client with database override
- `client_no_db`: FastAPI test client without database

### Document Fixtures

- `sample_docx_content`: Sample Word document content
- `sample_large_docx`: Large document for size limit testing
- `invalid_file_content`: Invalid file for error handling tests

### Mock Fixtures

- `mock_logger`: Mock logger instance
- `mock_settings`: Mock application settings

### Data Fixtures

- `sample_document_data`: Sample document data
- `sample_section_data`: Sample section data

## Test Categories

### Unit Tests (`test_config.py`, `test_logger.py`)

**Configuration Tests:**
- Default settings validation
- Environment variable overrides
- File upload settings
- Pagination settings
- Edge cases

**Logger Tests:**
- Logging setup
- Logger creation
- Log level handling
- Exception logging

### CRUD Tests (`test_crud.py`)

**Document CRUD:**
- Create document
- Retrieve by ID
- Retrieve by hash
- Mark as parsed
- Duplicate detection

**Section CRUD:**
- Create section
- Create with parent
- Retrieve sections
- Count sections

**Table & Image CRUD:**
- Create tables
- Create images
- Relationship handling

**Pagination Optimization:**
- N+1 query prevention
- Bulk count retrieval

### API Tests (`test_api_routes.py`)

**Health Endpoint:**
- Database connection check
- Error handling

**Document Parsing:**
- Successful parsing
- File validation
- Size limits
- Duplicate detection
- Error handling

**Document Retrieval:**
- Get by ID
- Get list with pagination
- Not found handling

**Section Operations:**
- Get section by path
- Get section tree
- Hierarchy handling

### Parser Tests (`test_parser.py`)

**Basic Parsing:**
- Heading detection
- Section creation
- Content extraction
- Numbering

**Advanced Features:**
- Parent-child relationships
- Nested headings
- Table extraction
- Image extraction

**Edge Cases:**
- Empty documents
- No headings
- Deep nesting
- Corrupted files

## Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| `config.py` | > 90% |
| `logger.py` | > 90% |
| `crud.py` | > 85% |
| `routes.py` | > 80% |
| `docx.py` | > 75% |

## CI/CD Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Best Practices

### Writing New Tests

1. **Use descriptive names**: `test_parse_document_with_nested_headings`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use fixtures**: Don't duplicate setup code
4. **Test edge cases**: Not just happy paths
5. **Mock external dependencies**: Database, file system

### Example Test Structure

```python
def test_something_descriptive(fixture):
    # Arrange - Set up test data
    test_data = {"key": "value"}

    # Act - Execute the function
    result = function_under_test(test_data)

    # Assert - Verify results
    assert result["expected"] == "value"
    assert result.count == 1
```

## Troubleshooting

### Import Errors

```bash
# Add src to path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or run from project root
cd /path/to/project
pytest
```

### Database Errors

Tests use in-memory SQLite, so no database setup is required.

### Missing Dependencies

```bash
pip install pytest pytest-cov pytest-asyncio
```

## Continuous Improvement

- Add tests for any new features
- Update tests when fixing bugs
- Maintain > 80% code coverage
- Run tests before committing
