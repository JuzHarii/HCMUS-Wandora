import { Navigate, Route, Routes } from 'react-router'
import { lazy, Suspense } from 'react'

import { AuthProvider, RequireAuth } from '@/auth'

const LandingPage = lazy(() => import('@/pages/LandingPage').then(({ LandingPage }) => ({ default: LandingPage })))
const AuthPage = lazy(() => import('@/pages/AuthPage').then(({ AuthPage }) => ({ default: AuthPage })))
const TripDashboardPage = lazy(() => import('@/pages/TripDashboardPage').then(({ TripDashboardPage }) => ({ default: TripDashboardPage })))
const TripCreationPage = lazy(() => import('@/pages/TripCreationPage').then(({ TripCreationPage }) => ({ default: TripCreationPage })))
const ItineraryPage = lazy(() => import('@/pages/ItineraryPage').then(({ ItineraryPage }) => ({ default: ItineraryPage })))

function App() {
  return (
    <AuthProvider>
      <Suspense fallback={<main className="route-loading">Loading Wandora…</main>}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/landing" element={<Navigate replace to="/" />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/home" element={<RequireAuth><TripDashboardPage /></RequireAuth>} />
          <Route path="/trips" element={<Navigate replace to="/home" />} />
          <Route path="/trips/new" element={<RequireAuth><TripCreationPage /></RequireAuth>} />
          <Route path="/trips/:workspaceId" element={<RequireAuth><ItineraryPage /></RequireAuth>} />
          <Route path="*" element={<Navigate replace to="/" />} />
        </Routes>
      </Suspense>
    </AuthProvider>
  )
}

export default App
