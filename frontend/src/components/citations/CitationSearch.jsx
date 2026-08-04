function CitationSearch({
  search,
  setSearch,
}) {
  return (
    <div className="mb-4">
      <input
        className="form-control"
        placeholder="Search citations..."
        value={search}
        onChange={(e) =>
          setSearch(e.target.value)
        }
      />
    </div>
  );
}

export default CitationSearch;
