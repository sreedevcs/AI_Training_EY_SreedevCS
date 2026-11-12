import { Navigate, Outlet, useLocation } from 'react-router-dom'

function ProtectedRoute({ isLoggedIn }) {
  const location = useLocation()

  if (!isLoggedIn) {
    return (
      <Navigate
        to="/login"
        state={{ from: location }}
        replace
      />
    )
  }

  return <Outlet />
}

export default ProtectedRoute