// =====================================
// Researchers Module
// Scientific Collaboration Network Analyzer
// =====================================

const researcherTable = document.getElementById("researcherTable");
const researcherForm = document.getElementById("researcherForm");

let researcherModal = new bootstrap.Modal(
    document.getElementById("researcherModal")
);

// ----------------------------
// Load Researchers
// ----------------------------

async function loadResearchers() {

    try {

        const response = await fetch(RESEARCHERS_API);

        const researchers = await response.json();

        researcherTable.innerHTML = "";

        researchers.forEach((researcher) => {

            researcherTable.innerHTML += `

                <tr>

                    <td>${researcher.id}</td>

                    <td>${researcher.full_name}</td>

                    <td>${researcher.department}</td>

                    <td>${researcher.designation}</td>

                    <td>${researcher.skills}</td>

                    <td>${researcher.research_interest}</td>

                    <td>${researcher.institution_id}</td>

                    <td>

                        <button
                            class="btn btn-warning btn-sm"
                            onclick="editResearcher(${researcher.id})">

                            <i class="bi bi-pencil-square"></i>

                            Edit

                        </button>

                    </td>

                </tr>

            `;

        });

    }

    catch (error) {

        console.log(error);

        alert("Unable to load researchers.");

    }

}

// ----------------------------
// Save Researcher
// ----------------------------

researcherForm.addEventListener("submit", saveResearcher);

async function saveResearcher(event) {

    event.preventDefault();

    const id = document.getElementById("researcherId").value;

    const researcherData = {

        full_name: document.getElementById("full_name").value,

        department: document.getElementById("department").value,

        skills: document.getElementById("skills").value,

        research_interest: document.getElementById("research_interest").value,

        designation: document.getElementById("designation").value,

        institution_id: parseInt(
            document.getElementById("institution_id").value
        )

    };

    try {

        let response;

        if (id === "") {

            response = await fetch(RESEARCHERS_API, {

                method: "POST",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify(researcherData)

            });

        }

        else {

            response = await fetch(RESEARCHERS_API + id, {

                method: "PUT",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify(researcherData)

            });

        }

        if (response.ok) {

            researcherModal.hide();

            researcherForm.reset();

            document.getElementById("researcherId").value = "";

            loadResearchers();

        }

        else {

            const error = await response.json();

            alert(error.detail || "Operation failed.");

        }

    }

    catch (error) {

        console.log(error);

        alert("Server Error.");

    }

}

// ----------------------------
// Edit Researcher
// ----------------------------

async function editResearcher(id) {

    try {

        const response = await fetch(RESEARCHERS_API + "/" + id);

        const researcher = await response.json();

        document.getElementById("researcherId").value = researcher.id;

        document.getElementById("full_name").value = researcher.full_name;

        document.getElementById("department").value = researcher.department;

        document.getElementById("skills").value = researcher.skills;

        document.getElementById("research_interest").value = researcher.research_interest;

        document.getElementById("designation").value = researcher.designation;

        document.getElementById("institution_id").value = researcher.institution_id;

        researcherModal.show();

    }

    catch (error) {

        console.log(error);

        alert("Unable to fetch researcher.");

    }

}

// ----------------------------
// Reset Form
// ----------------------------

document.getElementById("researcherModal")
.addEventListener("hidden.bs.modal", function () {

    researcherForm.reset();

    document.getElementById("researcherId").value = "";

});

// ----------------------------
// Initial Load
// ----------------------------

loadResearchers();