import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../css/reviews.css";

function Reviews() {
  const navigate = useNavigate();

  const [reviews, setReviews] = useState([]);
  const [filter, setFilter] = useState("All");
  const [loading, setLoading] = useState(true);

  const [feedback, setFeedback] = useState("");
  const [decision, setDecision] = useState("Accepted");
  const [selectedReview, setSelectedReview] = useState(null);

  const [publicationId, setPublicationId] = useState("");
  const [reviewerId, setReviewerId] = useState("");

  const token = localStorage.getItem("access_token");
  const role = localStorage.getItem("role");

  // =====================================================
  // CHECK LOGIN + LOAD REVIEWS
  // =====================================================

  useEffect(() => {
    const fetchReviews = async () => {
      // Check login
      if (!token) {
        alert("Please login again.");
        navigate("/login");
        return;
      }

      try {
        setLoading(true);

        const response = await axios.get(
          "http://127.0.0.1:8000/reviews/",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        setReviews(response.data);
      } catch (error) {
        console.log("Error loading reviews:", error);

        // Token expired / invalid
        if (error.response?.status === 401) {
          localStorage.removeItem("access_token");
          alert("Please login again.");
          navigate("/login");
        }

        // User does not have permission
        else if (error.response?.status === 403) {
          alert("You are not authorized to view reviews.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchReviews();
  }, [token, navigate]);

  // =====================================================
  // RELOAD REVIEWS
  // =====================================================

  const reloadReviews = async () => {
    if (!token) {
      alert("Please login again.");
      navigate("/login");
      return;
    }

    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/reviews/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setReviews(response.data);
    } catch (error) {
      console.log("Error reloading reviews:", error);

      if (error.response?.status === 401) {
        localStorage.removeItem("access_token");
        alert("Please login again.");
        navigate("/login");
      }
    }
  };

  // =====================================================
  // ASSIGN REVIEWER
  // =====================================================

  const handleAssignReviewer = async (event) => {
    event.preventDefault();

    if (!publicationId || !reviewerId) {
      alert("Please enter Publication ID and Reviewer ID.");
      return;
    }

    if (!token) {
      alert("Please login again.");
      navigate("/login");
      return;
    }

    try {
      await axios.post(
        "http://127.0.0.1:8000/reviews/",
        {
          publication_id: Number(publicationId),
          reviewer_id: Number(reviewerId),
          review_feedback: null,
          decision: "Pending",
          status: "Pending",
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      alert("Reviewer assigned successfully.");

      setPublicationId("");
      setReviewerId("");

      await reloadReviews();
    } catch (error) {
      console.log("Error assigning reviewer:", error);

      if (error.response?.status === 401) {
        localStorage.removeItem("access_token");
        alert("Please login again.");
        navigate("/login");
        return;
      }

      alert(
        error.response?.data?.detail ||
          "Unable to assign reviewer."
      );
    }
  };

  // =====================================================
  // FILTER REVIEWS
  // =====================================================

  const filteredReviews = reviews.filter((review) => {
    if (filter === "All") {
      return true;
    }

    return review.status === filter;
  });

  // =====================================================
  // SUBMIT REVIEW
  // =====================================================

  const handleSubmitReview = async () => {
    if (!selectedReview) {
      return;
    }

    if (!feedback.trim()) {
      alert("Please enter review feedback.");
      return;
    }

    if (!token) {
      alert("Please login again.");
      navigate("/login");
      return;
    }

    try {
      await axios.put(
        `http://127.0.0.1:8000/reviews/${selectedReview.review_id}`,
        {
          publication_id: selectedReview.publication_id,
          reviewer_id: selectedReview.reviewer_id,
          review_feedback: feedback,
          decision: decision,
          status: "Completed",
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      alert("Review submitted successfully.");

      setFeedback("");
      setDecision("Accepted");
      setSelectedReview(null);

      await reloadReviews();
    } catch (error) {
      console.log("Error submitting review:", error);

      if (error.response?.status === 401) {
        localStorage.removeItem("access_token");
        alert("Please login again.");
        navigate("/login");
        return;
      }

      alert(
        error.response?.data?.detail ||
          "Unable to submit review."
      );
    }
  };

  // =====================================================
  // CANCEL REVIEW
  // =====================================================

  const cancelReview = () => {
    setSelectedReview(null);
    setFeedback("");
    setDecision("Accepted");
  };

  // =====================================================
  // UI
  // =====================================================

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "30px",
        backgroundColor: "#f4f8fc",
        boxSizing: "border-box",
      }}
    >
      {/* PAGE TITLE */}

      <h1
        style={{
          color: "#1f4e9e",
          textAlign: "center",
          marginBottom: "10px",
        }}
      >
        Review Management
      </h1>

      <p
        style={{
          textAlign: "center",
          color: "#555",
          fontSize: "17px",
          marginBottom: "30px",
        }}
      >
        Manage assigned, pending, and completed publication reviews.
      </p>

      {/* =====================================================
          ASSIGN REVIEWER
          SYSTEM ADMIN + INSTITUTION ADMIN
          ===================================================== */}

      {(role === "System Admin" ||
        role === "Institution Admin") && (
        <div
          style={{
            backgroundColor: "white",
            padding: "25px",
            borderRadius: "10px",
            border: "1px solid #ddd",
            marginBottom: "30px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          }}
        >
          <h2
            style={{
              color: "#1f4e9e",
              marginBottom: "20px",
            }}
          >
            Assign Reviewer
          </h2>

          <form onSubmit={handleAssignReviewer}>
            {/* PUBLICATION ID */}

            <div style={{ marginBottom: "15px" }}>
              <label>
                <strong>Publication ID</strong>
              </label>

              <br />

              <input
                type="number"
                value={publicationId}
                onChange={(e) =>
                  setPublicationId(e.target.value)
                }
                placeholder="Enter Publication ID"
                required
                style={{
                  width: "300px",
                  maxWidth: "100%",
                  padding: "10px",
                  marginTop: "8px",
                  boxSizing: "border-box",
                }}
              />
            </div>

            {/* REVIEWER ID */}

            <div style={{ marginBottom: "15px" }}>
              <label>
                <strong>Reviewer ID</strong>
              </label>

              <br />

              <input
                type="number"
                value={reviewerId}
                onChange={(e) =>
                  setReviewerId(e.target.value)
                }
                placeholder="Enter Reviewer ID"
                required
                style={{
                  width: "300px",
                  maxWidth: "100%",
                  padding: "10px",
                  marginTop: "8px",
                  boxSizing: "border-box",
                }}
              />
            </div>

            <button
              type="submit"
              style={primaryButtonStyle}
            >
              Assign Reviewer
            </button>
          </form>
        </div>
      )}

      {/* =====================================================
          FILTER BUTTONS
          ===================================================== */}

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "10px",
          marginBottom: "25px",
          flexWrap: "wrap",
        }}
      >
        <button
          onClick={() => setFilter("All")}
          style={
            filter === "All"
              ? activeFilterStyle
              : filterStyle
          }
        >
          All
        </button>

        <button
          onClick={() => setFilter("Pending")}
          style={
            filter === "Pending"
              ? activeFilterStyle
              : filterStyle
          }
        >
          Pending
        </button>

        <button
          onClick={() => setFilter("Completed")}
          style={
            filter === "Completed"
              ? activeFilterStyle
              : filterStyle
          }
        >
          Completed
        </button>
      </div>

      {/* =====================================================
          REVIEWS TABLE
          ===================================================== */}

      {loading ? (
        <p
          style={{
            textAlign: "center",
            fontSize: "18px",
          }}
        >
          Loading reviews...
        </p>
      ) : filteredReviews.length === 0 ? (
        <p
          style={{
            textAlign: "center",
            fontSize: "18px",
            color: "#555",
          }}
        >
          No reviews found.
        </p>
      ) : (
        <div
          style={{
            width: "100%",
            overflowX: "auto",
            backgroundColor: "white",
            borderRadius: "8px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          }}
        >
          <table
            style={{
              width: "100%",
              minWidth: "900px",
              borderCollapse: "collapse",
              tableLayout: "fixed",
            }}
          >
            <thead>
              <tr>
                <th
                  style={{
                    ...tableHeaderStyle,
                    width: "90px",
                  }}
                >
                  Review ID
                </th>

                <th
                  style={{
                    ...tableHeaderStyle,
                    width: "110px",
                  }}
                >
                  Publication ID
                </th>

                <th
                  style={{
                    ...tableHeaderStyle,
                    width: "110px",
                  }}
                >
                  Reviewer ID
                </th>

                <th
                  style={{
                    ...tableHeaderStyle,
                    width: "35%",
                  }}
                >
                  Feedback
                </th>

                <th
                  style={{
                    ...tableHeaderStyle,
                    width: "130px",
                  }}
                >
                  Decision
                </th>

                <th
                  style={{
                    ...tableHeaderStyle,
                    width: "120px",
                  }}
                >
                  Status
                </th>

                {role === "Reviewer" && (
                  <th
                    style={{
                      ...tableHeaderStyle,
                      width: "150px",
                    }}
                  >
                    Action
                  </th>
                )}
              </tr>
            </thead>

            <tbody>
              {filteredReviews.map((review) => (
                <tr key={review.review_id}>
                  <td style={tableCellStyle}>
                    {review.review_id}
                  </td>

                  <td style={tableCellStyle}>
                    {review.publication_id}
                  </td>

                  <td style={tableCellStyle}>
                    {review.reviewer_id}
                  </td>

                  <td
                    style={{
                      ...tableCellStyle,
                      textAlign: "left",
                      wordBreak: "break-word",
                      whiteSpace: "normal",
                    }}
                  >
                    {review.review_feedback || "-"}
                  </td>

                  <td style={tableCellStyle}>
                    {review.decision}
                  </td>

                  <td style={tableCellStyle}>
                    {review.status}
                  </td>

                  {/* REVIEWER ACTION */}

                  {role === "Reviewer" && (
                    <td style={tableCellStyle}>
                      {review.status === "Pending" ? (
                        <button
                          onClick={() => {
                            setSelectedReview(review);
                            setFeedback("");
                            setDecision("Accepted");
                          }}
                          style={primaryButtonStyle}
                        >
                          Submit Review
                        </button>
                      ) : (
                        <span
                          style={{
                            color: "#555",
                          }}
                        >
                          Completed
                        </span>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* =====================================================
          SUBMIT REVIEW FORM
          ===================================================== */}

      {selectedReview && (
        <div
          style={{
            marginTop: "30px",
            padding: "25px",
            backgroundColor: "white",
            borderRadius: "10px",
            border: "1px solid #ddd",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          }}
        >
          <h2
            style={{
              color: "#1f4e9e",
              marginBottom: "20px",
            }}
          >
            Submit Review
          </h2>

          <p>
            <strong>Review ID:</strong>{" "}
            {selectedReview.review_id}
          </p>

          <p>
            <strong>Publication ID:</strong>{" "}
            {selectedReview.publication_id}
          </p>

          <p>
            <strong>Reviewer ID:</strong>{" "}
            {selectedReview.reviewer_id}
          </p>

          {/* FEEDBACK */}

          <label>
            <strong>Feedback</strong>
          </label>

          <textarea
            value={feedback}
            onChange={(e) =>
              setFeedback(e.target.value)
            }
            placeholder="Enter your review feedback"
            rows="6"
            style={{
              width: "100%",
              padding: "12px",
              marginTop: "10px",
              marginBottom: "20px",
              boxSizing: "border-box",
              fontSize: "16px",
              border: "1px solid #ccc",
              borderRadius: "5px",
              resize: "vertical",
            }}
          />

          {/* DECISION */}

          <label>
            <strong>Decision</strong>
          </label>

          <br />

          <select
            value={decision}
            onChange={(e) =>
              setDecision(e.target.value)
            }
            style={{
              padding: "10px",
              marginTop: "10px",
              marginBottom: "20px",
              minWidth: "200px",
            }}
          >
            <option value="Accepted">
              Accepted
            </option>

            <option value="Rejected">
              Rejected
            </option>

            <option value="Revision Required">
              Revision Required
            </option>
          </select>

          <br />

          <button
            onClick={handleSubmitReview}
            style={primaryButtonStyle}
          >
            Submit Review
          </button>

          <button
            onClick={cancelReview}
            style={cancelButtonStyle}
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

// =====================================================
// STYLES
// =====================================================

const tableHeaderStyle = {
  padding: "14px 10px",
  border: "1px solid #ddd",
  backgroundColor: "#1f78d1",
  color: "white",
  textAlign: "center",
  verticalAlign: "middle",
  wordBreak: "break-word",
};

const tableCellStyle = {
  padding: "14px 10px",
  border: "1px solid #ddd",
  textAlign: "center",
  verticalAlign: "middle",
  wordBreak: "break-word",
};

const primaryButtonStyle = {
  padding: "10px 18px",
  backgroundColor: "#1976d2",
  color: "white",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer",
  fontSize: "15px",
};

const cancelButtonStyle = {
  padding: "10px 18px",
  marginLeft: "10px",
  backgroundColor: "#777",
  color: "white",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer",
  fontSize: "15px",
};

const filterStyle = {
  padding: "10px 20px",
  border: "1px solid #aaa",
  borderRadius: "5px",
  backgroundColor: "#eee",
  cursor: "pointer",
  fontSize: "15px",
};

const activeFilterStyle = {
  padding: "10px 20px",
  border: "1px solid #1976d2",
  borderRadius: "5px",
  backgroundColor: "#1976d2",
  color: "white",
  cursor: "pointer",
  fontSize: "15px",
};

export default Reviews;