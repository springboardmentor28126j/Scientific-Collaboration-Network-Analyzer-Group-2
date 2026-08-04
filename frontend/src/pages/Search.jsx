import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { search } from "../services/searchService";

import SearchFilters from "../components/search/SearchFilters";
import SearchResults from "../components/search/SearchResults";

export default function Search() {
  const [searchParams] = useSearchParams();

  const keyword = searchParams.get("q") || "";

  const [page, setPage] = useState(1);

  const [loading, setLoading] = useState(false);

  const [results, setResults] = useState({
    researchers: [],
    publications: [],
    institutions: [],
    total: 0,
    page_size: 10,
  });

  const [filters, setFilters] = useState({
    type: "all",
    year: "",
    publicationType: "",
    status: "",
    institution: "",
    sort: "relevance",
  });

  useEffect(() => {
    setPage(1);
  }, [keyword]);

  useEffect(() => {
    if (!keyword.trim()) return;

    const loadSearch = async () => {
      try {
        setLoading(true);

        const data = await search({
          q: keyword,
          page,
          pageSize: 10,
          ...filters,
        });

        setResults(data);
      } catch (error) {
        console.error("Search failed:", error);

        setResults({
          researchers: [],
          publications: [],
          institutions: [],
          total: 0,
          page_size: 10,
        });
      } finally {
        setLoading(false);
      }
    };

    loadSearch();
  }, [keyword, page, filters]);

  return (
    <div className="container py-5">

      <div className="row">

        {/* Sidebar */}

        <div className="col-lg-3 mb-4">
          <SearchFilters
            filters={filters}
            setFilters={setFilters}
          />
        </div>

        {/* Results */}

        <div className="col-lg-9">
          <SearchResults
            loading={loading}
            keyword={keyword}
            results={results}
            page={page}
            setPage={setPage}
          />
        </div>

      </div>

    </div>
  );
}
