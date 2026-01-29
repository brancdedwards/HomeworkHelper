const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Get available grammar categories
  async getCategories() {
    const response = await fetch(`${API_BASE_URL}/grammar/categories`);
    if (!response.ok) throw new Error('Failed to fetch categories');
    return response.json();
  },

  // Generate a practice session
  async createPracticeSession({ num_questions, category, difficulty = 'normal', style = 'default' }) {
    const response = await fetch(`${API_BASE_URL}/grammar/practice/session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        num_questions,
        category,
        difficulty,
        style,
      }),
    });

    if (!response.ok) throw new Error('Failed to create practice session');
    return response.json();
  },

  // Future: Submit attempt for tracking
  async submitAttempt(attemptData) {
    const response = await fetch(`${API_BASE_URL}/practice/attempts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(attemptData),
    });

    if (!response.ok) throw new Error('Failed to submit attempt');
    return response.json();
  },
};

export default api;
