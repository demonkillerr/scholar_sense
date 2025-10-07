# Sentiment Analysis Frontend Service

## Project Overview
A Next.js-based sentiment analysis frontend that provides a user-friendly interface for text and document sentiment analysis. The application allows users to upload documents (PDF), specify topics for analysis, and view sentiment analysis results with visual indicators.

## Technology Stack
- **Next.js**: React framework with server-side rendering capabilities
- **React**: JavaScript library for building user interfaces
- **TypeScript**: Typed JavaScript for improved developer experience
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Next API Routes**: API routing within the Next.js application

## Project Structure
```
frontend/
├── src/
│   └── app/
│       ├── api/
│       │   ├── analyse/
│       │   │   └── route.ts           # API route for sentiment analysis
│       │   └── upload/
│       │       └── route.ts           # API route for file upload
│       ├── favicon.ico
│       ├── globals.css                 # Global CSS styles
│       ├── layout.tsx                  # Root layout component
│       └── page.tsx                    # Main page component with UI
├── public/                             # Static assets directory
├── package.json                        # Project dependencies
├── tailwind.config.ts                  # Tailwind CSS configuration
├── tsconfig.json                       # TypeScript configuration
└── next.config.ts                      # Next.js configuration
```

## Environment Requirements
- Node.js 18.0 or higher
- npm or yarn package manager
- Connection to the backend service

## Deployment Steps
1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Start the development server:
```bash
npm run dev
# or
yarn dev
```

3. Build for production:
```bash
npm run build
# or
yarn build
```

4. Start the production server:
```bash
npm start
# or
yarn start
```

## Configuration
- Backend API is configured to connect to `http://localhost:5000` by default
- File upload size and types are validated both client and server-side

## Frontend Features

### 1. Document Upload
- Drag-and-drop interface for uploading PDF files
- File validation to ensure only PDFs are accepted
- Visual feedback for upload status

### 2. Topic-based Analysis
- Input field for specifying analysis topic
- Validation to ensure required information is provided

### 3. Results Display
- Sentiment analysis results with visual indicators
- Support/Oppose/Neutral stance indication with color coding
- Display of relevance scores and sentiment percentages
- Topic-related sentences and keywords highlighting

## API Integration

### 1. File Upload API
- **Endpoint**: `/api/upload`
- **Method**: POST
- **Function**: Forwards file uploads to the backend service

### 2. Analysis API
- **Endpoint**: `/api/analyse`
- **Method**: POST
- **Function**: Sends analysis requests to the backend with file path and topic

## Error Handling
The frontend implements the following error handling:
- File type validation (PDF only)
- Required field validation
- API error handling with user-friendly messages
- Network error handling

## Development Notes
1. Run `npm run dev` for the development environment with hot reloading
2. The development server runs on `http://localhost:3000` by default
3. Backend connection is required for API functionality

## Browser Compatibility
- Chrome/Edge/Firefox/Safari (latest versions)
- Responsive design for desktop and mobile devices
