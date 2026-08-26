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

// Contextual AI assistance: recommendations live with the publication work,
// instead of on a separate page.
const publicationEsc = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const recommendationForm = document.getElementById("paperRecommendationForm");
recommendationForm?.addEventListener("submit", async event => {
    event.preventDefault();
    const query = document.getElementById("paperRecommendationQuery").value.trim();
    const host = document.getElementById("paperRecommendationResults");
    host.innerHTML = '<div class="small text-muted">Finding relevant publications...</div>';
    try {
        const response = await fetch(`http://127.0.0.1:8000/ai/paper-recommendations?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Unable to find recommendations");
        host.innerHTML = data.results.length ? `<div class="row g-2">${data.results.map(item => `<div class="col-md-6"><div class="border rounded-3 p-3 h-100"><div class="d-flex justify-content-between gap-2"><strong>${publicationEsc(item.title)}</strong><span class="badge text-bg-primary text-nowrap">${item.relevance_score}% match</span></div><div class="small text-muted mt-1">${publicationEsc(item.publication_type)} · ${publicationEsc(item.status)}</div><div class="mt-2">${item.matched_terms.map(term => `<span class="badge text-bg-light border text-dark me-1">${publicationEsc(term)}</span>`).join("")}</div></div></div>`).join("")}</div>` : '<div class="alert alert-light border mb-0">No matching publications were found. Try another keyword or add more publication abstracts.</div>';
    } catch (error) { host.innerHTML = `<div class="alert alert-danger mb-0">${publicationEsc(error.message)}</div>`; }
});

document.getElementById("suggestKeywordsButton")?.addEventListener("click", async () => {
    const host = document.getElementById("keywordSuggestionResults");
    host.innerHTML = '<span class="text-muted">Generating keyword suggestions...</span>';
    try {
        const response = await fetch("http://127.0.0.1:8000/ai/keyword-suggestions", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({title:document.getElementById("title").value, abstract:document.getElementById("abstract").value})});
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Unable to suggest keywords");
        host.innerHTML = data.keywords.length ? `<span class="text-muted me-2">Suggested:</span>${data.keywords.map(item => `<span class="badge text-bg-primary me-1">${publicationEsc(item)}</span>`).join("")}` : '<span class="text-muted">Add a title or abstract to receive suggestions.</span>';
    } catch (error) { host.innerHTML = `<span class="text-danger">${publicationEsc(error.message)}</span>`; }
});
