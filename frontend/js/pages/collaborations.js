const COLLABORATIONS_API = "http://127.0.0.1:8000/collaborations/";
const collaborationModal = new bootstrap.Modal(document.getElementById("collaborationModal"));
const collaborationForm = document.getElementById("collaborationForm");
let collaborationRecords = [];

async function loadCollaborations(){
  const rows = document.getElementById("collaborationRows");
  try {
    const response = await fetch(COLLABORATIONS_API);
    if (!response.ok) throw new Error("Unable to load collaborations");
    collaborationRecords = await response.json();
    rows.innerHTML = collaborationRecords.length ? collaborationRecords.map(item => `<tr><td>${item.id}</td><td>${item.researcher1_id}</td><td>${item.researcher2_id}</td><td>${item.project || "-"}</td><td>${item.publication_id || "-"}</td><td class="text-end"><button class="btn btn-sm btn-outline-primary me-1" onclick="editCollaboration(${item.id})"><i class="bi bi-pencil"></i></button><button class="btn btn-sm btn-outline-danger" onclick="deleteCollaboration(${item.id})"><i class="bi bi-trash"></i></button></td></tr>`).join("") : '<tr><td colspan="6" class="text-center text-muted">No collaborations created yet.</td></tr>';
  } catch (error) { rows.innerHTML = `<tr><td colspan="6" class="text-center text-danger">${error.message}</td></tr>`; }
}

function resetForm(){ collaborationForm.reset(); document.getElementById("collaborationId").value=""; document.getElementById("modalTitle").textContent="Add Collaboration"; }
function editCollaboration(id){ const item = collaborationRecords.find(record => record.id === id); if (!item) return; document.getElementById("collaborationId").value=item.id; document.getElementById("researcher1Id").value=item.researcher1_id; document.getElementById("researcher2Id").value=item.researcher2_id; document.getElementById("project").value=item.project || ""; document.getElementById("publicationId").value=item.publication_id || ""; document.getElementById("modalTitle").textContent="Edit Collaboration"; collaborationModal.show(); }
async function deleteCollaboration(id){ if (!confirm("Delete this collaboration record?")) return; const response = await fetch(COLLABORATIONS_API + id, {method:"DELETE"}); if (!response.ok) { alert((await response.json()).detail || "Delete failed"); return; } loadCollaborations(); }
collaborationForm.addEventListener("submit", async event => { event.preventDefault(); const id=document.getElementById("collaborationId").value; const payload={researcher1_id:Number(document.getElementById("researcher1Id").value),researcher2_id:Number(document.getElementById("researcher2Id").value),project:document.getElementById("project").value.trim() || null,publication_id:document.getElementById("publicationId").value ? Number(document.getElementById("publicationId").value) : null}; if(payload.researcher1_id === payload.researcher2_id){alert("Choose two different researchers.");return;} const response=await fetch(COLLABORATIONS_API + (id || ""),{method:id?"PUT":"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)}); if(!response.ok){alert((await response.json()).detail || "Save failed");return;} collaborationModal.hide();loadCollaborations(); });
loadCollaborations();
