export default function StatsSection({ stats }) {

    if (!stats) {
        return (
            <div className="container py-5 text-center">
                Loading statistics...
            </div>
        );
    }

    const cards = [
        {
            title: "Researchers",
            value: stats.researchers,
        },
        {
            title: "Publications",
            value: stats.publications,
        },
        {
            title: "Institutions",
            value: stats.institutions,
        },
        {
            title: "Conferences",
            value: stats.conferences,
        },
    ];

    return (
        <section className="py-5 bg-light">
            <div className="container">
                <div className="row g-4">

                    {cards.map((card) => (
                        <div
                            className="col-md-3"
                            key={card.title}
                        >
                            <div className="card shadow border-0 h-100 text-center">
                                <div className="card-body">

                                    <h5 className="text-muted">
                                        {card.title}
                                    </h5>

                                    <h2 className="display-5 fw-bold text-primary">
                                        {card.value}
                                    </h2>

                                </div>
                            </div>
                        </div>
                    ))}

                </div>
            </div>
        </section>
    );
}
