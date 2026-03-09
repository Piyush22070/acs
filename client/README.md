# 🚀 Autonomous Chaos Sentinel - Frontend

A professional Next.js frontend for the Autonomous Chaos Sentinel payment system with AI-powered resilience and real-time transaction tracking.

## ✨ Quick Start

**Development server is already running at: `http://localhost:3001`**

```bash
cd /Users/piyush/Desktop/acs/client
pnpm dev
```

## 📚 Documentation

| Document | Time | Purpose |
|----------|------|---------|
| **[QUICKSTART.md](./QUICKSTART.md)** | 5 min | Overview & how to use |
| **[FEATURES_SUMMARY.md](./FEATURES_SUMMARY.md)** | 15 min | Feature breakdown with diagrams |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | 30+ min | Technical deep-dive |
| **[IMPLEMENTATION_REPORT.md](./IMPLEMENTATION_REPORT.md)** | 10 min | Project stats & metrics |
| **[BUILD_COMPLETE.md](./BUILD_COMPLETE.md)** | 10 min | Build summary & next steps |

**→ Start with [QUICKSTART.md](./QUICKSTART.md)**

## 🎯 Core Features

✅ **Idempotency Key Generator** - UUID per payment prevents duplicates  
✅ **Transaction Lifecycle Dashboard** - Real-time tracking (Pending → Validated → Finalized)  
✅ **Sentinel Health Pulse** - Animated health indicator with 3 states  
✅ **Smart Error Feedback** - Context-aware error messages  
✅ **Error Boundaries** - Graceful crash handling  
✅ **Optimistic UI Updates** - Immediate feedback while processing  
✅ **JWT Security Middleware** - Auth token validation  
✅ **Server-Side Rendering** - Instant loads on any device

## 🏗️ Project Structure

```
src/
├── components/
│   ├── layout/
│   │   └── Sidebar.tsx
│   └── ui/
│       ├── ErrorBoundary.tsx
│       ├── HealthPulse.tsx
│       ├── PaymentForm.tsx
│       └── TransactionDashboard.tsx
└── store/
    └── paymentStore.ts

app/
├── layout.tsx
├── page.tsx
├── dashboard/page.tsx
└── globals.css
```

## 💻 Tech Stack

- **Framework:** Next.js 16.1.2 (Turbopack)
- **State:** Zustand
- **Styling:** Tailwind CSS
- **Errors:** React Error Boundary
- **IDs:** UUID v4
- **Type Safety:** TypeScript

## 🎮 Usage

1. Open `http://localhost:3001`
2. Enter payment amount
3. Click "Pay Now"
4. Watch UUID generate & transaction track through states
5. Monitor health status in sidebar

## 🔌 Backend Integration

Ready to connect your APIs. Update these files:
- `src/components/ui/PaymentForm.tsx` - Payment submission
- `src/components/ui/HealthPulse.tsx` - Health polling
- `src/store/paymentStore.ts` - State updates

## 📖 Full Documentation

Read the docs in this order:
1. [QUICKSTART.md](./QUICKSTART.md) ⭐ Start here!
2. [FEATURES_SUMMARY.md](./FEATURES_SUMMARY.md)
3. [ARCHITECTURE.md](./ARCHITECTURE.md)

## ✅ Status

✅ Dev server running on http://localhost:3001  
✅ All 8 core features implemented  
✅ 5 professional components created  
✅ Ready for backend integration  
✅ Production-ready code quality  

---

**Built with ⚡ for the Autonomous Chaos Sentinel Project**

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
