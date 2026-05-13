# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Next.js Development Tools

### Node.js & Package Managers
- **Node.js**: v20+ required for Next.js 14+
- **npm**: Default package manager (comes with Node.js)
- **pnpm**: Preferred for monorepos — faster installs, better deduplication
- **yarn**: Alternative, use with Yarn 3+ for Plug'n'Play support

### Testing Frameworks
- **Vitest**: Fast unit/integration testing (Vite-based)
- **Playwright**: E2E testing (already configured with Patchright anti-detection)
- **Jest**: Legacy option for React component testing
- **React Testing Library**: For component testing

### Code Quality Tools
- **ESLint**: With Next.js and React plugins
- **Prettier**: Code formatting
- **TypeScript**: Strict mode enabled
- **Husky**: Git hooks for pre-commit checks

### Deployment Platforms
- **Vercel**: Primary deployment — optimized for Next.js
- **Netlify**: Alternative — good for static exports
- **Railway**: For full-stack applications
- **Docker**: For self-hosted deployments

### Development Utilities
- **VS Code**: IDE with Next.js extensions
- **Git**: Version control with conventional commits
- **GitHub Actions**: CI/CD pipeline automation
- **Docker**: Containerization for consistent environments

### Browser Testing
- **Patchright**: Already configured for anti-detection testing
- **Camoufox**: For testing on different browser fingerprints
- **BrowserStack**: Cross-browser testing (if needed)

### API & Database Tools
- **Prisma**: Database ORM (PostgreSQL, MySQL, SQLite)
- **Supabase**: Backend-as-a-Service with real-time features
- **GraphQL**: Apollo Client or GraphQL Yoga
- **REST**: Axios or fetch with proper TypeScript types

### Monitoring & Analytics
- **Vercel Analytics**: Built-in performance monitoring
- **Sentry**: Error tracking and performance monitoring
- **PostHog**: Product analytics
- **Google Analytics**: Web analytics

### Performance Optimization
- **Next.js Image Optimization**: Built-in image optimization
- **Bundle Analyzer**: Webpack bundle visualization
- **Lighthouse CI**: Automated performance audits
- **Core Web Vitals**: Performance monitoring

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Related

- [Agent workspace](/concepts/agent-workspace)

<!-- clawx:begin -->
## ClawX Tool Notes

### uv (Python)

- `uv` is bundled with ClawX and on PATH. Do NOT use bare `python` or `pip`.
- Run scripts: `uv run python <script>` | Install packages: `uv pip install <package>`

### Browser

- `browser` tool provides full automation (scraping, form filling, testing) via an isolated managed browser.
- Flow: `action="start"` → `action="snapshot"` (see page + get element refs like `e12`) → `action="act"` (click/type using refs).
- Open new tabs: `action="open"` with `targetUrl`.
- To just open a URL for the user to view, use `shell:openExternal` instead.
- If a browser action fails, transient errors (timeout, network) can often be resolved by retrying once or navigating to a different URL.
- When asked to search, look up, or interact with a web page, use the browser tool. Do not substitute with guesses or training data when real-time web access is requested.
<!-- clawx:end -->
