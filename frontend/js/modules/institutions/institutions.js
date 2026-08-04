// =======================================
// Institutions Module
// Scientific Collaboration Network Analyzer
// =======================================


const institutionTable =
document.getElementById("institutionTable");


const institutionForm =
document.getElementById("institutionForm");



let institutionModal =
new bootstrap.Modal(
document.getElementById("institutionModal")
);





// ===============================
// Load Institutions
// ===============================


async function loadInstitutions(){


try{


const response =
await fetch(INSTITUTIONS_API);



const institutions =
await response.json();




institutionTable.innerHTML="";



institutions.forEach((institution)=>{



institutionTable.innerHTML += `


<tr>


<td>
${institution.id}
</td>


<td>
${institution.name}
</td>


<td>
${institution.address || "-"}
</td>


<td>

<a href="${institution.website || '#'}"
target="_blank">

${institution.website || "-"}

</a>


</td>



<td>
${institution.contact_email || "-"}
</td>



<td>


<button

class="btn btn-warning btn-sm me-2"

onclick="editInstitution(${institution.id})">


<i class="bi bi-pencil"></i>

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



catch(error){


console.log(error);


alert("Unable to load institutions");


}



}









// ===============================
// Add / Update Institution
// ===============================


institutionForm.addEventListener(
"submit",
saveInstitution
);




async function saveInstitution(event){


event.preventDefault();




const id =
document.getElementById("institutionId").value;




const data = {


name:
document.getElementById("institutionName").value,


address:
document.getElementById("institutionAddress").value,


website:
document.getElementById("institutionWebsite").value,


contact_email:
document.getElementById("institutionEmail").value


};







let response;




if(id===""){



response =
await fetch(
INSTITUTIONS_API + "/",
{


method:"POST",


headers:{


"Content-Type":"application/json"


},


body:JSON.stringify(data)


}

);



}



else{


response =
await fetch(
INSTITUTIONS_API + "/" + id,
{


method:"PUT",


headers:{


"Content-Type":"application/json"


},


body:JSON.stringify(data)


}

);



}





if(response.ok){



institutionModal.hide();


institutionForm.reset();


document.getElementById("institutionId").value="";


loadInstitutions();



}


else{


alert("Operation failed");


}



}









// ===============================
// Edit Institution
// ===============================


async function editInstitution(id){



const response =
await fetch(
INSTITUTIONS_API + "/" + id
);



const institution =
await response.json();




document.getElementById("institutionId").value =
institution.id;



document.getElementById("institutionName").value =
institution.name;



document.getElementById("institutionAddress").value =
institution.address || "";



document.getElementById("institutionWebsite").value =
institution.website || "";



document.getElementById("institutionEmail").value =
institution.contact_email || "";





institutionModal.show();



}









// ===============================
// Delete Institution
// ===============================


async function deleteInstitution(id){



if(!confirm(
"Are you sure you want to delete this institution?"
))

return;




const response =
await fetch(
INSTITUTIONS_API + "/" + id,
{


method:"DELETE"


}

);




if(response.ok){


loadInstitutions();


}


else{


alert("Delete failed");


}



}








// ===============================
// Search
// ===============================


document
.getElementById("searchInstitution")
.addEventListener(
"keyup",
function(){



let value =
this.value.toLowerCase();



let rows =
institutionTable.getElementsByTagName("tr");



for(let row of rows){



row.style.display =
row.innerText
.toLowerCase()
.includes(value)
?
""
:
"none";



}



}

);








// ===============================
// Reset Modal
// ===============================


document
.getElementById("institutionModal")
.addEventListener(
"hidden.bs.modal",
function(){


institutionForm.reset();


document.getElementById("institutionId").value="";


}

);







// Initial Load

loadInstitutions();