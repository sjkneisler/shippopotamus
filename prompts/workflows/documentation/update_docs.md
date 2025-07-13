<!-- id:update_docs emoji:📚 type:workflow tags:documentation,maintenance -->

# Update Documentation Workflow

Let's go update the documentation, given the work that has just been completed. Read through various existing documentation to get a lay of the land, then make a plan to update the docs to cover what's been completed, fix any outdated information or cruft, clean up anything unnecessary, and in general "leave things better than we found them."

## Key Considerations

Keep in mind the usual concerns around documentation, especially relating to LLM Agentic Coding:

### Documentation is important so that both the human and the LLM understand:
- What's currently implemented
- What's left to be done
- What issues did we face that we might face again in the future
- Patterns and systems in place so that we have a comprehensive understanding

### Too much documentation is bad
- It's hard to read, both for humans and LLMs, and can lead to cruft
- Outdated documentation is worse than no documentation
- Verbose documentation fills up context windows unnecessarily

### File count balance is critical
- **Too many files**: LLM has to either make a ton of tool calls (bad) to read them all, or doesn't get enough information when reading a small subset
- **Too few files**: LLMs are forced to load large files into context, which can lead to unnecessarily filling up the context window with irrelevant information, and can make edits more difficult

## Workflow Steps

1. **Survey Current Documentation**
   - Read README.md and other top-level docs
   - Check for CHANGELOG, CONTRIBUTING, or other standard files
   - Scan documentation directories for structure
   - Note any obviously outdated information

2. **Identify Recent Changes**
   - Review recent commits or ask about completed work
   - Identify new features, removed features, or changed behaviors
   - Check for new dependencies or requirements

3. **Create Update Plan**
   - List specific files that need updates
   - Identify information to add, update, or remove
   - Consider if restructuring would improve clarity
   - Plan for appropriate file granularity

4. **Execute Updates**
   - Update feature documentation
   - Fix outdated examples and code snippets
   - Remove references to deprecated functionality
   - Add documentation for new capabilities
   - Ensure consistency across all docs

5. **Quality Checks**
   - Verify all code examples work
   - Check that links are valid
   - Ensure terminology is consistent
   - Confirm documentation matches implementation

## Remember

- Focus on clarity and accuracy over completeness
- Prefer showing over telling (examples > descriptions)
- Keep the target audience in mind
- Leave clear breadcrumbs for future updates