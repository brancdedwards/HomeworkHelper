-- Migration: Create question_history table for tracking generated questions across sessions
-- This prevents showing the same questions repeatedly and enables analytics

CREATE TABLE IF NOT EXISTS question_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,                    -- 'grammar', 'reading', etc.
    topic TEXT NOT NULL,                      -- Topic name from topics table
    category TEXT,                             -- Question category
    question_text TEXT NOT NULL,              -- Full question prompt
    question_hash TEXT UNIQUE NOT NULL,       -- SHA256 hash of normalized question
    correct_answer TEXT,                       -- The correct answer
    options_json TEXT,                        -- JSON array of all options
    explanation TEXT,                          -- Explanation text
    passage_text TEXT,                         -- For reading: the passage (NULL for grammar)

    -- Tracking fields
    times_shown INTEGER DEFAULT 0,            -- How many times shown to students
    last_shown_at TEXT,                        -- Timestamp of last use
    created_at TEXT DEFAULT (datetime('now')), -- When first generated

    -- Indexes for performance
    CONSTRAINT unique_question UNIQUE (question_hash)
);

-- Index for fast lookups when checking if question exists
CREATE INDEX IF NOT EXISTS idx_question_hash ON question_history(question_hash);

-- Index for cooldown queries (find questions not shown recently)
CREATE INDEX IF NOT EXISTS idx_last_shown ON question_history(subject, last_shown_at);

-- Index for subject/topic queries
CREATE INDEX IF NOT EXISTS idx_subject_topic ON question_history(subject, topic);
