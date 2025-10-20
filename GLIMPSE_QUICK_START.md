# Glimpse Project — Quick Start Guide

**For:** New team members and collaborators
**Time to complete:** 15 minutes

---

## 🚀 Immediate Actions

### 1. Review Core Documents (10 min)
```bash
# Read these in order:
1. GLIMPSE_PROJECT_CHARTER.md      # Vision, mission, goals
2. INITIALIZATION_COMPLETE.md     # What's been done
3. PHASE1_DELIVERABLES.md         # What needs to be done
4. WORKFLOW_ROUTINES.md           # How we work
```

### 2. Set Up Environment (5 min)
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate   # Linux/Mac

# Verify installation
python --version  # Should be 3.12.9
pip list | grep -E "faiss|sentence-transformers|langchain"

# Run demo to verify everything works
python demo_rag_initialization.py
```

### 3. Join Communication Channels
- [ ] Add yourself to project Slack/Teams channel
- [ ] Join Monday 10am weekly sync (recurring invite)
- [ ] Access shared knowledge base (link TBD)
- [ ] Subscribe to advisory board updates (if applicable)

---

## 📋 Your Role

### Project Lead
**Focus:** Governance, stakeholders, decision-making
**First Tasks:**
- Schedule advisory board candidate calls
- Approve ethics protocol draft
- Set up stakeholder communication

### Technical Lead
**Focus:** RAG implementation, architecture, code review
**First Tasks:**
- Run and validate test suite: `pytest tests/test_rag_orbit.py -v`
- Review `src/rag_orbit/` implementation
- Set up encrypted data repository

### Ethics Coordinator
**Focus:** IRB preparation, compliance, data handling
**First Tasks:**
- Review institutional IRB requirements
- Draft research protocol v0.1
- Prepare consent form template

### Data Steward
**Focus:** Data collection, validation, provenance
**First Tasks:**
- Review data handling protocols
- Set up provenance tracking workflow
- Plan pilot data collection (Week 4-6)

### Researcher
**Focus:** Literature review, experiments, analysis
**First Tasks:**
- Set up reference manager (Zotero)
- Join Tuesday 11am literature sessions
- Start cognitive neuroscience paper review

---

## 🗓️ This Week's Schedule

### Monday 10:00 AM — Week Planning
- Review last week (if applicable)
- Plan this week's priorities
- Identify blockers

### Tuesday 11:00 AM — Literature Review
- Rotating presenter format
- 3-5 papers per session
- Update annotated bibliography

### Wednesday 2:00 PM — Technical Deep Dive
- Architecture and implementation
- Code review
- Problem-solving

### Friday 4:00 PM — Progress Review
- Week accomplishments
- Documentation updates
- Next week preview

---

## 🎯 Week 1 Priorities

### Everyone
- [ ] Read core documents
- [ ] Join communication channels
- [ ] Attend Monday planning sync
- [ ] Complete role-specific first tasks

### Team-Level Goals
- [ ] Validate RAG infrastructure (run tests and demo)
- [ ] Identify 2-3 advisory board candidates per position
- [ ] Start literature review process
- [ ] Begin ethics protocol draft

---

## 💻 Development Workflow

### Daily Routine
```bash
# Morning: Pull latest changes
git pull origin main

# During work: Regular commits
git add .
git commit -m "Descriptive message"
git push origin your-branch

# Evening: Update progress
# Add entry to PHASE1_DELIVERABLES.md
# Post async update in channel
```

### Code Standards
- **Style:** Black formatting, Ruff linting
- **Types:** Mypy strict mode, full type hints
- **Tests:** Pytest, >80% coverage required
- **Docs:** Google-style docstrings

### Pull Request Process
1. Create feature branch: `git checkout -b feature/your-feature`
2. Write code with tests
3. Run: `pytest tests/ -v` (all must pass)
4. Format: `black src/ tests/` and `ruff check src/ tests/`
5. Create PR with description
6. Wait for review (24-hour turnaround)
7. Address feedback and merge

---

## 🧪 Testing Your Work

### Run All Tests
```bash
# Full test suite
pytest tests/ -v --cov=src --cov-report=html

# Specific module
pytest tests/test_rag_orbit.py -v

# View coverage report
open htmlcov/index.html  # or start htmlcov/index.html on Windows
```

### Run Demo
```bash
# End-to-end demonstration
python demo_rag_initialization.py

# Check output
cat results/rag_initialization_provenance.json
```

### Validate Code Quality
```bash
# Type checking
mypy src/ --strict

# Linting
ruff check src/ tests/

# Formatting
black --check src/ tests/
```

---

## 📚 Key Concepts

### Integrated Cognition
Engagement across empirical, experiential, and conceptual domains using inherent human cognitive and sensory capacities.

### RAG Orbit
Our RAG system with:
- **Chunking:** Document segmentation with metadata
- **Embeddings:** Semantic vector representations
- **Retrieval:** FAISS similarity search
- **Provenance:** Complete audit trail (SHA-256)

### Data Categories
- **Empirical:** Observable, measurable phenomena
- **Experiential:** Subjective, first-person reports
- **Mixed:** Integration of both modalities

### Provenance Tracking
Every operation recorded with checksums, timestamps, and lineage for complete reproducibility.

---

## 🆘 Getting Help

### Technical Issues
1. Check documentation in `src/rag_orbit/`
2. Review test cases in `tests/test_rag_orbit.py`
3. Ask in `#technical` channel
4. Escalate to Technical Lead if blocked >24 hours

### Process Questions
1. Check `WORKFLOW_ROUTINES.md`
2. Review `PHASE1_DELIVERABLES.md`
3. Ask in `#general` channel
4. Contact Project Lead

### Ethics/Compliance
1. Review `GLIMPSE_PROJECT_CHARTER.md` ethics section
2. Contact Ethics Coordinator directly
3. Never proceed if uncertain

---

## 🎓 Learning Resources

### RAG Systems
- FAISS documentation: https://github.com/facebookresearch/faiss
- Sentence Transformers: https://www.sbert.net/
- LangChain: https://python.langchain.com/

### Research Methods
- Cognitive Science Society: https://cognitivesciencesociety.org/
- Open Science Framework: https://osf.io/

### Ethics
- [Institution-specific IRB resources]
- Research ethics primers (to be added)

---

## ✅ Onboarding Checklist

### Day 1
- [ ] Read GLIMPSE_PROJECT_CHARTER.md
- [ ] Read INITIALIZATION_COMPLETE.md
- [ ] Set up development environment
- [ ] Run demo successfully
- [ ] Join communication channels

### Week 1
- [ ] Attend all scheduled meetings
- [ ] Complete role-specific first tasks
- [ ] Make first contribution (even if small)
- [ ] Meet with project lead 1-on-1

### Week 2
- [ ] Participate in literature review session
- [ ] Submit first pull request
- [ ] Provide feedback on documentation
- [ ] Identify one process improvement

---

## 🎯 Success Indicators

You'll know you're up to speed when you can:

- ✅ Explain the project vision and goals to someone else
- ✅ Run tests and demos without errors
- ✅ Navigate the codebase confidently
- ✅ Contribute to your area of responsibility
- ✅ Participate actively in team discussions
- ✅ Identify when to ask for help vs. solve independently

---

## 📞 Contact Information

**Project Lead:** [TBD]
**Technical Lead:** [TBD]
**Ethics Coordinator:** [TBD]
**Data Steward:** [TBD]

**Project Email:** glimpse-project@[institution].edu
**Slack/Teams:** [Channel links TBD]
**Shared Folder:** [Link TBD]

---

## 🚦 Next Steps

After completing this quick start:

1. **Attend Monday sync** — Get immediate priorities
2. **Review your role section** — Focus on specific tasks
3. **Make first contribution** — Even documentation updates help
4. **Ask questions** — Better to clarify than assume

**Welcome to the Glimpse project!** 🎉

---

**Document Version:** 1.0
**Last Updated:** 2025-01-19
**Questions?** Ask in #general channel
