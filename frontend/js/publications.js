// ======================================
// Publication Management
// Scientific Collaboration Network Analyzer
// ======================================

const publicationTable = document.getElementById("publicationTable");
const publicationForm = document.getElementById("publicationForm");

const publicationModal = new bootstrap.Modal(
    document.getElementById("publicationModal")
);

// ======================================
// Load Publications
// ======================================

async function loadPublications() {

    try {

        const response = await fetch(PUBLICATIONS_API + "/");

        if (!response.ok) {
            throw new Error("Unable to load publications.");
        }

        const publications = await response.json();

        publicationTable.innerHTML = "";

        publications.forEach(pub => {

            publicationTable.innerHTML += `

                <tr>

                    <td>${pub.id}</td>

                    <td>${pub.title}</td>

                    <td>${pub.publication_type}</td>

                    <td>${pub.status}</td>

                    <td>${pub.doi || "-"}</td>

                    <td>${pub.institution_id ?? "-"}</td>

                    <td>

                        <button
                            class="btn btn-warning btn-sm me-1"
                            onclick="editPublication(${pub.id})">

                            <i class="bi bi-pencil-square"></i>

                        </button>

                        <button
                            class="btn btn-danger btn-sm"
                            onclick="deletePublication(${pub.id})">

                            <i class="bi bi-trash"></i>

                        </button>

                    </td>

                </tr>

            `;

        });

    }

    catch (error) {

        console.error(error);

        alert("Unable to load publications.");

    }

}

// ======================================
// Save Publication
// ======================================

publicationForm.addEventListener("submit", savePublication);

async function savePublication(event) {

    event.preventDefault();

    const id = document.getElementById("publicationId").value;

    const publication = {

        title: document.getElementById("title").value.trim(),

        abstract: document.getElementById("abstract").value.trim(),

        publication_type: document.getElementById("publication_type").value,

        status: document.getElementById("status").value,

        doi: document.getElementById("doi").value.trim(),

        publication_date:
            document.getElementById("publication_date").value || null,

        journal_or_venue:
            document.getElementById("journal_or_venue").value.trim(),

        institution_id:
            document.getElementById("institution_id").value === ""
            ? null
            : parseInt(document.getElementById("institution_id").value),

        researcher_ids: []

    };

    try {

        let response;

        if (id === "") {

            response = await fetch(PUBLICATIONS_API + "/", {

                method: "POST",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify(publication)

            });

        }

        else {

            response = await fetch(PUBLICATIONS_API + "/" + id, {

                method: "PUT",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify(publication)

            });

        }

        const result = await response.json();

        if (!response.ok) {

            alert(result.detail || "Operation failed.");

            return;

        }

        publicationModal.hide();

        publicationForm.reset();

        document.getElementById("publicationId").value = "";

        loadPublications();

    }

    catch (error) {

        console.error(error);

        alert("Server Error.");

    }

}

// ======================================
// Edit Publication
// ======================================

async function editPublication(id) {

    try {

        const response = await fetch(PUBLICATIONS_API + "/" + id);

        if (!response.ok) {

            alert("Publication not found.");

            return;

        }

        const pub = await response.json();

        document.getElementById("publicationId").value = pub.id;

        document.getElementById("title").value = pub.title;

        document.getElementById("abstract").value = pub.abstract || "";

        document.getElementById("publication_type").value =
            pub.publication_type;

        document.getElementById("status").value = pub.status;

        document.getElementById("doi").value = pub.doi || "";

        document.getElementById("institution_id").value =
            pub.institution_id || "";

        document.getElementById("publication_date").value =
            pub.publication_date || "";

        document.getElementById("journal_or_venue").value =
            pub.journal_or_venue || "";

        publicationModal.show();

    }

    catch (error) {

        console.error(error);

        alert("Unable to load publication.");

    }

}

// ======================================
// Delete Publication
// ======================================

async function deletePublication(id) {

    if (!confirm("Delete this publication?")) {

        return;

    }

    try {

        const response = await fetch(PUBLICATIONS_API + "/" + id, {

            method: "DELETE"

        });

        const result = await response.json();

        if (!response.ok) {

            alert(result.detail || "Delete failed.");

            return;

        }

        alert(result.message);

        loadPublications();

    }

    catch (error) {

        console.error(error);

        alert("Server Error.");

    }

}

// ======================================
// Reset Form
// ======================================

document.getElementById("publicationModal")
.addEventListener("hidden.bs.modal", function () {

    publicationForm.reset();

    document.getElementById("publicationId").value = "";

});

// ======================================
// Initial Load
// ======================================

loadPublications();