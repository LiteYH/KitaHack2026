# 🚀 BossolutionAI

**AI-Powered Marketing and Advertisement Platform for SMEs**

Automate content creation, analyze competitors, optimize campaigns, and boost your ROI — all powered by AI.

![Next.js](https://img.shields.io/badge/Next.js-16.1.6-black?style=flat&logo=next.js)
![React](https://img.shields.io/badge/React-19.2.3-blue?style=flat&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.119.0-009688?style=flat&logo=fastapi)
![Firebase](https://img.shields.io/badge/Firebase-10.8.0-orange?style=flat&logo=firebase)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7.3-blue?style=flat&logo=typescript)
![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=flat&logo=python)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🎯 Core Features

#### 1. **Content Planning** 📝
- AI-powered content generation using Google Gemini
- Content calendar with scheduling
- Topic suggestions based on trends
- Multi-platform content adaptation

#### 2. **Competitor Intelligence** 🔍
- Monitor competitor social media activity
- Scrape and analyze competitor content
- Get actionable insights and recommendations
- Track competitor performance metrics

#### 3. **Publishing** 📤
- Schedule posts across multiple platforms
- One-click publishing to Facebook, Instagram, LinkedIn, Twitter
- Post preview before publishing
- Bulk scheduling capabilities

#### 4. **Campaign & Optimization** 🎯
- Create and manage marketing campaigns
- Set budgets and KPIs
- A/B testing functionality
- Real-time optimization suggestions

#### 5. **ROI Dashboard** 📊
- Real-time performance metrics
- Revenue tracking
- ROI calculations
- Custom reports and analytics

#### 6. **Continuous Monitoring** 👁️
- Keyword and brand mention monitoring
- Social listening across platforms
- Sentiment analysis
- Automated alerts

### 🔐 Authentication
- Email/Password authentication
- Google Sign In integration
- Password reset functionality
- Protected routes and session management

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16.1.6 (App Router)
- **UI Library**: React 19.2.3
- **Language**: TypeScript 5.7.3
- **Styling**: Tailwind CSS 4.0.3
- **Components**: Radix UI
- **Font**: Space Grotesk
- **Authentication**: Firebase SDK 10.8.0
- **State Management**: React Context API

### Backend
- **Framework**: FastAPI 0.119.0
- **Language**: Python 3.10+
- **Validation**: Pydantic 2.12.3
- **Server**: Uvicorn 0.37.0
- **Authentication**: Firebase Admin SDK 6.5.0+
- **AI**: LangChain + Google Generative AI

### Database & Services
- **Authentication**: Firebase Authentication
- **Database**: Firestore (NoSQL)
- **Storage**: Firebase Storage
- **AI**: Google Gemini API
- **Social APIs**: Facebook, Instagram, LinkedIn, Twitter

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- Firebase account

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/bossolutionai.git
cd bossolutionai
```

2. **Install frontend dependencies**
```bash
cd frontend
npm install
```

3. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure Firebase**
- See [FIREBASE_SETUP.md](./FIREBASE_SETUP.md) for detailed instructions
- Enable Email/Password and Google authentication
- Create Firestore database
- Generate service account for backend

5. **Set up environment variables**

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**Backend** (`backend/.env`):
```env
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="your_private_key"
FIREBASE_CLIENT_EMAIL=your_client_email
FIREBASE_CLIENT_ID=your_client_id
GOOGLE_API_KEY=your_gemini_api_key
```

6. **Run the application**

**Terminal 1 - Backend**:
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

7. **Access the application**
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📁 Project Structure

```
bossolutionai/
├── frontend/                   # Next.js frontend application
│   ├── app/                    # App router pages
│   │   ├── auth/               # Authentication pages
│   │   │   ├── signin/
│   │   │   ├── signup/
│   │   │   └── forgot-password/
│   │   ├── chat/               # Main dashboard (protected)
│   │   ├── layout.tsx          # Root layout with AuthProvider
│   │   └── page.tsx            # Welcome page
│   ├── components/             # React components
│   │   ├── auth/               # Auth components
│   │   ├── chat/               # Chat interface
│   │   ├── welcome/            # Welcome page components
│   │   └── ui/                 # Reusable UI components
│   ├── contexts/               # React contexts
│   │   └── AuthContext.tsx    # Authentication context
│   ├── lib/                    # Utilities and configs
│   │   └── firebase.ts         # Firebase client config
│   └── package.json
│
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── routers/    # API route handlers
│   │   │           └── items.py
│   │   ├── core/               # Core configurations
│   │   │   ├── config.py       # Settings
│   │   │   ├── firebase.py     # Firebase Admin SDK
│   │   │   └── auth.py         # Auth middleware
│   │   ├── schemas/            # Pydantic models
│   │   └── services/           # Business logic
│   ├── main.py                 # FastAPI application
│   └── requirements.txt
│
├── QUICKSTART.md               # Quick start guide
├── FIREBASE_SETUP.md           # Firebase setup instructions
├── ARCHITECTURE.md             # System architecture
└── README.md                   # This file
```

---

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - Get started in 5 minutes
- **[FIREBASE_SETUP.md](./FIREBASE_SETUP.md)** - Complete Firebase setup guide
- **[FIREBASE_INTEGRATION_SUMMARY.md](./FIREBASE_INTEGRATION_SUMMARY.md)** - Integration details
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Visual system architecture
- **[backend/README.md](./backend/README.md)** - Backend API documentation
- **[backend/STRUCTURE.md](./backend/STRUCTURE.md)** - Backend folder structure

---

## 🖼️ Screenshots

### Welcome Page
Beautiful Aurora background with gradient effects and animations.

### Authentication
- Clean sign in/sign up forms
- Google Sign In integration
- Password reset functionality

### Dashboard
- 6 feature cards for easy navigation
- Chat-style interface
- Real-time updates

*(Add actual screenshots here)*

---

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run linter
```

### Backend Development
```bash
cd backend
uvicorn main:app --reload    # Start with hot reload
pytest                       # Run tests
python -m black .            # Format code
```

### Code Style
- **Frontend**: ESLint + Prettier
- **Backend**: Black + Flake8
- **Commits**: Conventional Commits

---

## 🌟 Features Roadmap

### Phase 1: Foundation ✅
- [x] Authentication system
- [x] Protected routes
- [x] Firebase integration
- [x] Basic UI/UX

### Phase 2: Core Features 🚧
- [ ] Content Planning implementation
- [ ] Competitor Intelligence
- [ ] Publishing scheduler
- [ ] Campaign management
- [ ] ROI Dashboard
- [ ] Monitoring system

### Phase 3: Advanced Features 📋
- [ ] Multi-user collaboration
- [ ] Advanced analytics
- [ ] Custom reports
- [ ] White-label options
- [ ] Mobile app

### Phase 4: Enterprise 🔮
- [ ] Team management
- [ ] SSO integration
- [ ] Advanced security
- [ ] Custom integrations
- [ ] Dedicated support

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style
- Write tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 🐛 Bug Reports & Feature Requests

Please use GitHub Issues to report bugs or request features:
- **Bug Report**: Describe the issue, steps to reproduce, expected vs actual behavior
- **Feature Request**: Describe the feature, use case, and potential implementation

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**BossolutionAI** - Built for SMEs by developers who understand marketing challenges.

---

## 🙏 Acknowledgments

- **Firebase** - Authentication and database
- **Google Gemini** - AI content generation
- **Vercel** - Deployment platform
- **Next.js** - React framework
- **FastAPI** - Python web framework
- **Tailwind CSS** - Styling framework
- **Radix UI** - Component library

---

## 📞 Support

- **Documentation**: Check the `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/bossolutionai/issues)
- **Email**: support@bossolutionai.com

---

## 🔗 Links

- **Website**: https://bossolutionai.com
- **Documentation**: https://docs.bossolutionai.com
- **API Reference**: http://localhost:8000/docs (when running locally)

---

**Made with ❤️ for SMEs worldwide**

⭐ Star this repo if you find it helpful!
