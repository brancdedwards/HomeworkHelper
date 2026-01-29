# Topic Import Tools

This directory contains tools for importing grammar topics into the database with AI-generated metadata.

## 📋 Process Overview

1. **Create CSV** - List topics you want to add
2. **Generate Metadata** - AI generates category, templates, examples
3. **Review** - You review and edit the generated metadata
4. **Import** - Load approved topics into database

## 🚀 Quick Start

### Step 1: Create Your Topics CSV

Copy the template:
```bash
cp data/imports/grammar_topics_template.csv data/imports/my_topics.csv
```

Edit `my_topics.csv` and add your topics:
```csv
topic_name,source,notes
subject-verb agreement,newsletter 2025-01-26,Example: The dog runs vs dogs run
past perfect tense,newsletter 2025-01-26,Had + past participle
comma splices,cheat sheet,Two independent clauses incorrectly joined
```

### Step 2: Generate Metadata

Run the generation script:
```bash
python tools/import_topics.py data/imports/my_topics.csv
```

This will:
- Call Claude API for each topic
- Generate category, prompt template, and example
- Save results to `data/imports/topics_review.json`
- Show progress and any errors

### Step 3: Review Generated Metadata

View the generated metadata:
```bash
python tools/review_topics.py
```

This shows:
- Summary table of all topics
- Detailed view of each topic
- Option to approve or edit

**Optional:** Edit `data/imports/topics_review.json` manually if needed.

### Step 4: Import to Database

Import approved topics:
```bash
python tools/import_to_db.py
```

This will:
- Insert topics into the database
- Skip duplicates
- Archive the review file
- Show import summary

## 📁 File Structure

```
data/imports/
  ├── grammar_topics_template.csv    # Template for creating topic lists
  ├── my_topics.csv                  # Your topic list (you create this)
  ├── topics_review.json             # Generated metadata (review before import)
  └── topics_review_*.json           # Archived review files

tools/
  ├── import_topics.py               # Step 2: Generate metadata
  ├── review_topics.py               # Step 3: Review metadata
  ├── import_to_db.py                # Step 4: Import to database
  └── README.md                      # This file
```

## 🎯 Topic Metadata Structure

Each topic includes:

- **name**: The grammar topic name (e.g., "subject-verb agreement")
- **category**: One of 8 valid categories (Grammar Mechanics, Parts Of Speech, etc.)
- **prompt_template**: Template for generating questions with placeholders
- **example**: Sample question with answer and explanation
- **grade_level**: Target grade (default: 5th grade)
- **source**: Where the topic came from (newsletter date, cheat sheet, etc.)

## 🛡️ Quality Guardrails

The import pipeline includes several quality controls:

1. **Structured Output**: Pydantic models enforce schema validation
2. **Category Validation**: Only accepts valid categories from database
3. **Self-Validation**: AI checks its own output for quality
4. **Human Review**: You review before import
5. **Duplicate Detection**: Skips topics already in database
6. **Low Temperature**: AI uses temperature=0.3 for consistency

## 💡 Tips

- **Start small**: Try 5-10 topics first to test the workflow
- **Be specific**: Add notes in CSV to guide metadata generation
- **Review carefully**: Check examples for accuracy (remember the "elephant" issue!)
- **Keep sources**: Track newsletter dates for future reference
- **Iterate**: If metadata is wrong, regenerate or edit JSON manually

## 🔧 Troubleshooting

**API Key Error:**
```bash
# Make sure .env has CLAUDE_API_KEY set
cat .env | grep CLAUDE_API_KEY
```

**Import Errors:**
```bash
# Check database path in settings
python -c "from backend.app.core.settings import settings; print(settings.DB_PATH)"
```

**JSON Validation:**
```bash
# Validate JSON format
python -m json.tool data/imports/topics_review.json
```

## 📝 Example Workflow

```bash
# 1. Create CSV with 10 topics from latest newsletter
vim data/imports/topics_2025_01_26.csv

# 2. Generate metadata
python tools/import_topics.py data/imports/topics_2025_01_26.csv

# 3. Review
python tools/review_topics.py
# Look good? Approve!

# 4. Import
python tools/import_to_db.py
# ✅ 10 topics added!

# 5. Test in the app
# Go to http://localhost:3000 and select a category
```

## 🚀 Future Enhancements

- [ ] Web-based admin panel (Option C)
- [ ] OCR integration for cheat sheets
- [ ] Newsletter parser for automatic topic extraction
- [ ] Bulk edit interface
- [ ] Topic validation tests
- [ ] Automatic categorization suggestions
