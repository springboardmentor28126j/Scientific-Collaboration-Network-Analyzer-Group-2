import React from "react";
import { useParams } from "react-router-dom";

function EditResearcher() {
  const { id } = useParams();

  return (
    <div className="container mt-5">
      <h2>Edit Researcher</h2>

      <div className="card p-4">
        <p>
          Editing researcher with ID: <strong>{id}</strong>
        </p>

        <p>This page is under development.</p>
      </div>
    </div>
  );
}

export default EditResearcher;
