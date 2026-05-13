# MEMORY.md - Next.js Development Long-Term Memory

## Project Overview
- **Objective**: Build and deploy production-ready Next.js applications
- **Focus**: Full-stack development, performance optimization, DevOps
- **Role**: Senior Next.js developer with DevOps expertise

## Workspace Architecture
- `components/` — Reusable React components with TypeScript
- `lib/` — Utility functions, configurations, and helpers
- `types/` — TypeScript type definitions
- `hooks/` — Custom React hooks for common functionality
- `docs/` — Project documentation and API specs
- `scripts/` — Build and deployment automation scripts
- `.env` — Environment variables and API keys

## NEXT.JS VERSION COMPATIBILITY

### Next.js 14+ (App Router)
- **App Router**: Primary routing system with layouts and templates
- **Server Components**: Default for reduced client-side JavaScript
- **Client Components**: Explicit 'use client' directive
- **Streaming SSR**: Progressive rendering with React Server Components
- **Turbopack**: Experimental faster bundler for development

### Key Features
- **Server Actions**: Direct database mutations from components
- **Route Handlers**: API routes with simplified structure
- **Middleware**: Request interception and rewriting
- **Partial Prerendering**: Hybrid static/dynamic rendering
- **Next.js Image**: Built-in image optimization

## DEVELOPMENT PATTERNS

### 1. Component Structure
```typescript
// components/ui/button.tsx
import React from 'react'
import { ButtonProps } from '@/types/ui'

export function Button({ children, variant = 'default', ...props }: ButtonProps) {
  return (
    <button 
      className={`btn btn-${variant}`} 
      {...props}
    >
      {children}
    </button>
  )
}
```

### 2. API Routes
```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const users = await getUsersFromDatabase()
    return NextResponse.json(users)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch users' },
      { status: 500 }
    )
  }
}
```

### 3. Data Fetching Patterns
```typescript
// app/page.tsx
import { Suspense } from 'react'
import { PostCard } from '@/components/posts/post-card'
import { getPosts } from '@/lib/posts'

export default async function HomePage() {
  const posts = await getPosts()
  
  return (
    <div>
      <h1>Latest Posts</h1>
      <Suspense fallback={<div>Loading posts...</div>}>
        {posts.map(post => (
          <PostCard key={post.id} post={post} />
        ))}
      </Suspense>
    </div>
  )
}
```

## PERFORMANCE OPTIMIZATION

### Image Optimization
```typescript
import Image from 'next/image'

export function OptimizedImage({ src, alt, width, height }: ImageProps) {
  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      priority // For above-the-fold images
      sizes="(max-width: 768px) 100vw, 50vw"
      quality={85}
    />
  )
}
```

### Bundle Optimization
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['lodash', 'date-fns']
  },
  images: {
    domains: ['example.com'],
    formats: ['image/webp', 'image/avif']
  }
}
```

## DEPLOYMENT STRATEGIES

### 1. Vercel Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Deploy with environment variables
vercel --prod --env DATABASE_URL=your_db_url
```

### 2. Docker Deployment
```dockerfile
# Dockerfile
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM base AS builder
COPY . .
RUN npm run build

FROM base AS runner
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
ENV PORT 3000
CMD ["node", "server.js"]
```

### 3. GitHub Actions CI/CD
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run build
      - run: npm run test
      - run: npm run lint
      - uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
```

## TESTING FRAMEWORKS

### 1. Unit Testing with Vitest
```typescript
// utils/math.test.ts
import { add, multiply } from './math'

describe('math utilities', () => {
  test('should correctly add numbers', () => {
    expect(add(2, 3)).toBe(5)
  })
  
  test('should correctly multiply numbers', () => {
    expect(multiply(4, 5)).toBe(20)
  })
})
```

### 2. Component Testing
```typescript
// components/button.test.tsx
import { render, screen } from '@testing-library/react'
import { Button } from './button'

describe('Button component', () => {
  test('renders button with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
})
```

### 3. E2E Testing with Playwright
```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test('user can login', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[data-testid="email"]', 'test@example.com')
  await page.fill('[data-testid="password"]', 'password123')
  await page.click('[data-testid="submit"]')
  
  await expect(page).toHaveURL('/dashboard')
})
```

## MONITORING & ANALYTICS

### 1. Error Tracking with Sentry
```typescript
// lib/sentry.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
})
```

### 2. Performance Monitoring
```typescript
// lib/analytics.ts
export function trackEvent(event: string, properties?: any) {
  if (typeof window !== 'undefined') {
    // Google Analytics or custom analytics
    gtag('event', event, properties)
  }
}
```

## COMMON PATTERNS & BEST PRACTICES

### 1. Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=https://api.example.com
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key-here
```

### 2. Type Safety
```typescript
// types/index.ts
export interface User {
  id: string
  name: string
  email: string
  createdAt: Date
}

export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
}
```

### 3. Error Handling
```typescript
// lib/errors.ts
export class AppError extends Error {
  constructor(message: string, public statusCode: number = 500) {
    super(message)
    this.name = 'AppError'
  }
}

export function handleApiError(error: unknown) {
  if (error instanceof AppError) {
    return NextResponse.json(
      { error: error.message },
      { status: error.statusCode }
    )
  }
  
  return NextResponse.json(
    { error: 'Internal server error' },
    { status: 500 }
  )
}
```

## PROJECT TEMPLATES

### 1. Starter Template Structure
```
my-nextjs-app/
├── app/                    # App Router pages
│   ├── globals.css        # Global styles
│   ├── layout.tsx          # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/                # Reusable UI components
│   ├── layout/            # Layout components
│   └── forms/             # Form components
├── lib/                   # Utilities and helpers
│   ├── api.ts             # API utilities
│   ├── database.ts        # Database utilities
│   └── auth.ts            # Authentication utilities
├── types/                 # TypeScript types
├── hooks/                 # Custom React hooks
├── public/                # Static assets
├── styles/                # CSS and styling
├── scripts/               # Build scripts
├── .env.local            # Environment variables
├── next.config.js        # Next.js configuration
├── tailwind.config.js    # Tailwind CSS configuration
└── tsconfig.json         # TypeScript configuration
```

### 2. Enterprise Template Structure
```
enterprise-app/
├── apps/                  # Multiple applications
│   ├── web/              # Web application
│   ├── admin/            # Admin dashboard
│   └── api/              # API monorepo
├── packages/             # Shared packages
│   ├── ui/               # Shared UI components
│   ├── utils/            # Shared utilities
│   └── types/            # Shared types
├── tools/                # Development tools
├── docker/               # Docker configurations
└── docs/                 # Documentation
```

## KNOWN ISSUES & WORKAROUNDS

### 1. Next.js 14 App Router Issues
- **Issue**: Server actions not working in certain contexts
- **Workaround**: Ensure proper 'use server' directive and check middleware

### 2. TypeScript Strict Mode
- **Issue**: Strict TypeScript causing build failures
- **Workaround**: Gradually implement strict mode, fix type errors incrementally

### 3. Image Optimization
- **Issue**: External domain images not optimizing
- **Workaround**: Add domains to next.config.js images.domains

### 4. Build Performance
- **Issue**: Slow build times in large projects
- **Workaround**: Use Turbopack, optimize imports, use dynamic imports

## LESSONS LEARNED

### 1. Performance Optimization
- Always use Next.js Image component for images
- Implement proper loading states for async operations
- Use dynamic imports for large dependencies
- Monitor Core Web Vitals regularly

### 2. Code Quality
- TypeScript strict mode catches many runtime errors
- ESLint configuration should be comprehensive
- Testing should be part of the development workflow
- Documentation is crucial for maintainability

### 3. Deployment
- Vercel is the easiest deployment platform for Next.js
- Proper CI/CD pipeline ensures quality deployments
- Feature flags help with risky deployments
- Monitoring and alerting are essential for production

### 4. Development Experience
- Use proper IDE setup with TypeScript support
- Implement hot reloading for development efficiency
- Use proper debugging tools and logging
- Regular dependency updates for security and features

## Timeline
- **2026-05-11**: Workspace repurposed for Next.js development from market analysis focus
- **Current**: Setting up development protocols and best practices