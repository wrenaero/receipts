# CLAUDE.md - AI Assistant Development Guide

**Repository:** receipts
**Last Updated:** 2025-11-27
**Purpose:** Receipt management system

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Codebase Structure](#codebase-structure)
3. [Development Workflows](#development-workflows)
4. [Key Conventions](#key-conventions)
5. [Architecture Guidelines](#architecture-guidelines)
6. [Testing Strategy](#testing-strategy)
7. [Git Workflow](#git-workflow)
8. [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Repository Overview

### Purpose
This repository manages receipt tracking, storage, and processing functionality. The system is designed to handle receipt data including capturing, storing, categorizing, and analyzing receipt information.

### Project Status
- **Stage:** Initial development
- **Primary Language:** TBD (will be established based on first implementation)
- **Framework:** TBD
- **Database:** TBD

### Key Features (Planned)
- Receipt capture and storage
- OCR/text extraction from receipt images
- Categorization and tagging
- Expense tracking and reporting
- Search and filtering capabilities
- Export functionality

---

## Codebase Structure

### Recommended Directory Layout

When implementing this project, follow this structure:

```
receipts/
├── src/                      # Source code
│   ├── api/                 # API endpoints/routes
│   ├── models/              # Data models and schemas
│   ├── services/            # Business logic
│   ├── utils/               # Utility functions
│   ├── config/              # Configuration files
│   └── middleware/          # Middleware components
├── tests/                    # Test files
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test fixtures and mock data
├── docs/                     # Documentation
├── scripts/                  # Build and utility scripts
├── .github/                  # GitHub workflows and templates
├── CLAUDE.md                # This file
├── README.md                # User-facing documentation
├── CONTRIBUTING.md          # Contribution guidelines
└── package.json|requirements.txt|go.mod  # Dependencies

```

### Module Organization

- **Models:** Define data structures for receipts, users, categories, etc.
- **Services:** Implement business logic (receipt processing, OCR integration, analytics)
- **API:** RESTful or GraphQL endpoints for external interaction
- **Utils:** Helper functions for date parsing, currency conversion, validation, etc.

---

## Development Workflows

### Adding New Features

1. **Planning Phase**
   - Use TodoWrite tool to create task list
   - Break down feature into small, testable components
   - Identify affected modules and dependencies

2. **Implementation Phase**
   - Start with data models and schemas
   - Implement business logic in services
   - Create API endpoints
   - Write tests alongside code (TDD when appropriate)

3. **Testing Phase**
   - Run unit tests for individual components
   - Run integration tests for workflows
   - Manual testing of new features
   - Update documentation

4. **Review Phase**
   - Self-review all changes
   - Check for security vulnerabilities
   - Verify error handling is appropriate
   - Ensure code follows conventions

### Bug Fixes

1. **Reproduction**
   - Write failing test that reproduces the bug
   - Understand root cause through debugging

2. **Fix**
   - Implement minimal fix
   - Verify test now passes
   - Check for similar issues elsewhere

3. **Prevention**
   - Add additional test cases
   - Update validation or error handling if needed

---

## Key Conventions

### Code Style

#### General Principles
- **Simplicity First:** Write the simplest code that solves the problem
- **No Over-Engineering:** Avoid premature abstractions and unnecessary complexity
- **Clear Naming:** Use descriptive, self-documenting names for variables, functions, and classes
- **Consistent Formatting:** Follow language-specific style guides (PEP 8 for Python, ESLint for JavaScript, etc.)

#### Comments and Documentation
- Add comments only when logic isn't self-evident
- Use docstrings/JSDoc for public APIs and complex functions
- Keep comments up-to-date with code changes
- Avoid obvious comments that just repeat what code does

#### Error Handling
- Validate at system boundaries (user input, external APIs)
- Trust internal code and framework guarantees
- Use specific error types/classes
- Provide actionable error messages
- Log errors with sufficient context

### Naming Conventions

**Files:**
- Use lowercase with hyphens: `receipt-service.js`, `user-model.py`
- Test files: `receipt-service.test.js`, `test_user_model.py`

**Functions/Methods:**
- Use verbs: `createReceipt()`, `validateAmount()`, `parseDate()`
- Be specific: prefer `calculateTotalWithTax()` over `calculate()`

**Variables:**
- Use nouns: `receiptData`, `totalAmount`, `userPreferences`
- Boolean variables: `isValid`, `hasPermission`, `shouldProcess`

**Constants:**
- Use UPPER_CASE: `MAX_FILE_SIZE`, `DEFAULT_CURRENCY`, `API_TIMEOUT`

**Classes:**
- Use PascalCase: `ReceiptProcessor`, `ImageAnalyzer`, `UserService`

### Data Handling

#### Receipt Data Structure
```json
{
  "id": "uuid",
  "userId": "uuid",
  "merchantName": "string",
  "date": "ISO8601 timestamp",
  "totalAmount": "decimal",
  "currency": "string (ISO 4217)",
  "category": "string",
  "items": [
    {
      "description": "string",
      "quantity": "number",
      "unitPrice": "decimal",
      "totalPrice": "decimal"
    }
  ],
  "paymentMethod": "string",
  "imageUrl": "string",
  "extractedText": "string",
  "metadata": "object",
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

#### Currency Handling
- Always store amounts as decimal types (never floats)
- Store currency code alongside amounts
- Use ISO 4217 currency codes (USD, EUR, GBP, etc.)
- Handle currency conversion explicitly when needed

#### Date/Time Handling
- Store all timestamps in UTC
- Use ISO 8601 format for serialization
- Convert to local timezone only for display
- Parse dates defensively with validation

---

## Architecture Guidelines

### Separation of Concerns

**Controllers/Routes:**
- Handle HTTP request/response
- Validate input schemas
- Call appropriate services
- Return formatted responses

**Services:**
- Contain business logic
- Are framework-agnostic
- Can be tested independently
- May call other services or repositories

**Repositories/Models:**
- Handle data persistence
- Abstract database operations
- Return domain objects
- Don't contain business logic

**Utilities:**
- Pure functions when possible
- Single responsibility
- Reusable across modules
- Well-tested

### Security Considerations

1. **Input Validation**
   - Validate all user input
   - Sanitize file uploads
   - Check file types and sizes
   - Use allowlists over denylists

2. **Authentication & Authorization**
   - Implement proper user authentication
   - Verify permissions before operations
   - Use secure session management
   - Hash passwords with bcrypt/argon2

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Never log sensitive information
   - Implement proper access controls

4. **Common Vulnerabilities**
   - Prevent SQL injection (use parameterized queries)
   - Prevent XSS (sanitize output)
   - Prevent CSRF (use tokens)
   - Prevent path traversal (validate file paths)
   - Rate limit API endpoints

### Performance Considerations

- Use pagination for large datasets
- Implement caching where appropriate
- Optimize database queries (use indexes)
- Compress images before storage
- Use async operations for I/O-bound tasks
- Implement connection pooling for databases

---

## Testing Strategy

### Test Coverage Goals
- Minimum 80% code coverage for business logic
- 100% coverage for critical paths (payment processing, data persistence)
- All public APIs have integration tests
- Edge cases and error conditions are tested

### Testing Pyramid

**Unit Tests (70%)**
- Test individual functions and methods
- Mock external dependencies
- Fast execution
- Focus on business logic

**Integration Tests (20%)**
- Test component interactions
- Use test database
- Test API endpoints end-to-end
- Verify data persistence

**E2E Tests (10%)**
- Test complete user workflows
- Use staging environment
- Test critical paths only
- May include manual testing

### Test Organization

```
tests/
├── unit/
│   ├── services/
│   │   ├── receipt-service.test.js
│   │   └── ocr-service.test.js
│   └── utils/
│       └── date-utils.test.js
├── integration/
│   ├── api/
│   │   └── receipts-api.test.js
│   └── database/
│       └── receipt-repository.test.js
└── fixtures/
    ├── sample-receipts.json
    └── test-images/
```

### Writing Good Tests

```javascript
// Good: Descriptive test names
describe('ReceiptService', () => {
  describe('calculateTotal', () => {
    it('should sum item prices correctly', () => {
      // Test implementation
    });

    it('should throw error for negative prices', () => {
      // Test implementation
    });

    it('should handle empty items array', () => {
      // Test implementation
    });
  });
});

// Good: Test one thing at a time
it('should create receipt with valid data', () => {
  const receipt = createReceipt(validData);
  expect(receipt).toBeDefined();
  expect(receipt.id).toBeDefined();
  expect(receipt.totalAmount).toBe(validData.totalAmount);
});

// Avoid: Testing multiple unrelated things
it('should work correctly', () => {
  // Tests creation, update, deletion, and querying all at once
});
```

---

## Git Workflow

### Branch Naming

- Feature branches: `feature/receipt-ocr`, `feature/export-csv`
- Bug fixes: `fix/amount-calculation`, `fix/date-parsing`
- Claude AI branches: `claude/claude-md-*` (auto-generated)
- Release branches: `release/v1.0.0`
- Hotfix branches: `hotfix/critical-security-fix`

### Commit Messages

Follow the Conventional Commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(receipts): add OCR text extraction
fix(api): correct total calculation for multi-currency
docs(readme): update installation instructions
test(services): add tests for receipt validation
refactor(models): simplify receipt schema
```

### Pull Request Guidelines

1. **Before Creating PR**
   - Ensure all tests pass
   - Update documentation if needed
   - Review your own changes first
   - Rebase on latest main if needed

2. **PR Description Should Include**
   - Summary of changes
   - Motivation and context
   - Testing performed
   - Screenshots (if UI changes)
   - Breaking changes (if any)

3. **PR Review Checklist**
   - Code follows conventions
   - Tests are adequate
   - No security vulnerabilities
   - Documentation is updated
   - No unnecessary complexity

---

## AI Assistant Guidelines

### General Principles for AI Development

1. **Read Before Writing**
   - Always read existing files before modifying
   - Understand context and existing patterns
   - Never propose changes to unread code

2. **Use TodoWrite Tool**
   - Create task list for complex features
   - Break down work into small steps
   - Mark tasks as in_progress/completed
   - Keep only one task in_progress at a time

3. **Minimize Changes**
   - Only change what's necessary
   - Don't refactor unrelated code
   - Don't add unsolicited features
   - Keep solutions simple and focused

4. **Security First**
   - Check for OWASP Top 10 vulnerabilities
   - Validate input at boundaries
   - Use parameterized queries
   - Sanitize output for XSS prevention
   - Never commit secrets or credentials

5. **Testing Requirements**
   - Write tests for new features
   - Update tests when changing behavior
   - Ensure tests pass before committing
   - Test error cases and edge conditions

### Working with This Repository

**When Adding Features:**
1. Read relevant existing code
2. Create TodoWrite task list
3. Implement following architecture guidelines
4. Write/update tests
5. Update documentation if needed
6. Commit with clear message
7. Push to claude/* branch

**When Fixing Bugs:**
1. Reproduce the bug (write failing test if possible)
2. Read surrounding code for context
3. Implement minimal fix
4. Verify tests pass
5. Commit with fix/* prefix

**When Refactoring:**
1. Only refactor when explicitly requested
2. Ensure tests exist before refactoring
3. Make small, incremental changes
4. Verify tests still pass after each change
5. Never mix refactoring with feature work

### Common Pitfalls to Avoid

❌ **Don't:**
- Create files without checking if they exist
- Add unnecessary abstractions
- Over-engineer solutions
- Add comments to unchanged code
- Commit without running tests
- Push to wrong branch
- Add error handling for impossible conditions
- Create helpers for one-time operations
- Design for hypothetical requirements

✅ **Do:**
- Use specialized tools (Read, Edit, Write) over bash
- Run tools in parallel when independent
- Trust framework guarantees
- Keep solutions simple
- Delete unused code completely
- Follow existing patterns
- Ask for clarification when ambiguous
- Focus on current requirements

### File Operations Best Practices

```bash
# Good: Use Read tool
Read file_path="/home/user/receipts/src/services/receipt-service.js"

# Bad: Use bash cat
Bash command="cat src/services/receipt-service.js"

# Good: Use Edit tool for changes
Edit file_path="/path/to/file" old_string="..." new_string="..."

# Bad: Use sed/awk
Bash command="sed -i 's/old/new/' file"

# Good: Use Grep tool for searching
Grep pattern="calculateTotal" output_mode="content"

# Bad: Use bash grep
Bash command="grep -r 'calculateTotal' src/"
```

### Repository-Specific Workflows

**Receipt Processing Feature:**
1. Check if OCR library is configured
2. Add service method for image processing
3. Add API endpoint for upload
4. Implement validation (file type, size)
5. Add tests for happy path and errors
6. Update API documentation

**Database Changes:**
1. Create migration file
2. Update model/schema
3. Update affected services
4. Add database tests
5. Update seed data if needed
6. Document schema changes

**API Endpoint Addition:**
1. Define request/response schemas
2. Add route handler
3. Implement service method
4. Add input validation
5. Add integration test
6. Update API documentation

---

## Additional Resources

### Useful Commands

```bash
# Run tests
npm test          # JavaScript/Node
pytest            # Python
go test ./...     # Go

# Lint code
npm run lint      # JavaScript
flake8 .          # Python
golangci-lint run # Go

# Format code
npm run format    # JavaScript (Prettier)
black .           # Python
gofmt -w .        # Go

# Database migrations
npm run migrate   # JavaScript
alembic upgrade head  # Python (SQLAlchemy)
migrate -path migrations -database "..." up  # Go

# Build
npm run build     # JavaScript
python setup.py build  # Python
go build          # Go
```

### Documentation Links

- [Conventional Commits](https://www.conventionalcommits.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [ISO 4217 Currency Codes](https://en.wikipedia.org/wiki/ISO_4217)
- [ISO 8601 Date/Time](https://en.wikipedia.org/wiki/ISO_8601)

---

## Changelog

### 2025-11-27
- Initial CLAUDE.md creation
- Established repository structure and conventions
- Defined development workflows and guidelines
- Set up AI assistant best practices

---

## Contact & Support

For questions or clarifications about this guide:
- Check existing documentation in `/docs`
- Review code examples in the repository
- Ask the user for specific requirements or preferences

---

**Remember:** The goal is to write clean, maintainable, secure code that solves the problem at hand. Keep it simple, test thoroughly, and follow established patterns.
