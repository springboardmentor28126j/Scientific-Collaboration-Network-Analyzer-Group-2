function ConferencePagination({
  totalItems,
  itemsPerPage,
  currentPage,
  paginate,
}) {
  const pageNumbers = [];

  for (
    let i = 1;
    i <= Math.ceil(totalItems / itemsPerPage);
    i++
  ) {
    pageNumbers.push(i);
  }

  if (pageNumbers.length <= 1) {
    return null;
  }

  return (
    <nav className="mt-4">
      <ul className="pagination justify-content-center">

        <li
          className={`page-item ${
            currentPage === 1 ? "disabled" : ""
          }`}
        >
          <button
            className="page-link"
            onClick={() => paginate(currentPage - 1)}
          >
            Previous
          </button>
        </li>

        {pageNumbers.map((number) => (
          <li
            key={number}
            className={`page-item ${
              currentPage === number ? "active" : ""
            }`}
          >
            <button
              className="page-link"
              onClick={() => paginate(number)}
            >
              {number}
            </button>
          </li>
        ))}

        <li
          className={`page-item ${
            currentPage === pageNumbers.length
              ? "disabled"
              : ""
          }`}
        >
          <button
            className="page-link"
            onClick={() => paginate(currentPage + 1)}
          >
            Next
          </button>
        </li>

      </ul>
    </nav>
  );
}

export default ConferencePagination;
