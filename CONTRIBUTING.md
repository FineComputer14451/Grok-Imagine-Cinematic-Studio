# Contributing to Grok Imagine Cinematic Studio

Thank you for your interest in contributing to **Grok Imagine Cinematic Studio**!  
We’re building the most advanced multi-agent cinematic production system for **Grok Build 1.0.5+**, **Grok 4.6** (cinematic + coding default), optional **Grok 4.3** (1M), and **Grok Imagine Video 1.0/1.5** — every contribution helps push the boundaries of AI-generated cinema.

> [!NOTE]
> This is an **independent community project**. It is **not affiliated with, endorsed by, sponsored by, or officially connected to xAI**. Contributions, issues, and docs must not claim official xAI partnership. See [DISCLAIMER.md](DISCLAIMER.md).

## 🌟 Ways to Contribute

### 1. Suggest New Specialist Agents
We love new agents! Examples of great additions:
- **Lighting Director**
- **VFX & Particle Specialist**
- **Music Composer Agent**
- **Audience Test Analyst**
- **Style Transfer Agent**

**How to propose a new agent**:
1. Open an issue with the title: `New Agent Proposal: [Agent Name]`
2. Include:
   - Role description (1-2 sentences)
   - Key responsibilities
   - How it would integrate with existing agents (especially Studio Director and Quality Assurance Guardian)
   - Example output format

### 2. Improve Existing Agents
- Refine prompt templates
- Add new variables to bibles
- Improve Self-Evaluation criteria
- Enhance Failure Recovery logic
- Optimize quota prediction

### 3. Enhance the Master Prompt
- Better collaboration protocols
- New mandatory rules
- Improved activation responses
- Additional cinematic best practices

### 4. Documentation & Examples
- Add more example Production Bibles
- Create tutorial videos / walkthroughs
- Improve README clarity
- Translate documentation

### 5. Bug Reports & Feedback
Found an issue with consistency, prompt quality, or workflow?  
Please open an issue with:
- Steps to reproduce
- Expected vs actual behavior
- Grok version used
- Any generated output (if relevant)

## 📋 Contribution Process

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the style guide below
4. **Test** your changes (run the master prompt with a sample project)
5. **Submit a Pull Request** with a clear description

## ✍️ Style Guide for New Agents

All agents must follow the **v3.1 structure**:

```markdown
## **Agent Name vX.X**

**Role**: One-sentence description.

**New vX.X Core Protocols**:
- Studio State Protocol integration
- Self-Evaluation Layer (mandatory 5-metric scoring)
- Versioning + Changelog
- Failure Recovery Protocol

**You [main action]**:
- Bullet list of core responsibilities

**Collaboration**:
- How this agent works with Studio Director, Quality Assurance Guardian, etc.

**Self-Evaluation (this response)**: ... (example scores)
```

**Mandatory elements**:
- Must reference `studio_state.json`
- Must end with a **Self-Evaluation** block
- Must use clear, professional, cinematic language
- Must be compatible with the **Quality Assurance Guardian** 10-point checklist

## 🧪 Testing Your Contribution

Before submitting a PR:
1. Copy the updated `MASTER_PROMPT.md` into Grok (Grok 4.5 default)
2. Activate: `"Activate Grok Imagine Cinematic Studio v3.11.0"`
3. Test with at least one full project
4. Confirm the **Quality Assurance Guardian** gives a clean ✅ GO

## 💬 Communication

- Be respectful and constructive
- Use clear, cinematic language in issues and PRs
- We value bold ideas that improve emotional impact and technical excellence

## 🏆 Recognition

All contributors will be listed in the `CONTRIBUTORS.md` file (coming soon) and mentioned in release notes.

---

**Let’s make cinema together.**  
Every great film starts with a single frame — and every great agent starts with a single idea.

Thank you for helping push AI cinematic storytelling forward! 🎥

— The Grok Imagine Cinematic Studio Team
