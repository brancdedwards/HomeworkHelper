# 🎉 Topic Import System - Ready to Use!

## What I Built For You

A complete AI-powered pipeline to import grammar topics into your app with quality controls and review process.

## 📦 What's Included

### 1. **Import Scripts** (`tools/` directory)
- `import_wizard.py` - Interactive wizard (easiest option!)
- `import_topics.py` - Generate metadata from CSV
- `review_topics.py` - Review generated topics with nice formatting
- `import_to_db.py` - Import approved topics to database

### 2. **Data Files** (`data/imports/` directory)
- `grammar_topics_template.csv` - Template for creating topic lists
- `starter_topics.csv` - 16 ready-to-use 5th grade topics

### 3. **Documentation**
- `TOPIC_IMPORT_GUIDE.md` - Quick start guide
- `tools/README.md` - Detailed documentation

## 🚀 Get Started Now (3 options)

### Option 1: Interactive Wizard (Recommended!)
```bash
python tools/import_wizard.py
```
Follow the prompts - it guides you through everything!

### Option 2: Import Starter Topics (Fastest!)
```bash
# Install rich library first
pip install rich

# Import 16 ready-made topics
python tools/import_topics.py data/imports/starter_topics.csv
python tools/review_topics.py
python tools/import_to_db.py
```

### Option 3: Manual Process
```bash
# 1. Create your CSV
cp data/imports/grammar_topics_template.csv data/imports/my_topics.csv
# Edit my_topics.csv

# 2. Generate
python tools/import_topics.py data/imports/my_topics.csv

# 3. Review
python tools/review_topics.py

# 4. Import
python tools/import_to_db.py
```

## 🎯 How It Works

```
Your CSV File
     ↓
[AI Generation] ← Claude API with strict guardrails
     ↓
topics_review.json (you review this)
     ↓
[Your Approval]
     ↓
Database ← Topics ready for practice!
```

## 🛡️ Quality Controls Built-In

1. **Schema Validation** - Pydantic models ensure correct structure
2. **Category Validation** - Only accepts your 8 valid categories
3. **Self-Validation** - AI checks its own output
4. **Human Review** - You approve before import
5. **Duplicate Detection** - Won't import duplicates
6. **Low Temperature (0.3)** - More consistent output

## 📝 Starter Topics Included

The `starter_topics.csv` includes 16 common 5th grade topics:
- Subject-verb agreement
- Past/present perfect tense
- Progressive tenses
- Comma usage (series, introductory phrases)
- Coordinating/subordinating conjunctions
- Pronouns (relative, reflexive)
- Homophones
- Proper nouns
- Quotation marks & apostrophes
- Run-ons & fragments

## 🔄 Weekly Workflow

1. **Monday**: Newsletter arrives
2. **Extract topics** from "What We're Learning" section
3. **Create CSV**: `topics_2025_01_26.csv`
4. **Run wizard**: `python tools/import_wizard.py`
5. **Practice**: Your son uses fresh, relevant topics all week!

## 📊 What Gets Generated

For each topic name you provide, Claude generates:

| Field | Description | Example |
|-------|-------------|---------|
| **name** | Topic name | "subject-verb agreement" |
| **category** | One of 8 categories | "Grammar Mechanics" |
| **prompt_template** | Question generation template | "Choose the verb that agrees with {subject}..." |
| **example** | Full example Q&A | "Question: The dogs ___ in the park.\nAnswer: run\nExplanation: Plural subject needs plural verb" |
| **grade_level** | Target grade | "5th grade" |

## 🎨 Review Interface

The review script (`review_topics.py`) shows:
- Clean summary table
- Detailed view with formatting
- Approve/reject workflow

Uses the `rich` library for beautiful terminal output!

## 💡 Pro Tips

1. **Start with starter topics** - Import those first to test the system
2. **Batch by week** - Create one CSV per newsletter
3. **Use notes field** - Track context (test dates, difficulty, etc.)
4. **Review carefully** - Remember the "elephant" issue - AI makes mistakes!
5. **Keep sources** - Track newsletter dates for future reference

## 🔧 Technical Details

### File Locations
```
/data/imports/
  ├── *.csv                    # Your topic lists
  ├── topics_review.json       # Generated metadata (review this!)
  └── topics_review_*.json     # Archived reviews

/tools/
  ├── import_wizard.py         # 🧙 Interactive wizard
  ├── import_topics.py         # Step 1: Generate
  ├── review_topics.py         # Step 2: Review
  ├── import_to_db.py          # Step 3: Import
  └── README.md                # Detailed docs
```

### API Usage
- Model: `claude-3-5-haiku-20241022` (from your settings)
- Temperature: `0.3` (low for consistency)
- Max tokens: `2000` per topic
- Cost: ~16 topics ≈ $0.05 (very cheap!)

### Database Schema
Topics are inserted with:
- `name`, `category`, `prompt_template`, `example`
- `subject` = "grammar"
- `active` = 1
- Normalized category (spaces → underscores)

## 🆘 Troubleshooting

**"rich not found"**
```bash
pip install rich
```

**"API key error"**
```bash
cat .env | grep CLAUDE_API_KEY
```

**"Database error"**
```bash
ls -la homework_helper.db
```

**"Duplicates in dropdown"**
- Fixed! Clear browser cache

## 📈 Next Steps

1. **Try it now**: Run `python tools/import_wizard.py`
2. **Import starter topics**: Get 16 topics ready
3. **Test the app**: Generate practice session
4. **Weekly routine**: Import new topics from newsletters
5. **Future**: OCR integration for cheat sheets (Phase 2!)

## 🎓 What This Solves

✅ Stale topics in database
✅ Manual data entry
✅ Inconsistent formatting
✅ Missing metadata
✅ No quality control
✅ Tedious import process

## 🚀 Ready to Go!

Everything is set up. Just run:
```bash
python tools/import_wizard.py
```

Or for a quick test:
```bash
pip install rich
python tools/import_topics.py data/imports/starter_topics.csv
```

---

**Questions?** Check `TOPIC_IMPORT_GUIDE.md` or `tools/README.md`
