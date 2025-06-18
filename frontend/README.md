# Chatbot Frontend - Angular Application

This is the frontend web application for the AI-powered chatbot, built with Angular 19 and modern web technologies.

## 🌟 Features

- **Modern Chat Interface**: Clean, responsive design with real-time messaging
- **Angular 19**: Latest Angular framework with server-side rendering (SSR)
- **TypeScript**: Fully typed development experience
- **Real-time Communication**: Seamless API integration with the Flask backend
- **Mobile Responsive**: Works perfectly on all device sizes
- **Beautiful UI**: Modern chatbot interface with smooth animations

## 🚀 Quick Start

### Prerequisites
- Node.js 18.0 or higher
- npm 9.0 or higher
- Angular CLI (install with `npm install -g @angular/cli`)

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The application will be available at `http://localhost:4200`

## 📋 Available Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Start development server on port 4200 |
| `npm run build` | Build the app for production |
| `npm run watch` | Build with file watching for development |
| `npm test` | Run unit tests with Karma |
| `npm run serve:ssr` | Serve the SSR version |

## 🏗️ Project Structure

```
src/
├── app/
│   ├── chatbot/           # Main chatbot component
│   │   ├── chatbot.component.ts
│   │   ├── chatbot.component.html
│   │   └── chatbot.component.css
│   └── ...
├── styles.css             # Global styles
├── main.ts               # Application bootstrap
└── index.html            # Main HTML template
```

## 🔧 Configuration

### Backend Connection
The frontend connects to the backend API at `http://localhost:5001/api/chat`. Make sure the backend is running before starting the frontend.

### Environment Variables
- Development: Uses `http://localhost:5001` for API calls
- Production: Configure API URL in build settings

## 🎨 User Interface

The chatbot interface includes:
- Message input field with send button
- Chat history display
- Real-time message updates
- Loading indicators during API calls
- Error handling for network issues

## 🔄 API Integration

The frontend communicates with the Flask backend through RESTful API calls:
- **POST** `/api/chat` - Send messages and receive AI responses
- Automatic CORS handling
- Error handling and retry logic

## 🛠️ Development

### Adding New Features
1. Create new components in the `src/app/` directory
2. Update the routing if needed
3. Add new services for API communication
4. Test your changes with `npm test`

### Code Style
- Use TypeScript strict mode
- Follow Angular style guide
- Use consistent naming conventions
- Add proper type definitions

## 📦 Build & Deployment

```bash
# Production build
npm run build

# The build artifacts will be stored in the `dist/` directory
```

## 🐛 Troubleshooting

**Port 4200 already in use:**
```bash
ng serve --port 4201
```

**npm install fails:**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Backend connection issues:**
- Ensure backend is running on port 5001
- Check CORS configuration
- Verify API endpoints

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

**Note:** This frontend application requires the backend API to be running for full functionality. Start the backend server first, then launch this frontend application. 