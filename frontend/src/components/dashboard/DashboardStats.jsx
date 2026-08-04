import {
  Users,
  FileText,
  Building2,
  CalendarDays,
} from "lucide-react";

export default function DashboardStats({ stats }) {
  if (!stats) {
    return (
      <div className="text-center py-5">
        <div
          className="spinner-border text-primary"
          role="status"
        >
          <span className="visually-hidden">Loading...</span>
        </div>

        <p className="mt-3">Loading dashboard...</p>
      </div>
    );
  }

  const cards = [
    {
      title: "Researchers",
      value: stats.researchers,
      color: "primary",
      icon: <Users size={42} />,
    },
    {
      title: "Publications",
      value: stats.publications,
      color: "success",
      icon: <FileText size={42} />,
    },
    {
      title: "Institutions",
      value: stats.institutions,
      color: "warning",
      icon: <Building2 size={42} />,
    },
    {
      title: "Conferences",
      value: stats.conferences,
      color: "info",
      icon: <CalendarDays size={42} />,
    },
  ];

  return (
    <div className="row g-4 mb-5">

      {cards.map((card) => (

        <div
          key={card.title}
          className="col-lg-3 col-md-6"
        >
          <div
            className={`card border-0 shadow h-100 border-start border-5 border-${card.color}`}
          >
            <div className="card-body">

              <div className="d-flex justify-content-between align-items-center">

                <div>

                  <h6 className="text-muted mb-2">
                    {card.title}
                  </h6>

                  <h2 className={`text-${card.color}`}>
                    {card.value}
                  </h2>

                </div>

                <div className={`text-${card.color}`}>
                  {card.icon}
                </div>

              </div>

            </div>
          </div>
        </div>

      ))}

    </div>
  );
}
