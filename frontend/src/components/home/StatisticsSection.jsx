import DashboardStats from "../dashboard/DashboardStats";

export default function StatisticsSection({
  statistics,
}) {
  return (
    <div className="container py-5">
      <DashboardStats stats={statistics} />
    </div>
  );
}
