# FA-C002-LAB Project Instructions

## Project Philosophy

**Core Principles:**

- **Lean & Concise**: No verbose explanations, no theoretical fluff
- **Technical Focus**: Direct, practical, implementation-focused
- **Test-Driven**: Every decision maps to mid-course test criteria
- **Business Analysis Ready**: Data modeling focused on real business questions
- **Ship Working Code**: Functional over perfect, iterate based on feedback

## Documentation Standards

**What Belongs in Docs:**

- Technical specifications
- Configuration details
- Command references
- Test criteria mappings

**What Doesn't:**

- Long-form tutorials (user learns by doing)
- Theoretical explanations (user understands fundamentals)
- Step-by-step guides (user can replicate)
- Verbose setup instructions (basics mastered)

**Writing Style:**

- Bullet points over paragraphs
- Code over prose
- Commands over explanations
- Technical notes only, no fluff

## Mid-Course Test Requirements

**Component Breakdown:**

1. **Data Ingestion (35 pts)**: Git workflow + Python pipelines + Docker PostgreSQL
2. **Transformation (40 pts)**: Multi-layer dbt models + incremental + custom macros + ERD
3. **CI/CD (5 pts)**: GitHub Actions with automated checks
4. **Extra Features (20 pts)**: Optional advanced implementations

**Success Criteria:** 70+ points (pass: 50+)

**Full Details:** See `docs/goal/midcourse_test_criteria.md`

## Code Style Preferences

**Python:**

- Type hints where useful
- Error handling without verbosity
- Functional over OOP for simple scripts
- Clear variable names, minimal comments

**SQL/dbt:**

- Clean, readable transformations
- Business logic in intermediate layer
- Marts for final analytics
- Tests co-located with models

**Git:**

- Meaningful commit messages
- Feature branches for all work
- PRs with technical context only
- Keep history clean

## Data Modeling Strategy

**Approach:**

- Multi-entity models (facts + dimensions)
- Dimensional modeling (star schema)
- Three-layer architecture (staging → intermediate → mart)
- Analytics-ready for business questions

**Business Analysis Focus:**

- Revenue analysis
- Customer segmentation
- Product performance
- Time-series trends

## Communication Preferences

**When Working with Claude:**

**Do:**

- Show code, not explanations
- Provide technical specs, not tutorials
- Give direct answers, not background
- Focus on implementation steps, not theory

**Don't:**

- Explain basics already understood
- Provide verbose documentation
- Write long-form educational content
- Repeat information unnecessarily

## Tech Stack

- **dbt**: SQL transformations + testing
- **Snowflake**: Cloud data warehouse
- **Python**: Pipeline scripts
- **Docker**: PostgreSQL containerization
- **GitHub Actions**: CI/CD automation

---

**Philosophy:** Ship working code, pass the test, build for real analysis. Everything else is noise.
