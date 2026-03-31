import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import Dashboard from './Dashboard/index.tsx'
import OutputSearch from './OutputSearch/index.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        {/* Dashboard Routes */}
        <Route path="/" element={<Dashboard />} />

        {/* Output Search Routes */}
        <Route path="/search" element={<OutputSearch />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
