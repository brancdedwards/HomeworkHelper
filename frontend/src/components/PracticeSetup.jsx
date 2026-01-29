import { useState, useEffect } from 'react';
import api from '../services/api';

function PracticeSetup({ onStartPractice, loading, setLoading }) {
  const [mode, setMode] = useState('random');
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('grammar');
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSubjects();
  }, []);

  useEffect(() => {
    if (selectedSubject) {
      loadCategories(selectedSubject);
    }
  }, [selectedSubject]);

  const loadSubjects = async () => {
    try {
      const data = await api.getSubjects();
      setSubjects(data.subjects || []);
    } catch (err) {
      setError('Failed to load subjects. Is the backend running?');
      console.error(err);
    }
  };

  const loadCategories = async (subject) => {
    try {
      const data = await api.getCategories(subject);
      setCategories(data.categories || []);
      setSelectedCategory(''); // Reset category when subject changes
    } catch (err) {
      setError('Failed to load categories. Is the backend running?');
      console.error(err);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const session = await api.createPracticeSession({
        subject: selectedSubject,
        num_questions: numQuestions,
        category: mode === 'category' ? selectedCategory : null,
      });

      onStartPractice(session);
    } catch (err) {
      setError('Failed to generate questions. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Configure Your Practice Session
        </h2>
        <p className="text-gray-600">
          Choose how you want to practice and click generate!
        </p>
      </div>

      {error && (
        <div className="bg-error-50 border-l-4 border-error-500 p-4 rounded">
          <p className="text-error-700 font-medium">{error}</p>
        </div>
      )}

      {/* Subject Selection */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          Choose Subject
        </label>
        <div className="grid grid-cols-2 gap-3">
          {subjects.map((subject) => (
            <button
              key={subject.key}
              onClick={() => setSelectedSubject(subject.key)}
              className={`p-4 rounded-lg border-2 transition-all ${
                selectedSubject === subject.key
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 hover:border-gray-300 text-gray-700'
              }`}
            >
              <div className="font-semibold">{subject.icon} {subject.display_name}</div>
              <div className="text-sm mt-1 opacity-75">
                {subject.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Mode Selection */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          Practice Mode
        </label>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => setMode('random')}
            className={`p-4 rounded-lg border-2 transition-all ${
              mode === 'random'
                ? 'border-primary-500 bg-primary-50 text-primary-700'
                : 'border-gray-200 hover:border-gray-300 text-gray-700'
            }`}
          >
            <div className="font-semibold">🎲 Random Mix</div>
            <div className="text-sm mt-1 opacity-75">
              Questions from all categories
            </div>
          </button>

          <button
            onClick={() => setMode('category')}
            className={`p-4 rounded-lg border-2 transition-all ${
              mode === 'category'
                ? 'border-primary-500 bg-primary-50 text-primary-700'
                : 'border-gray-200 hover:border-gray-300 text-gray-700'
            }`}
          >
            <div className="font-semibold">🎯 Choose Category</div>
            <div className="text-sm mt-1 opacity-75">
              Focus on specific topics
            </div>
          </button>
        </div>
      </div>

      {/* Category Selection */}
      {mode === 'category' && (
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Select Category
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:outline-none"
          >
            <option value="">Choose a category...</option>
            {categories.map((cat) => (
              <option key={cat.key} value={cat.key}>
                {cat.display_name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Number of Questions */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Number of Questions: <span className="text-primary-600">{numQuestions}</span>
        </label>
        <input
          type="range"
          min="1"
          max="10"
          value={numQuestions}
          onChange={(e) => setNumQuestions(parseInt(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>1</span>
          <span>10</span>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={loading || (mode === 'category' && !selectedCategory)}
        className="btn-primary w-full text-lg"
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Generating Questions...
          </span>
        ) : (
          '🔄 Generate Practice Session'
        )}
      </button>

      <div className="text-xs text-gray-500 text-center">
        💡 Tip: Start with fewer questions to warm up!
      </div>
    </div>
  );
}

export default PracticeSetup;
