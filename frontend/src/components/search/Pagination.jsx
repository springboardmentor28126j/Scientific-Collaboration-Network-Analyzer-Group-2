export default function Pagination({
  page,
  pageSize,
  total,
  onPageChange,
}) {
  const totalPages = Math.ceil(total / pageSize);

  if (totalPages <= 1) return null;

  return (
    <nav className="mt-5">

      <ul className="pagination justify-content-center">

        <li
          className={`page-item ${
            page === 1 ? "disabled" : ""
          }`}
        >
          <button
            className="page-link"
            onClick={() =>
              onPageChange(page - 1)
            }
          >
            Previous
          </button>
        </li>

        {Array.from(
          { length: totalPages },
          (_, i) => i + 1
        ).map((number) => (

          <li
            key={number}
            className={`page-item ${
              page === number
                ? "active"
                : ""
            }`}
          >
            <button
              className="page-link"
              onClick={() =>
                onPageChange(number)
              }
            >
              {number}
            </button>
          </li>

        ))}

        <li
          className={`page-item ${
            page === totalPages
              ? "disabled"
              : ""
          }`}
        >
          <button
            className="page-link"
            onClick={() =>
              onPageChange(page + 1)
            }
          >
            Next
          </button>
        </li>

      </ul>

    </nav>
  );
}
