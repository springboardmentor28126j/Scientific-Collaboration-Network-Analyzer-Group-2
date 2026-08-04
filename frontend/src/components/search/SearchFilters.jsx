import { useState } from "react";

export default function SearchFilters({
  filters,
  setFilters,
}) {
  const update = (field, value) => {
    setFilters({
      ...filters,
      [field]: value,
    });
  };

  return (
    <div className="card shadow border-0 rounded-4">
      <div className="card-body">

        <h4 className="fw-bold mb-4">
          Filters
        </h4>

        {/* Search Type */}

        <div className="mb-3">
          <label className="form-label">
            Search Type
          </label>

          <select
            className="form-select"
            value={filters.type}
            onChange={(e) =>
              update("type", e.target.value)
            }
          >
            <option value="all">All</option>
            <option value="researchers">Researchers</option>
            <option value="publications">Publications</option>
            <option value="institutions">Institutions</option>
          </select>
        </div>

        {/* Year */}

        <div className="mb-3">
          <label className="form-label">
            Publication Year
          </label>

          <input
            type="number"
            className="form-control"
            value={filters.year}
            onChange={(e) =>
              update("year", e.target.value)
            }
          />
        </div>

        {/* Publication Type */}

        <div className="mb-3">
          <label className="form-label">
            Publication Type
          </label>

          <select
            className="form-select"
            value={filters.publicationType}
            onChange={(e) =>
              update(
                "publicationType",
                e.target.value
              )
            }
          >
            <option value="">Any</option>
            <option value="Journal">
              Journal
            </option>
            <option value="Conference">
              Conference
            </option>
            <option value="Book">
              Book
            </option>
          </select>
        </div>

        {/* Status */}

        <div className="mb-3">
          <label className="form-label">
            Status
          </label>

          <select
            className="form-select"
            value={filters.status}
            onChange={(e) =>
              update("status", e.target.value)
            }
          >
            <option value="">Any</option>
            <option value="Published">
              Published
            </option>
            <option value="Accepted">
              Accepted
            </option>
            <option value="Draft">
              Draft
            </option>
          </select>
        </div>

        {/* Institution */}

        <div className="mb-3">
          <label className="form-label">
            Institution
          </label>

          <input
            className="form-control"
            value={filters.institution}
            onChange={(e) =>
              update(
                "institution",
                e.target.value
              )
            }
          />
        </div>

        {/* Sort */}

        <div className="mb-3">
          <label className="form-label">
            Sort
          </label>

          <select
            className="form-select"
            value={filters.sort}
            onChange={(e) =>
              update("sort", e.target.value)
            }
          >
            <option value="relevance">
              Relevance
            </option>

            <option value="newest">
              Newest
            </option>

            <option value="oldest">
              Oldest
            </option>

            <option value="citations">
              Citations
            </option>
          </select>
        </div>

      </div>
    </div>
  );
}
