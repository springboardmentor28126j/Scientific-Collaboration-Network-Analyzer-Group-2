import React, { useState, useEffect } from "react";
import axios from "axios";

function Collaboration() {
  const [researcherId, setResearcherId] = useState("");
  const [requests, setRequests] = useState([]);

  const sendRequest = async () => {
    try {
      const token = localStorage.getItem("access_token");

      await axios.post(
        "http://127.0.0.1:8000/collaborations/request",
        {
          receiver_id: researcherId,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      alert("Collaboration Request Sent Successfully!");
      setResearcherId("");
    } catch (error) {
      console.error(error);
      console.log(error.response?.data);
      alert("Failed to send collaboration request");
    }
  };
  const getPendingRequests = async () => {
    console.log("Pending request function called");
    try {
      const token = localStorage.getItem("access_token");

      const response = await axios.get(
        "http://127.0.0.1:8000/collaborations/pending",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log(response.data);

      setRequests(response.data);

    } catch (error) {
      console.error(error);
    }
  };
  useEffect(() => {
    getPendingRequests();
  }, []);
  const acceptRequest = async (id) => {

    try {

      const token = localStorage.getItem("access_token");

      await axios.put(
        `http://127.0.0.1:8000/collaborations/${id}/accept`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );


      alert("Request Accepted");

      await getPendingRequests();


    }
    catch (error) {

      console.error(error);

      alert("Accept failed");

    }

  };

  const rejectRequest = async (id) => {

    try {

      const token = localStorage.getItem("access_token");

      await axios.put(
        `http://127.0.0.1:8000/collaborations/${id}/reject`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      alert("Request Rejected");

      await getPendingRequests();

    }
    catch (error) {

      console.error(error);
      alert("Reject failed");

    }

  };
  return (
    <div className="container mt-5">
      <h2>Collaboration Management</h2>

      <div className="card p-4 mt-3">
        <h4>Send Collaboration Request</h4>

        <input
          className="form-control mt-3"
          placeholder="Enter Researcher ID"
          value={researcherId}
          onChange={(e) => setResearcherId(e.target.value)}
        />

        <button
          className="btn btn-primary mt-3"
          onClick={sendRequest}
        >
          Send Request
        </button>
      </div>

      <div className="card p-4 mt-4">

        <h4>Pending Requests</h4>

        {
          requests.length === 0 ? (
            <p>No Pending Requests</p>
          )
            :
            (
              requests.map((request) => (
                <div key={request.id} className="border p-3 mt-3">

                  <p>
                    Request ID: {request.id}
                  </p>

                  <p>
                    From: {request.sender_id}
                  </p>


                  <button
                    className="btn btn-success"
                    onClick={() => acceptRequest(request.id)}
                  >
                    Accept
                  </button>


                  <button
                    className="btn btn-danger ms-2"
                    onClick={() => rejectRequest(request.id)}
                  >
                    Reject
                  </button>


                </div>
              ))
            )

        }

      </div>
    </div>
  );
}

export default Collaboration;