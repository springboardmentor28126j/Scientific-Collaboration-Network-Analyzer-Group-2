function Pagination({

    currentPage,
    totalPages,
    onPageChange

}) {

    if (totalPages <= 1) return null;

    return (

        <div className="d-flex justify-content-center mt-4">

            <button
                className="btn btn-outline-primary me-2"
                disabled={currentPage === 1}
                onClick={() => onPageChange(currentPage - 1)}
            >
                Previous
            </button>

            {

                [...Array(totalPages)].map((_, index) => (

                    <button
                        key={index}
                        className={
                            currentPage === index + 1
                                ? "btn btn-primary me-2"
                                : "btn btn-outline-primary me-2"
                        }
                        onClick={() => onPageChange(index + 1)}
                    >
                        {index + 1}
                    </button>

                ))

            }

            <button
                className="btn btn-outline-primary"
                disabled={currentPage === totalPages}
                onClick={() => onPageChange(currentPage + 1)}
            >
                Next
            </button>

        </div>

    );

}

export default Pagination;