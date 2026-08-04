import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const COLORS = [
  "#0d6efd",
  "#198754",
  "#ffc107",
  "#dc3545",
  "#20c997",
  "#6f42c1",
];

export default function DashboardCharts({
  yearlyData,
  publicationTypes,
}) {
  return (
    <div className="row g-4">

      <div className="col-lg-7">

        <div className="card shadow border-0 h-100">

          <div className="card-body">

            <h5 className="mb-4">
              Publications Per Year
            </h5>

            <ResponsiveContainer
              width="100%"
              height={320}
            >
              <LineChart data={yearlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip />

                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#0d6efd"
                  strokeWidth={3}
                />

              </LineChart>
            </ResponsiveContainer>

          </div>

        </div>

      </div>

      <div className="col-lg-5">

        <div className="card shadow border-0 h-100">

          <div className="card-body">

            <h5 className="mb-4">
              Publication Types
            </h5>

            <ResponsiveContainer
              width="100%"
              height={320}
            >
              <PieChart>

                <Pie
                  data={publicationTypes}
                  dataKey="count"
                  nameKey="type"
                  outerRadius={100}
                  label
                >

                  {publicationTypes.map(
                    (entry, index) => (
                      <Cell
                        key={index}
                        fill={
                          COLORS[
                            index % COLORS.length
                          ]
                        }
                      />
                    )
                  )}

                </Pie>

                <Tooltip />

                <Legend />

              </PieChart>
            </ResponsiveContainer>

          </div>

        </div>

      </div>

    </div>
  );
}
