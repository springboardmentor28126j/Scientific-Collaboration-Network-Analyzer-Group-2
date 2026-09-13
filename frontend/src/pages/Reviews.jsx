import { useEffect, useState } from "react";
import axios from "axios";

function Reviews() {
  const [reviews, setReviews] = useState([]);
  const [filter, setFilter] = useState("All");
  const [loading, setLoading] = useState(true);
useEffect(() => {
  const loadReviews = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/reviews/"
      );

      setReviews(response.data);
    } catch (error) {
      console.log("Error loading reviews:", error);
    } finally {
      setLoading(false);
    }
  };

  loadReviews();
}, []);

  const filteredReviews = reviews.filter((review) => {
    if (filter === "All") return true;
    return review.status === filter;
  });

  return (
    <div style={{ padding: "40px", backgroundColor: "#f4f8fc", minHeight: "100vh" }}>
      
      <h1
  style={{
    color: "#1f4e9e",
    marginBottom: "20px",
    lineHeight: "1.2",
  }}
>
  Review Management
</h1>

<p
  style={{
    color: "#555",
    fontSize: "17px",
    marginTop: "0",
    marginBottom: "25px",
  }}
  
>
    Manage assigned, pending, and completed publication reviews.
</p>

      <div style={{ marginBottom: "25px" }}>
        <button
          onClick={() => setFilter("All")}
          style={{ marginRight: "10px", padding: "10px 18px" }}
        >
          All
        </button>

        <button
          onClick={() => setFilter("Pending")}
          style={{ marginRight: "10px", padding: "10px 18px" }}
        >
          Pending
        </button>

        <button
          onClick={() => setFilter("Completed")}
          style={{ padding: "10px 18px" }}
        >
          Completed
        </button>
      </div>

      {loading ? (
        <p>Loading reviews...</p>
      ) : filteredReviews.length === 0 ? (
        <p>No reviews found.</p>
      ) : (
        <table
          style={{
            width: "100%",
            backgroundColor: "white",
            borderCollapse: "collapse",
          }}
        >
          <thead>
            <tr>
              <th style={{ padding: "12px", border: "1px solid #ddd" }}>
                Review ID
              </th>

              <th style={{ padding: "12px", border: "1px solid #ddd" }}>
                Publication ID
              </th>

              <th style={{ padding: "12px", border: "1px solid #ddd" }}>
                Reviewer ID
              </th>

              <th style={{ padding: "12px", border: "1px solid #ddd" }}>
                Feedback
              </th>

              <th style={{ padding: "12px", border: "1px solid #ddd" }}>
                Decision
              </th>

              <th style={{ padding: "12px", border: "1px solid #ddd" }}>
                Status
              </th>
            </tr>
          </thead>

          <tbody>
            {filteredReviews.map((review) => (
              <tr key={review.review_id}>
                <td style={{ padding: "12px", border: "1px solid #ddd" }}>
                  {review.review_id}
                </td>

                <td style={{ padding: "12px", border: "1px solid #ddd" }}>
                  {review.publication_id}
                </td>

                <td style={{ padding: "12px", border: "1px solid #ddd" }}>
                  {review.reviewer_id}
                </td>

                <td style={{ padding: "12px", border: "1px solid #ddd" }}>
                  {review.review_feedback}
                </td>

                <td style={{ padding: "12px", border: "1px solid #ddd" }}>
                  {review.decision}
                </td>

                <td style={{ padding: "12px", border: "1px solid #ddd" }}>
                  {review.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Reviews;