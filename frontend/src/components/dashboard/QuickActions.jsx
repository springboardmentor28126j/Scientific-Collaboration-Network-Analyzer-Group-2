import { Link } from "react-router-dom";

export default function QuickActions() {

  const actions = [
    {
      title: "Add Researcher",
      route: "/researchers/create",
      color: "primary",
    },
    {
      title: "Add Publication",
      route: "/publications/create",
      color: "success",
    },
    {
      title: "Add Institution",
      route: "/institutions/create",
      color: "warning",
    },
    {
      title: "Add Conference",
      route: "/conferences/create",
      color: "info",
    },
  ];

  return (
    <div className="card shadow border-0 mb-5">

      <div className="card-body">

        <h4 className="mb-4">
          🚀 Quick Actions
        </h4>

        <div className="row g-3">

          {actions.map((action) => (

            <div
              key={action.title}
              className="col-lg-3 col-md-6"
            >
              <Link
                to={action.route}
                className={`btn btn-${action.color} w-100 py-3`}
              >
                {action.title}
              </Link>
            </div>

          ))}

        </div>

      </div>

    </div>
  );
}
