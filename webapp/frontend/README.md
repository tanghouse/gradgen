# GradGen Frontend

Next.js frontend for the GradGen graduation portrait generation platform.

## Features

### Pages

- **Landing Page** (`/`) - Hero, features, pricing
- **Login** (`/login`) - User authentication
- **Register** (`/register`) - New user signup with 5 free credits
- **Generate** (`/generate`) - Upload portraits and select university/degree
- **Dashboard** (`/dashboard`) - View jobs, download results, manage credits
- **Credits** (`/credits`) - Purchase credits via Stripe
- **Examples** (`/examples`) - Showcase sample transformations

### Key Functionality

- **Authentication**: JWT-based auth with persistent login
- **File Upload**: Single and batch portrait uploads
- **University Selection**: Dynamic university and degree level picker
- **Real-time Job Polling**: Automatic updates for processing jobs
- **Stripe Integration**: Secure credit purchases
- **Download Management**: Easy result downloads

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Payments**: Stripe.js + Stripe React Elements
- **State Management**: React Context API

## Setup

### Prerequisites

- Node.js 18+
- npm

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local with your backend URL
nano .env.local
```

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start dev server
npm run dev

# Open browser
open http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
app/
├── page.tsx              # Landing page
├── layout.tsx            # Root layout with AuthProvider
├── globals.css           # Global styles + Tailwind
├── login/page.tsx        # Login page
├── register/page.tsx     # Registration page
├── generate/page.tsx     # Portrait generation
├── dashboard/page.tsx    # User dashboard
├── credits/page.tsx      # Credit purchase
└── examples/page.tsx     # Example showcase

components/
└── Navbar.tsx            # Shared navigation component

lib/
├── api.ts                # API client with TypeScript types
└── auth-context.tsx      # Auth state management
```

## API Integration

The frontend communicates with the FastAPI backend via `/lib/api.ts`:

### Auth API
- `authAPI.register()` - Create new user
- `authAPI.login()` - Authenticate user

### User API
- `userAPI.getMe()` - Get current user
- `userAPI.updateMe()` - Update user info

### Generation API
- `generationAPI.listUniversities()` - Get available universities
- `generationAPI.generateSingle()` - Generate single portrait
- `generationAPI.generateBatch()` - Generate multiple portraits
- `generationAPI.listJobs()` - Get user's jobs
- `generationAPI.getJobStatus()` - Poll job status
- `generationAPI.downloadResult()` - Get download URL

### Payment API
- `paymentAPI.getConfig()` - Get Stripe public key
- `paymentAPI.createPaymentIntent()` - Create payment

## Authentication Flow

1. User registers/logs in
2. JWT token stored in `localStorage`
3. `AuthProvider` fetches user data
4. Token automatically added to API requests
5. Expired tokens redirect to login

## Protected Routes

Pages requiring authentication:
- `/generate`
- `/dashboard`
- `/credits`

Unauthenticated users are redirected to `/login`.

## Stripe Integration

The credits page uses Stripe Elements for secure payments:

1. User selects credit package
2. Frontend creates payment intent via backend
3. Stripe Elements renders payment form
4. Payment processed securely
5. Backend webhook adds credits to user account

## Job Polling

Dashboard automatically polls for job updates:
- Checks every 3 seconds
- Updates progress bar
- Stops polling when job completes
- Displays download buttons for completed images

## Styling

Uses Tailwind CSS with custom primary color palette:

```javascript
colors: {
  primary: {
    50: '#eff6ff',
    ...
    600: '#2563eb', // Main brand color
    ...
  }
}
```

## TypeScript

Fully typed with interfaces for:
- `User` - User account
- `University` - University data
- `GenerationJob` - Generation job
- `GeneratedImage` - Generated result
- `JobStatus` - Job polling response

## Development Tips

### Hot Reload
Next.js automatically reloads on file changes.

### API Changes
If backend API changes, update types in `lib/api.ts`.

### Styling
Use Tailwind utility classes. Custom styles go in `globals.css`.

### Environment Variables
Prefix public vars with `NEXT_PUBLIC_`.

## Common Issues

### CORS Errors
Ensure backend has correct `ALLOWED_ORIGINS` in `.env`.

### Auth Issues
Clear localStorage and re-login if tokens expire.

### Stripe Not Loading
Check Stripe publishable key is correct.

### Build Errors
Run `npm install` to ensure dependencies are up to date.

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL
```

### Docker

```bash
# Build image
docker build -t gradgen-frontend .

# Run container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=https://api.yourdomain.com gradgen-frontend
```

### Environment Variables in Production

Set `NEXT_PUBLIC_API_URL` to your production backend URL.

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## License

See main project LICENSE file.
