import { useState } from 'react';
import PracticeSetup from './components/PracticeSetup';
import QuestionDisplay from './components/QuestionDisplay';

function App() {
  const [practiceSession, setPracticeSession] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleStartPractice = (session) => {
    setPracticeSession(session);
  };

  const handleReset = () => {
    setPracticeSession(null);
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">
            📘 Grammar Practice
          </h1>
          <p className="text-white/90 text-lg">
            Master grammar concepts with AI-powered questions
          </p>
        </header>

        <main>
          {!practiceSession ? (
            <PracticeSetup
              onStartPractice={handleStartPractice}
              loading={loading}
              setLoading={setLoading}
            />
          ) : (
            <QuestionDisplay
              session={practiceSession}
              onReset={handleReset}
            />
          )}
        </main>

        <footer className="text-center mt-12 text-white/70 text-sm">
          <p>Powered by Anthropic Claude • Built with React</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
