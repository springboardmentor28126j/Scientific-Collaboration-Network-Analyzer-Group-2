export default function Pagination({

    currentPage,

    totalPages,

    onPageChange,

}) {

    return (

        <div className="d-flex justify-content-center mt-4">

            <button
                className="btn btn-outline-primary me-2"
                disabled={currentPage === 1}
                onClick={() => onPageChange(currentPage - 1)}
            >
                Previous
            </button>

            <span className="align-self-center">

                Page {currentPage} of {totalPages}

            </span>

            <button
                className="btn btn-outline-primary ms-2"
                disabled={currentPage === totalPages}
                onClick={() => onPageChange(currentPage + 1)}
            >
                Next
            </button>

        </div>

    );

}
