import { Navigate, Route, Routes } from 'react-router'
import { lazy, Suspense } from 'react'

import { AuthProvider, RequireAuth } from '@/auth'

const LandingPage = lazy(() => import('@/pages/LandingPage').then(({ LandingPage }) => ({ default: LandingPage })))
const AuthPage = lazy(() => import('@/pages/AuthPage').then(({ AuthPage }) => ({ default: AuthPage })))
const TripDashboardPage = lazy(() => import('@/pages/TripDashboardPage').then(({ TripDashboardPage }) => ({ default: TripDashboardPage })))
const TripCreationPage = lazy(() => import('@/pages/TripCreationPage').then(({ TripCreationPage }) => ({ default: TripCreationPage })))
const TripWorkspacePage = lazy(() => import('@/pages/TripWorkspacePage').then(({ TripWorkspacePage }) => ({ default: TripWorkspacePage })))
const ItineraryTab = lazy(() => import('@/pages/tabs/ItineraryTab').then(({ ItineraryTab }) => ({ default: ItineraryTab })))
const PackingTab = lazy(() => import('@/pages/tabs/PackingTab').then(({ PackingTab }) => ({ default: PackingTab })))
const MembersTab = lazy(() => import('@/pages/tabs/MembersTab').then(({ MembersTab }) => ({ default: MembersTab })))
const ReviewsTab = lazy(() => import('@/pages/tabs/ReviewsTab').then(({ ReviewsTab }) => ({ default: ReviewsTab })))
const ShareTab = lazy(() => import('@/pages/tabs/ShareTab').then(({ ShareTab }) => ({ default: ShareTab })))

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
          <Route path="/trips/:workspaceId" element={<RequireAuth><TripWorkspacePage /></RequireAuth>}>
            <Route index element={<Navigate to="itinerary" replace />} />
            <Route path="itinerary" element={<ItineraryTab />} />
            <Route path="packing" element={<PackingTab />} />
            <Route path="members" element={<MembersTab />} />
            <Route path="reviews" element={<ReviewsTab />} />
            <Route path="share" element={<ShareTab />} />
            <Route path="*" element={<Navigate to="itinerary" replace />} />
          </Route>
          <Route path="*" element={<Navigate replace to="/" />} />
        </Routes>
      </Suspense>
    </AuthProvider>
  )
}

export default App
