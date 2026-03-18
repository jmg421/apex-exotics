# Debugging Best Practices: Do's and Don'ts

*Inspired by the "AI Bugs" video - a cautionary tale about proper bug fixing*

## ✅ DO: Proper Debugging Approach

### 1. **Understand the Problem First**
- Read error messages completely
- Reproduce the bug consistently
- Identify the root cause, not just symptoms
- Document what you observe vs. what you expect

### 2. **Use Systematic Investigation**
- Start with logs and stack traces
- Use debuggers to step through code
- Add strategic print statements/logging
- Test hypotheses with minimal changes

### 3. **Fix the Root Cause**
- Address the underlying issue, not just the symptom
- Understand why the bug occurred
- Consider edge cases and similar patterns
- Write tests to prevent regression

### 4. **Validate Your Fix**
- Test the specific bug scenario
- Run full test suite
- Check for unintended side effects
- Verify the fix works in different environments

### 5. **Clean Up Properly**
- Remove temporary debugging code
- Update documentation if needed
- Refactor if the fix reveals design issues
- Share learnings with the team

## ❌ DON'T: Anti-Patterns to Avoid

### 1. **Don't Hide the Problem**
```javascript
// ❌ BAD: Hiding the error
try {
  riskyOperation();
} catch (e) {
  // Ignore error - it'll probably be fine
}

// ✅ GOOD: Handle appropriately
try {
  riskyOperation();
} catch (e) {
  logger.error('Risk operation failed:', e);
  return fallbackValue();
}
```

### 2. **Don't Use Band-Aid Solutions**
```python
# ❌ BAD: Working around the symptom
if user.name == "undefined":
    user.name = "Anonymous"  # Why is it undefined?

# ✅ GOOD: Fix the root cause
def create_user(name=None):
    if name is None:
        raise ValueError("User name is required")
    return User(name=name)
```

### 3. **Don't Guess and Check**
- Don't randomly change code hoping it works
- Don't copy-paste solutions without understanding
- Don't apply fixes without knowing why they work
- Don't skip testing your changes

### 4. **Don't Leave Debugging Artifacts**
```javascript
// ❌ BAD: Leaving debug code in production
console.log("DEBUG: user data:", user);
debugger; // Forgot to remove
window.DEBUG_MODE = true;

// ✅ GOOD: Clean, production-ready code
const processedUser = validateAndProcessUser(user);
```

### 5. **Don't Rush the Process**
- Don't skip reproduction steps
- Don't assume you know the cause immediately
- Don't fix multiple issues in one commit
- Don't deploy without proper testing

### 6. **Don't Re-Implement Existing Solutions**
```bash
# ❌ BAD: Implementing without checking history
git commit -m "Add auto-login feature"
# (Feature already exists in codebase)

# ✅ GOOD: Check first, then implement
git log --all --grep="auto-login\|login.*checkout"
git grep "checkout.*success\|auto.*login"
# Found existing implementation, use it instead
```

**Before implementing any feature:**
- Search git history: `git log --all --grep="feature-name"`
- Search codebase: `git grep "pattern"` or `grep -r "pattern"`
- Check for similar endpoints/functions
- Review existing architecture decisions
- Ask: "Has this been solved before?"

**Warning signs you're re-implementing:**
- "This feels familiar"
- Multiple files with similar names (e.g., `checkout_success.py` and `login_from_checkout`)
- Duplicate API endpoints with slight variations
- Comments like "// TODO: consolidate with existing implementation"

## 🎯 The "Leaf in the Gravel" Problem

**The Metaphor:** Like the AI agent in the video who buried the leaf instead of removing it, developers often:

- **Catch and ignore exceptions** instead of handling them properly
- **Add conditional checks** around symptoms instead of fixing causes  
- **Disable failing tests** instead of fixing the underlying issues
- **Add workarounds** that mask problems for future developers

## 🔧 Tools and Techniques

### Investigation Tools
- **Debuggers**: Step through code execution
- **Logging**: Strategic placement for visibility
- **Profilers**: Identify performance bottlenecks
- **Static Analysis**: Catch issues before runtime

### Testing Approaches
- **Unit Tests**: Isolate and verify individual components
- **Integration Tests**: Verify component interactions
- **Regression Tests**: Prevent old bugs from returning
- **Manual Testing**: Validate user experience

## 📝 Documentation

### What to Document
- Steps to reproduce the bug
- Root cause analysis
- Solution rationale
- Testing performed
- Potential side effects

### Bug Report Template
```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Expected vs. actual result

## Root Cause
Why this happened

## Solution
What was changed and why

## Testing
How the fix was validated
```

## 🚨 Red Flags

Watch out for these warning signs:
- "It works on my machine"
- "Let's just catch all exceptions"
- "This is a quick fix"
- "We'll come back and fix this properly later"
- "I'm not sure why this works, but it does"
- **"I think we need to implement X"** (without checking if X already exists)
- **"This feature has been implemented 3+ times"** (sign of poor code archaeology)

## 🔍 Code Archaeology: Check Before You Build

Before implementing any feature, perform code archaeology:

### 1. **Search Git History**
```bash
# Search commit messages
git log --all --grep="feature-name\|related-term"

# Search for when a file was added
git log --all --diff-filter=A -- path/to/file

# Find commits that touched specific code
git log -S "function_name" --source --all
```

### 2. **Search Codebase**
```bash
# Search all files
git grep "pattern"
grep -r "pattern" --include="*.py"

# Find similar function names
git grep "checkout.*success\|success.*checkout"

# Check for API endpoints
grep -r "@router\|@app.route" app/
```

### 3. **Check for Duplicates**
- Multiple files with similar names
- Similar API endpoints (`/api/checkout-success` vs `/api/auth/login-from-checkout`)
- Functions that do the same thing with different names
- Commented-out code that hints at previous attempts

### 4. **Review Architecture**
- Check `docs/` for architecture decisions
- Look for README files explaining design choices
- Review existing patterns before creating new ones

## 🏛️ Software Archaeology: Understanding Legacy Code

*Based on Michael Rozlog's six-step process and OOPSLA workshop methodologies*

When debugging unfamiliar or legacy code, use software archaeology to understand what you've inherited before attempting fixes.

### The Six-Step Archaeological Process

#### 1. **Inventory (Codebase Reconnaissance)**
**Goal:** Get a high-level understanding of structure and components

**Actions:**
- Build and run the application (verify dependencies work)
- Explore directory structure and file organization
- Identify entry points (`main()`, API endpoints, config files)
- Read any documentation (README, API docs, comments)
- Review version control history for major changes
- Use `tree` command or IDE file browser to visualize structure

**Tools:** `git log`, IDE file search, directory visualizers

**Output:** Mental map of codebase organization

#### 2. **Establish Context (Map Dependencies)**
**Goal:** Understand system architecture and relationships

**Actions:**
- Chart module interdependencies
- Identify tightly coupled components
- Note circular dependencies or unusual patterns
- Map external dependencies and integration points
- Document data flow into/out of the system

**Tools:** Dependency graphs, call hierarchies, UML generators

**Scary Section Indicators:**
- High cyclomatic complexity
- Frequent bug fixes in git history
- Lack of test coverage
- Deep nesting, long methods, many parameters

#### 3. **Static Analysis (Identify Patterns)**
**Goal:** Find potential problems without executing code

**Actions:**
- Use static analysis tools (SonarQube, ESLint, Pylint)
- Identify code smells (duplicated code, long methods)
- Measure complexity metrics
- Check for security vulnerabilities
- Review coding patterns and conventions

**Tools:** SonarQube, FindBugs, linters, complexity analyzers

**Output:** List of potential issues and complexity hotspots

#### 4. **Dynamic Analysis (Observe Behavior)**
**Goal:** Watch code execute in real-time

**Actions:**
- Use debugger to step through execution
- Add strategic logging statements
- Run existing unit tests
- Profile for performance bottlenecks
- Monitor system resources (CPU, memory, network)

**Tools:** Debuggers, profilers, logging frameworks, unit test runners

**Output:** Insights into runtime behavior and performance

#### 5. **Reverse Engineering (Deduce Intent)**
**Goal:** Understand the "why" behind the code

**Actions:**
- Trace execution paths carefully
- Experiment in isolated environment
- Look for design patterns
- Collaborate with developers who know the code
- Document findings with diagrams and notes

**Techniques:**
- **Synoptic signature analysis**: View code structure (punctuation only)
- **2-point font view**: See high-level structure without details
- **Network analysis**: Understand developer collaboration patterns

**Output:** Documented understanding of functionality and design

#### 6. **Refactor (With Extreme Caution)**
**Goal:** Improve code only after understanding it

**Actions:**
- Make small, incremental changes
- Write characterization tests first
- Use automated refactoring tools
- Test thoroughly after each change
- Get code reviews

**Warning:** Only refactor code you understand well with adequate test coverage

**Output:** Cleaner, more maintainable codebase

### Answering Key Archaeological Questions

**"What Have I Just Inherited?"**
- Codebase inventory: Languages, frameworks, LOC, age
- Documentation status: What exists vs. missing
- Test coverage: Where safety nets exist
- Technical debt: Known issues, outdated dependencies
- Active vs. dead code: What's actually used

**"Where Are the Scary Sections?"**
Metrics to identify risky code:
- High bug fix frequency (check git history)
- Complex functions (high cyclomatic complexity)
- Poor test coverage
- Frequent changes by multiple developers
- Commented-out code or TODOs
- Hardcoded values or magic numbers
- Lack of error handling

### Practical Application

**Before Debugging Legacy Code:**
1. Start with Inventory (30 min) - understand structure
2. Map Dependencies (1 hour) - identify relationships
3. Run Static Analysis (automated) - find obvious issues
4. Set up Dynamic Analysis (debugger + logging)
5. Only then start actual debugging

**Timeboxing:** Set limits for each step to avoid analysis paralysis

**Documentation:** Record findings for future developers

### Real Example: Auto-Login After Checkout

**❌ What Happened:**
```bash
# Implemented /api/auth/login-from-checkout
# But /api/checkout-success already existed!
git log --grep="checkout.*login"
# Found: "Add checkout success flow for automatic user login"
# Implemented 3+ times in different ways
```

**✅ What Should Have Happened:**
```bash
# 1. Search first
git log --all --grep="checkout.*login\|auto.*login"
git grep "checkout.*success"

# 2. Found existing implementation
# 3. Use or improve existing code instead of duplicating
```

**Cost of Re-Implementation:**
- Wasted development time
- Multiple code paths doing the same thing
- Harder to maintain and debug
- Confusion about which implementation to use

## 💡 Remember

**Good debugging is like archaeology** - you're uncovering the truth about what happened, not just making the symptoms disappear. The goal is understanding and resolution, not just making the error messages go away.

**The best debuggers are patient, systematic, and thorough.** They fix problems, not symptoms.

---

*"The most effective debugging tool is still careful thought, coupled with judiciously placed print statements."* - Brian Kernighan
