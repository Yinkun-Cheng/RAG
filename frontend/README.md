# RAG Frontend

React frontend for RAG Test Case Management System.

## Structure

```
frontend/
├── src/
│   ├── api/                  # API calls
│   ├── components/           # Reusable components
│   │   ├── Layout/
│   │   ├── ModuleTree/
│   │   ├── MarkdownEditor/
│   │   ├── ImageUpload/
│   │   └── TagSelect/
│   ├── pages/                # Page components
│   │   ├── Dashboard/
│   │   ├── PRD/
│   │   ├── TestCase/
│   │   ├── Import/
│   │   └── Search/
│   ├── hooks/                # Custom hooks
│   ├── store/                # State management
│   ├── types/                # TypeScript types
│   ├── utils/                # Utility functions
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

4. Open browser at http://localhost:5173

## Development

- React 18 + TypeScript
- Vite for build tool
- Ant Design for UI components
- React Query for data fetching
- Zustand for state management
