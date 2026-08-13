import { Navigate, Route, Routes } from 'react-router'

import { AuthProvider, RequireAuth } from '@/auth'
import { AuthPage } from '@/pages/AuthPage'
import { ItineraryPage } from '@/pages/ItineraryPage'
import { LandingPage } from '@/pages/LandingPage'
import { TripCreationPage } from '@/pages/TripCreationPage'
import { TripDashboardPage } from '@/pages/TripDashboardPage'

function App() {
  return (
    <AuthProvider>
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
    </AuthProvider>
  )
}

export default App
