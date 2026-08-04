// ========================================
// Conference Management
// ========================================

const conferenceTable = document.getElementById("conferenceTable");
const conferenceForm = document.getElementById("conferenceForm");

const conferenceModal = new bootstrap.Modal(
    document.getElementById("conferenceModal")
);

// ========================================
// Load Conferences
// ========================================

async function loadConferences() {

    try {

        const response = await fetch(CONFERENCES_API + "/");

        if (!response.ok) {

            throw new Error();

        }

        const conferences = await response.json();

        conferenceTable.innerHTML = "";

        conferences.forEach(conf => {

            conferenceTable.innerHTML += `

                <tr>

                    <td>${conf.id}</td>

                    <td>${conf.name}</td>

                    <td>${conf.location || ""}</td>

                    <td>${conf.start_date}</td>

                    <td>${conf.end_date}</td>

                </tr>

            `;

        });

    }

    catch (error) {

        console.error(error);

        alert("Unable to load conferences.");

    }

}

// ========================================
// Add Conference
// ========================================

conferenceForm.addEventListener("submit", saveConference);

async function saveConference(event) {

    event.preventDefault();

    const conference = {

        name: document.getElementById("name").value.trim(),

        location: document.getElementById("location").value.trim(),

        start_date: document.getElementById("start_date").value,

        end_date: document.getElementById("end_date").value

    };

    try {

        const response = await fetch(CONFERENCES_API + "/", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(conference)

        });

        const result = await response.json();

        if (!response.ok) {

            alert(result.detail || "Unable to save conference.");

            return;

        }

        conferenceModal.hide();

        conferenceForm.reset();

        loadConferences();

    }

    catch (error) {

        console.error(error);

        alert("Server Error.");

    }

}

// ========================================
// Reset Form
// ========================================

document.getElementById("conferenceModal")
.addEventListener("hidden.bs.modal", function () {

    conferenceForm.reset();

});

// ========================================
// Initial Load
// ========================================

loadConferences();