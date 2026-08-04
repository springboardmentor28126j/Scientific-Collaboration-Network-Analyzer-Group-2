import { useEffect, useState } from "react";

import DashboardStats from "../components/dashboard/DashboardStats";
import QuickActions from "../components/dashboard/QuickActions";
import DashboardCharts from "../components/dashboard/DashboardCharts";

import {
  getDashboardStats,
  getPublicationsPerYear,
  getPublicationTypes,
} from "../services/dashboardService";

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  const [yearlyData, setYearlyData] = useState([]);

  const [publicationTypes, setPublicationTypes] =
    useState([]);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [
        statsData,
        yearly,
        types,
      ] = await Promise.all([
        getDashboardStats(),
        getPublicationsPerYear(),
        getPublicationTypes(),
      ]);

      setStats(statsData);
      setYearlyData(yearly);
      setPublicationTypes(types);

    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="container py-5">

      <h1 className="mb-2">
        Dashboard
      </h1>

      <p className="text-muted mb-4">
        Welcome to the Scientific Collaboration Network Analyzer.
      </p>

      <QuickActions />

      <DashboardStats stats={stats} />

      <DashboardCharts
        yearlyData={yearlyData}
        publicationTypes={publicationTypes}
      />

    </div>
  );
}
