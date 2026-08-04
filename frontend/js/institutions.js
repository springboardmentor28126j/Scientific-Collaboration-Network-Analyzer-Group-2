// =========================================
// Institution Management
// Scientific Collaboration Network Analyzer
// =========================================

const institutionTable = document.getElementById("institutionTable");
const institutionForm = document.getElementById("institutionForm");

const institutionModal = new bootstrap.Modal(
    document.getElementById("institutionModal")
);

// =========================================
// Load All Institutions
// =========================================

async function loadInstitutions() {

    try {

        const response = await fetch(INSTITUTIONS_API + "/");

        if (!response.ok) {
            throw new Error("Unable to fetch institutions.");
        }

        const institutions = await response.json();

        institutionTable.innerHTML = "";

        institutions.forEach(institution => {

            institutionTable.innerHTML += `

                <tr>

                    <td>${institution.id}</td>

                    <td>${institution.name}</td>

                    <td>${institution.address || ""}</td>

                    <td>${institution.website || ""}</td>

                    <td>${institution.contact_email || ""}</td>

                    <td>

                        <button
                            class="btn btn-warning btn-sm me-1"
                            onclick="editInstitution(${institution.id})">

                            <i class="bi bi-pencil-square"></i>

                            Edit

                        </button>

                        <button
                            class="btn btn-danger btn-sm"
                            onclick="deleteInstitution(${institution.id})">

                            <i class="bi bi-trash"></i>

                            Delete

                        </button>

                    </td>

                </tr>

            `;

        });

    }

    catch (error) {

        console.error(error);

        alert("Unable to load institutions.");

    }

}

// =========================================
// Save Institution
// =========================================

institutionForm.addEventListener("submit", saveInstitution);

async function saveInstitution(event) {

    event.preventDefault();

    const id = document.getElementById("institutionId").value;

    const institution = {

        name: document.getElementById("name").value.trim(),

        address: document.getElementById("address").value.trim(),

        website: document.getElementById("website").value.trim(),

        contact_email: document.getElementById("contact_email").value.trim()

    };

    try {

        let response;

        if (id === "") {

            response = await fetch(INSTITUTIONS_API + "/", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(institution)

            });

        }

        else {

            response = await fetch(INSTITUTIONS_API + "/" + id, {

                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(institution)

            });

        }

        const result = await response.json();

        if (!response.ok) {

            alert(result.detail || "Operation Failed.");

            return;

        }

        institutionModal.hide();

        institutionForm.reset();

        document.getElementById("institutionId").value = "";

        loadInstitutions();

    }

    catch (error) {

        console.error(error);

        alert("Server Error.");

    }

}

// =========================================
// Edit Institution
// =========================================

async function editInstitution(id) {

    try {

        const response = await fetch(INSTITUTIONS_API + "/" + id);

        if (!response.ok) {

            alert("Institution not found.");

            return;

        }

        const institution = await response.json();

        document.getElementById("institutionId").value = institution.id;

        document.getElementById("name").value = institution.name;

        document.getElementById("address").value = institution.address || "";

        document.getElementById("website").value = institution.website || "";

        document.getElementById("contact_email").value = institution.contact_email || "";

        institutionModal.show();

    }

    catch (error) {

        console.error(error);

        alert("Unable to load institution.");

    }

}

// =========================================
// Delete Institution
// =========================================

async function deleteInstitution(id) {

    const confirmDelete = confirm(
        "Are you sure you want to delete this institution?"
    );

    if (!confirmDelete) {

        return;

    }

    try {

        const response = await fetch(INSTITUTIONS_API + "/" + id, {

            method: "DELETE"

        });

        const result = await response.json();

        if (!response.ok) {

            alert(result.detail || "Delete Failed.");

            return;

        }

        alert(result.message);

        loadInstitutions();

    }

    catch (error) {

        console.error(error);

        alert("Server Error.");

    }

}

// =========================================
// Reset Modal
// =========================================

document.getElementById("institutionModal")
.addEventListener("hidden.bs.modal", function () {

    institutionForm.reset();

    document.getElementById("institutionId").value = "";

});

// =========================================
// Initial Load
// =========================================

loadInstitutions();