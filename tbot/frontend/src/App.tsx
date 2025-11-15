// tbot/frontend/src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import StrategyManagementPage from './pages/StrategyManagementPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="strategies" element={<StrategyManagementPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
