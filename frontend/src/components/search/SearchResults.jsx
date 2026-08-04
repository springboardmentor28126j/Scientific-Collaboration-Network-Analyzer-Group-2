import SearchCard from "./SearchCard";
import Pagination from "./Pagination";

export default function SearchResults({
  loading,
  keyword,
  results,
  page,
  setPage,
}) {
  if (loading) {
    return (
      <div className="text-center py-5">
        <div
          className="spinner-border text-primary"
          role="status"
        >
          <span className="visually-hidden">
            Loading...
          </span>
        </div>

        <p className="mt-3 fs-5">
          Searching...
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}

      <div className="mb-4">
        <h3 className="fw-bold">
          Search Results
        </h3>

        <p className="text-muted">
          {results.total} result{results.total !== 1 ? "s" : ""} found for{" "}
          <strong>"{keyword}"</strong>
        </p>
      </div>

      {/* Researchers */}

      {results.researchers?.length > 0 && (
        <>
          <h4 className="mb-3">
            👤 Researchers
          </h4>

          {results.researchers.map((r) => (
            <SearchCard
              key={r.id}
              id={r.id}
              type="researcher"
              title={r.name}
              subtitle={r.department}
              badge={r.institution}
              description={
                r.bio ||
                `${r.publication_count} Publications • ${r.experience} Years Experience`
              }
            />
          ))}
        </>
      )}

      {/* Publications */}

      {results.publications?.length > 0 && (
        <>
          <h4 className="mt-5 mb-3">
            📄 Publications
          </h4>

          {results.publications.map((p) => (
            <SearchCard
              key={p.id}
              id={p.id}
              type="publication"
              title={p.title}
              subtitle={
                p.authors?.length
                  ? p.authors.join(", ")
                  : "Unknown Author"
              }
              badge={p.publication_type}
              description={`${p.publication_year} • ${p.citation_count} Citations`}
            />
          ))}
        </>
      )}

      {/* Institutions */}

      {results.institutions?.length > 0 && (
        <>
          <h4 className="mt-5 mb-3">
            🏛 Institutions
          </h4>

          {results.institutions.map((i) => (
            <SearchCard
              key={i.id}
              id={i.id}
              type="institution"
              title={i.name}
              subtitle={`${i.city || ""}${i.city && i.country ? ", " : ""}${i.country || ""}`}
              badge={i.abbreviation}
              description={`${i.department_count} Departments`}
            />
          ))}
        </>
      )}

      {/* Empty State */}

      {!loading &&
        results.researchers?.length === 0 &&
        results.publications?.length === 0 &&
        results.institutions?.length === 0 && (
          <div className="alert alert-warning mt-4">
            <h5>No results found.</h5>
            <p className="mb-0">
              Try searching with different keywords or remove some filters.
            </p>
          </div>
        )}

      {/* Pagination */}

      <Pagination
        page={page}
        pageSize={results.page_size}
        total={results.total}
        onPageChange={setPage}
      />
    </div>
  );
}
