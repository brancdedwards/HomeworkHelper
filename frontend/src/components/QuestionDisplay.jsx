import { useState } from 'react';

function QuestionDisplay({ session, onReset }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState({});
  const [selectedOptions, setSelectedOptions] = useState({});

  const currentQuestion = session.questions[currentIndex];
  const isLastQuestion = currentIndex === session.questions.length - 1;
  const totalCorrect = Object.values(answers).filter((a) => a).length;

  const handleOptionSelect = (option) => {
    if (submitted[currentIndex]) return; // Already submitted

    setSelectedOptions({
      ...selectedOptions,
      [currentIndex]: option,
    });
  };

  const handleSubmit = () => {
    const selectedOption = selectedOptions[currentIndex];
    if (!selectedOption) return;

    const isCorrect = selectedOption === currentQuestion.correct_answer;

    setAnswers({
      ...answers,
      [currentIndex]: isCorrect,
    });

    setSubmitted({
      ...submitted,
      [currentIndex]: true,
    });
  };

  const handleNext = () => {
    if (currentIndex < session.questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const isAnswered = submitted[currentIndex];
  const selectedOption = selectedOptions[currentIndex];
  const isCurrentCorrect = answers[currentIndex];

  const getOptionClass = (option) => {
    const baseClass = 'option-button';

    if (!isAnswered) {
      // Not submitted yet
      return `${baseClass} ${
        selectedOption === option ? 'option-selected' : 'option-default'
      }`;
    }

    // Submitted - show correct/incorrect
    if (option === currentQuestion.correct_answer) {
      return `${baseClass} option-correct`;
    }

    if (selectedOption === option && !isCurrentCorrect) {
      return `${baseClass} option-incorrect`;
    }

    return `${baseClass} option-default opacity-50`;
  };

  return (
    <div className="space-y-6">
      {/* Progress Bar */}
      <div className="card">
        <div className="flex justify-between items-center mb-3">
          <span className="text-sm font-semibold text-gray-700">
            Question {currentIndex + 1} of {session.questions.length}
          </span>
          <span className="text-sm text-gray-600">
            Score: {totalCorrect} / {Object.keys(answers).length}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{
              width: `${((currentIndex + 1) / session.questions.length) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Question Card */}
      <div className="card">
        {/* Category Badge */}
        <div className="mb-4">
          <span className="inline-block px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
            {currentQuestion.category.replace(/_/g, ' ')}
          </span>
          <span className="inline-block ml-2 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
            {currentQuestion.topic}
          </span>
        </div>

        {/* Question Text */}
        <h3 className="text-2xl font-bold text-gray-800 mb-6">
          {currentQuestion.question}
        </h3>

        {/* Options */}
        <div className="space-y-3">
          {currentQuestion.options.map((option, idx) => (
            <button
              key={idx}
              onClick={() => handleOptionSelect(option)}
              disabled={isAnswered}
              className={getOptionClass(option)}
            >
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white border-2 border-current flex items-center justify-center mr-3 font-bold">
                  {String.fromCharCode(65 + idx)}
                </div>
                <div className="flex-1 text-left">
                  <div className="font-medium">{option}</div>
                </div>
                {isAnswered && option === currentQuestion.correct_answer && (
                  <span className="ml-2 text-success-600">✓</span>
                )}
                {isAnswered &&
                  selectedOption === option &&
                  !isCurrentCorrect && (
                    <span className="ml-2 text-error-600">✗</span>
                  )}
              </div>
            </button>
          ))}
        </div>

        {/* Feedback */}
        {isAnswered && (
          <div
            className={`mt-6 p-4 rounded-lg ${
              isCurrentCorrect
                ? 'bg-success-50 border border-success-200'
                : 'bg-warning-50 border border-warning-200'
            }`}
          >
            <div className="flex items-start">
              <span className="text-2xl mr-3">
                {isCurrentCorrect ? '🎉' : '💡'}
              </span>
              <div>
                <h4
                  className={`font-bold mb-1 ${
                    isCurrentCorrect ? 'text-success-700' : 'text-warning-700'
                  }`}
                >
                  {isCurrentCorrect ? 'Correct!' : 'Not quite!'}
                </h4>
                <p className="text-gray-700">{currentQuestion.explanation}</p>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            className="btn-secondary flex-1 disabled:opacity-30"
          >
            ← Previous
          </button>

          {!isAnswered ? (
            <button
              onClick={handleSubmit}
              disabled={!selectedOption}
              className="btn-primary flex-1"
            >
              Check Answer
            </button>
          ) : !isLastQuestion ? (
            <button onClick={handleNext} className="btn-primary flex-1">
              Next Question →
            </button>
          ) : (
            <button onClick={onReset} className="btn-primary flex-1">
              🎯 New Session
            </button>
          )}
        </div>
      </div>

      {/* Summary (shown after last question) */}
      {isLastQuestion && isAnswered && (
        <div className="card bg-gradient-to-r from-primary-50 to-purple-50">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">
            Session Complete! 🎊
          </h3>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600">
                {session.questions.length}
              </div>
              <div className="text-sm text-gray-600">Total Questions</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-success-600">
                {totalCorrect}
              </div>
              <div className="text-sm text-gray-600">Correct</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {Math.round((totalCorrect / session.questions.length) * 100)}%
              </div>
              <div className="text-sm text-gray-600">Score</div>
            </div>
          </div>
          <p className="text-gray-700 text-center">
            {totalCorrect === session.questions.length
              ? '🌟 Perfect score! You\'re a grammar champion!'
              : totalCorrect >= session.questions.length * 0.7
              ? '👏 Great job! Keep practicing!'
              : '💪 Good effort! Practice makes perfect!'}
          </p>
        </div>
      )}
    </div>
  );
}

export default QuestionDisplay;
