const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Get available subjects
  async getSubjects() {
    const response = await fetch(`${API_BASE_URL}/subjects`);
    if (!response.ok) throw new Error('Failed to fetch subjects');
    return response.json();
  },

  // Get available categories for a subject
  async getCategories(subject = 'grammar') {
    const response = await fetch(`${API_BASE_URL}/subjects/${subject}/categories`);
    if (!response.ok) throw new Error('Failed to fetch categories');
    return response.json();
  },

  // Generate a practice session for a specific subject
  async createPracticeSession({ subject = 'grammar', num_questions, category, difficulty = 'normal', style = 'default' }) {
    const response = await fetch(`${API_BASE_URL}/subjects/${subject}/session`, {
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
