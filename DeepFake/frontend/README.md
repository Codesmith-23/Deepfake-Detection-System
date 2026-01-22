# Deepfake Video Detection System

A modern, professional frontend application for detecting deepfake videos using advanced AI technology. Built with Next.js 15, TypeScript, and Tailwind CSS.

## Features

### Core Pages
- **Landing Page**: Engaging hero section with project overview and statistics
- **Video Detection**: Drag-and-drop video upload with real-time analysis progress
- **About Page**: Detailed explanation of deepfake detection technology and methods
- **History Page**: Local storage-based history with search, filter, and export capabilities
- **Contact Page**: Support form with FAQ section

### Key Features
- 🎯 **Professional UI/UX**: Clean, modern design optimized for all devices
- 🚀 **Real-time Analysis**: Progress tracking with detailed status updates
- 📊 **Detailed Results**: Confidence scores, flagged frames, and downloadable reports
- 📱 **Responsive Design**: Mobile-first approach with seamless desktop scaling
- 🌙 **Dark Mode Support**: Toggle between light and dark themes
- 💾 **Local History**: Browser-based storage of analysis results
- 🔍 **Advanced Filtering**: Search and filter capabilities for history
- 📥 **Export Features**: Download analysis reports and history data

### Technical Highlights
- Built with **Next.js 15** (App Router)
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Lucide React** icons
- **Framer Motion** animations
- **React Dropzone** for file uploads
- **Axios** for API communication

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager

### Installation

1. **Clone or extract the project**
   ```bash
   cd deepfake-detection-system
   ```

2. **Install dependencies**
   ```bash
   npm install --legacy-peer-deps
   ```
   *Note: `--legacy-peer-deps` is used to handle React 19 compatibility issues with some packages*

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (root)/            # Landing page
│   ├── about/             # About page
│   ├── contact/           # Contact page
│   ├── detect/            # Video detection page
│   ├── history/           # Analysis history page
│   ├── globals.css        # Global styles
│   └── layout.tsx         # Root layout
├── components/
│   ├── layout/            # Header, Footer components
│   ├── ui/                # Reusable UI components
│   ├── DetectionResults.tsx
│   └── VideoUpload.tsx
├── hooks/                 # Custom React hooks
├── lib/                   # Utility functions and API
├── types/                 # TypeScript type definitions
└── ...
```

## Backend Integration

The frontend is designed to work with a REST API backend. Configure the following:

### Environment Variables

Create a `.env.local` file in the project root:

```env
NEXT_PUBLIC_API_BASE_URL=http://your-backend-url/api
```

### API Endpoints

The frontend expects these endpoints:

#### POST /api/analyze
Upload and analyze video file
```typescript
// Request: FormData with 'video' field
// Response:
{
  "success": true,
  "data": {
    "result": "deepfake" | "real",
    "confidence": 85,
    "flaggedFrames": ["url1", "url2", ...],
    "processingTime": 30
  }
}
```

#### POST /api/support
Submit support form
```typescript
// Request:
{
  "name": "string",
  "email": "string", 
  "subject": "string",
  "message": "string",
  "type": "general" | "technical" | "false_positive" | "false_negative"
}
```

#### POST /api/report
Report false positive/negative
```typescript
// Request:
{
  "analysisId": "string",
  "reportType": "false_positive" | "false_negative",
  "userFeedback": "string"
}
```

#### GET /api/health
Health check endpoint
```typescript
// Response:
{
  "status": "healthy" | "unhealthy",
  "version": "1.0.0"
}
```

### Mock API Mode

During development, the system uses a mock API that simulates real backend responses:

- Simulates upload progress
- Returns randomized analysis results
- Includes mock flagged frames
- Handles error states

To switch to production API, update the environment variable and ensure your backend implements the expected endpoints.

## Customization

### Styling
- Modify `tailwind.config.ts` for theme customization
- Update color palette in the config file
- Adjust component styles in their respective files

### Components
All components are designed to be modular and reusable:
- **Button**: Multiple variants and sizes
- **ProgressBar**: Customizable progress indicator  
- **Modal**: Flexible dialog component
- **VideoUpload**: Drag-and-drop file uploader

### API Integration
Update `src/lib/api.ts` to modify:
- API endpoint URLs
- Request/response formats
- Error handling
- Authentication

## Features Overview

### Video Detection Workflow
1. **Upload**: Drag-and-drop or browse for video files (MP4, AVI, MOV)
2. **Validation**: File type and size validation (max 500MB)
3. **Analysis**: Real-time progress updates with detailed stages
4. **Results**: Comprehensive analysis with confidence scores
5. **Actions**: Download reports, view flagged frames, report issues

### Analysis Results Include
- Overall result (Likely Deepfake / Likely Real)
- Confidence percentage with visual progress bar
- File information and analysis metadata
- Flagged frame thumbnails (when applicable)
- Downloadable JSON report
- Report issue functionality

### History Management
- Local browser storage of all analyses
- Search by filename
- Filter by result type (all/deepfake/real)
- Sort by date, filename, or confidence
- Export history data
- Individual entry management

## Browser Compatibility

- **Chrome** 88+
- **Firefox** 85+
- **Safari** 14+
- **Edge** 88+

## Performance Considerations

- Optimized bundle size with Next.js
- Lazy loading of non-critical components
- Efficient image handling
- Local storage for offline capabilities
- Responsive images and layouts

## Security Features

- Client-side file validation
- Secure API communication
- No permanent file storage
- Privacy-focused design
- CSRF protection ready

## Deployment

### Production Build
```bash
npm run build
npm start
```

### Static Export (if needed)
```bash
npm run build
npm run export
```

### Environment Setup
Ensure production environment variables are set:
- `NEXT_PUBLIC_API_BASE_URL`
- Any additional backend configuration

## Contributing

The codebase is structured for easy maintenance:

1. **Type Safety**: Full TypeScript coverage
2. **Component Structure**: Modular, reusable components
3. **Error Handling**: Comprehensive error boundaries
4. **Testing Ready**: Component structure supports testing
5. **Documentation**: Inline comments and clear naming

## Support

For technical issues or questions:
- Check the FAQ in the contact page
- Review the component documentation
- Ensure backend API compatibility
- Verify environment configuration

## License

This project is designed as a professional template for deepfake detection systems. Adapt the code according to your specific requirements and backend implementation.

---

**Built with ❤️ using Next.js, TypeScript, and Tailwind CSS**
