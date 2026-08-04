import { Link } from "react-router-dom";

export default function ResearcherTable({ researchers }) {

    if (!researchers || researchers.length === 0) {
        return (
            <div className="alert alert-info">
                No researchers found.
            </div>
        );
    }

    return (
        <div className="table-responsive">

            <table className="table table-hover align-middle">

                <thead className="table-primary">

                    <tr>
                        <th>Name</th>
                        <th>Experience</th>
                        <th>Phone</th>
                        <th>Actions</th>
                    </tr>

                </thead>

                <tbody>

                    {researchers.map((researcher) => (

                        <tr key={researcher.id}>

                            <td>{researcher.first_name} {researcher.last_name}</td>

                            <td>{researcher.experience} Years</td>

                            <td>{researcher.phone}</td>

                            <td>

                                <Link
                                    className="btn btn-sm btn-primary me-2"
                                    to={`/researchers/${researcher.id}`}
                                >
                                    View
                                </Link>

                                <Link
                                    className="btn btn-sm btn-warning me-2"
                                    to={`/researchers/edit/${researcher.id}`}
                                >
                                    Edit
                                </Link>

                                <button
                                    className="btn btn-sm btn-danger"
                                >
                                    Delete
                                </button>

                            </td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>
    );
}
