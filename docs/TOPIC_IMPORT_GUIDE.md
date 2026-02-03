# 📚 Quick Topic Import Guide

Get new grammar topics into your app in 4 easy steps!

## ⚡ Quick Start (5 minutes)

I've created a starter file with 16 common 5th grade topics. To import them:

```bash
# 1. Install rich library (one-time)
pip install rich

# 2. Generate metadata from starter topics
python tools/import_topics.py data/imports/starter_topics.csv

# 3. Review the generated topics
python tools/review_topics.py

# 4. Import to database
python tools/import_to_db.py
```

Done! Your app now has 16 fresh topics ready for practice.

## 📝 Adding Your Own Topics

### From Weekly Newsletters

1. Create a new CSV file:
```bash
cp data/imports/grammar_topics_template.csv data/imports/topics_2025_01_26.csv
```

2. Edit the CSV and add topics from this week's newsletter:
```csv
topic_name,source,notes
past perfect tense,newsletter 2025-01-26,Had + past participle
subordinating conjunctions,newsletter 2025-01-26,because/although/since
comma splices,newsletter 2025-01-26,Common error to avoid
```

3. Run the import process (same 4 steps above)

### Best Practices

✅ **DO:**
- Add 5-10 topics at a time
- Include notes from the newsletter/cheat sheet
- Track the source (newsletter date)
- Review before importing

❌ **DON'T:**
- Import topics already in the database (they'll be skipped)
- Rush through review - check for accuracy!
- Forget to activate your venv first

## 🎯 What Gets Generated

For each topic, Claude generates:

| Field | Example |
|-------|---------|
| **Category** | Parts Of Speech |
| **Prompt Template** | "Choose the correct {part_of_speech} to complete the sentence: {sentence}" |
| **Example** | "Question: Which pronoun fits? ___ went to the store.\nAnswer: He\nExplanation: 'He' is a subject pronoun." |
| **Grade Level** | 5th grade |

## 🔍 Reviewing Topics

The review step shows:
- Summary table of all topics
- Category assignments
- Full examples with answers
- Grade level

**If something looks wrong:**
1. Edit `data/imports/topics_review.json` manually, OR
2. Regenerate by running import_topics.py again

## 📊 Workflow Example

```
Weekly Newsletter arrives
     ↓
Extract 8 grammar topics mentioned
     ↓
Create CSV: topics_2025_01_26.csv
     ↓
Run: python tools/import_topics.py data/imports/topics_2025_01_26.csv
     ↓
Review output - looks good!
     ↓
Run: python tools/import_to_db.py
     ↓
🎉 8 new topics ready for practice!
     ↓
Your son practices the exact topics from this week's lessons
```

## 🆘 Troubleshooting

**"File not found" error:**
```bash
# Make sure you're in the project root
cd /Users/brandonedwards/.claude-worktrees/HomeworkHelper/pedantic-moore
```

**"API key not found" error:**
```bash
# Check your .env file
cat .env | grep CLAUDE_API_KEY
```

**"Import failed" error:**
```bash
# Check database path
ls -la homework_helper.db
```

**Topics show as duplicates in dropdown:**
- This was fixed! Clear your browser cache and refresh

## 📈 Next Steps

After importing topics:

1. **Test in the app** - Go to http://localhost:3000
2. **Generate practice session** - Select a category with new topics
3. **Check question quality** - Make sure examples are accurate
4. **Repeat weekly** - Keep topics fresh with each newsletter

## 🎓 Pro Tips

- Keep a running CSV of topics throughout the month
- Import weekly after newsletter arrives
- Archive old topics that are no longer being tested
- Use the notes field to track which test/quiz they're for

---

**Need help?** Check the detailed guide: `tools/README.md`
