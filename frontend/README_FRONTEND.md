# Grammar Practice React Frontend

A modern, kid-friendly React frontend for the Grammar Practice app, powered by Anthropic Claude API.

## 🎨 Features

- **Clean, Modern UI** - Built with React + Tailwind CSS
- **Two Practice Modes** - Random mix or category-specific questions
- **Interactive Questions** - Multiple choice with instant feedback
- **Progress Tracking** - Visual progress bar and score tracking
- **Responsive Design** - Works on desktop and mobile
- **Smooth Animations** - Engaging user experience

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at **http://localhost:3000**

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── PracticeSetup.jsx     # Configure practice session
│   │   └── QuestionDisplay.jsx   # Show questions & handle answers
│   ├── services/
│   │   └── api.js                # API integration
│   ├── App.jsx                   # Main app component
│   ├── index.css                 # Tailwind styles
│   └── main.jsx                  # Entry point
├── vite.config.js                # Vite configuration
└── tailwind.config.js            # Tailwind configuration
```

## 🎯 How to Use

1. **Start Backend** - Make sure the FastAPI server is running
2. **Start Frontend** - Run `npm run dev`
3. **Choose Mode** - Select random or category-specific practice
4. **Set Questions** - Use slider to choose 1-10 questions
5. **Generate** - Click to create your practice session
6. **Practice** - Answer questions and get instant feedback!

## 🎨 Customization

### Change Colors

Edit `tailwind.config.js` to customize the color scheme:

```js
theme: {
  extend: {
    colors: {
      primary: { /* your colors */ },
      success: { /* your colors */ },
      // ...
    }
  }
}
```

### API Endpoint

Update `src/services/api.js` if your backend runs on a different port:

```js
const API_BASE_URL = 'http://localhost:YOUR_PORT';
```

## 📦 Building for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

## 🔧 Technologies Used

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **FastAPI** - Backend API
- **Anthropic Claude** - AI question generation

## 🐛 Troubleshooting

**Frontend can't connect to backend:**
- Make sure the backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify the API_BASE_URL in `src/services/api.js`

**Tailwind styles not working:**
- Run `npm install` again
- Check that `tailwind.config.js` and `postcss.config.js` exist
- Restart the dev server

## 📝 Future Enhancements

- [ ] Hints system for wrong answers
- [ ] Progress analytics dashboard
- [ ] User authentication
- [ ] Save practice history
- [ ] Dark mode support
- [ ] Print/export results

## 🤝 Contributing

This is a personal learning project, but suggestions are welcome!

---

Built with ❤️ using React + Anthropic Claude
