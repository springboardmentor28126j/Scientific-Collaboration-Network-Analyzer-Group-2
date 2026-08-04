function CitationPagination({
  totalItems,
  itemsPerPage,
  currentPage,
  paginate,
}) {
  const totalPages = Math.ceil(
    totalItems / itemsPerPage
  );

  if (totalPages <= 1) return null;

  return (
    <nav className="mt-4">
      <ul className="pagination justify-content-center">

        {Array.from(
          { length: totalPages },
          (_, index) => (
            <li
              key={index}
              className={`page-item ${
                currentPage === index + 1
                  ? "active"
                  : ""
              }`}
            >
              <button
                className="page-link"
                onClick={() =>
                  paginate(index + 1)
                }
              >
                {index + 1}
              </button>
            </li>
          )
        )}

      </ul>
    </nav>
  );
}

export default CitationPagination;
