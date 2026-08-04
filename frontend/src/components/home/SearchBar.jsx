import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = () => {
    if (!query.trim()) return;

    navigate(`/search?q=${encodeURIComponent(query.trim())}`);
  };

  return (
    <div className="input-group input-group-lg shadow">
      <input
        type="text"
        className="form-control"
        placeholder="Search researchers, publications, institutions..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleSearch();
          }
        }}
      />

      <button
        className="btn btn-warning fw-bold px-4"
        onClick={handleSearch}
      >
        🔍 Search
      </button>
    </div>
  );
}
