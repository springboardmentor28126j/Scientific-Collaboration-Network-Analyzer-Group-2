import { Link } from "react-router-dom";

import {
  joinConference,
  leaveConference,
} from "../../services/conferenceService";

import {
  isSystemAdmin,
  isInstitutionAdmin,
  isResearcher,
} from "../../utils/auth";

function ConferenceCard({
  conference,
  onDelete,
  refreshConferences,
}) {

  const canManage =
    isSystemAdmin() || isInstitutionAdmin();

  const researcher = isResearcher();

  const handleJoin = async () => {
    try {
      await joinConference(conference.id);

      alert("Successfully joined conference.");

      if (refreshConferences) {
        refreshConferences();
      }
    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        alert(err.response.data.detail);
      } else {
        alert("Unable to join conference.");
      }
    }
  };

  const handleLeave = async () => {
    try {
      await leaveConference(conference.id);

      alert("Successfully left conference.");

      if (refreshConferences) {
        refreshConferences();
      }
    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        alert(err.response.data.detail);
      } else {
        alert("Unable to leave conference.");
      }
    }
  };

  return (
    <div className="card shadow h-100">

      <div className="card-body">

        <h4 className="card-title text-primary">
          {conference.title}
        </h4>

        <hr />

        <p>
          <strong>Location:</strong>
          <br />
          {conference.location || "Not specified"}
        </p>

        <p>
          <strong>Date:</strong>
          <br />
          {conference.conference_date || "Not specified"}
        </p>

        <p>
          <strong>Description:</strong>
          <br />
          {conference.description || "No description"}
        </p>

        <p>
          <strong>Participants:</strong>{" "}
          {conference.participant_count}
        </p>

      </div>

      <div className="card-footer bg-white">

        {canManage && (
          <div className="d-flex justify-content-between">

            <Link
              to={`/conferences/edit/${conference.id}`}
              className="btn btn-warning"
            >
              Edit
            </Link>

            <button
              className="btn btn-danger"
              onClick={() => onDelete(conference.id)}
            >
              Delete
            </button>

          </div>
        )}

        {researcher && (
          <div className="d-flex justify-content-between">

            <button
              className="btn btn-success"
              onClick={handleJoin}
            >
              Join
            </button>

            <button
              className="btn btn-secondary"
              onClick={handleLeave}
            >
              Leave
            </button>

          </div>
        )}

      </div>

    </div>
  );
}

export default ConferenceCard;
