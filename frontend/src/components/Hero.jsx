import SearchBar from "./SearchBar";

export default function Hero() {
    return (
        <section
            className="py-5"
            style={{
                background: "linear-gradient(135deg, #0d6efd, #4dabf7)",
                minHeight: "70vh",
                display: "flex",
                alignItems: "center",
            }}
        >
            <div className="container">
                <div className="row align-items-center">

                    <div className="col-lg-7 text-white">
                        <h1 className="display-3 fw-bold">
                            Scientific Collaboration
                        </h1>

                        <h2 className="display-5 mb-4">
                            Network Analyzer
                        </h2>

                        <p className="lead mb-4">
                            Discover publications, explore researchers,
                            connect institutions, and find conferences
                            from one unified research platform.
                        </p>

                        <SearchBar />
                    </div>

                    <div className="col-lg-5 text-center">
                        <img
                            src="https://cdn-icons-png.flaticon.com/512/2103/2103633.png"
                            alt="Research"
                            className="img-fluid"
                            style={{
                                maxHeight: "350px",
                            }}
                        />
                    </div>

                </div>
            </div>
        </section>
    );
}
