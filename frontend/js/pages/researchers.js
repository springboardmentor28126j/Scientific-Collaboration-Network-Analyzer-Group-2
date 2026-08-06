// ==========================================
// Researchers Module
// ==========================================


let researchersData = [];



const table =
document.getElementById("researcherTable");


const form =
document.getElementById("researcherForm");



const modal =
new bootstrap.Modal(
document.getElementById("researcherModal")
);






async function loadResearchers(){


try{


const response =
await fetch(
RESEARCHERS_API + "/"
);



researchersData =
await response.json();



displayResearchers(
researchersData
);



}

catch(error){


console.log(error);


table.innerHTML =
`
<tr>
<td colspan="8"
class="text-center text-danger">

Unable to load researchers

</td>
</tr>
`;


}


}








function displayResearchers(data){


table.innerHTML="";



if(data.length===0){


table.innerHTML=
`
<tr>
<td colspan="8"
class="text-center">

No researchers found

</td>
</tr>
`;

return;


}





data.forEach(
researcher=>{


table.innerHTML +=


`

<tr>


<td>${researcher.id}</td>


<td>${researcher.full_name}</td>


<td>${researcher.department}</td>


<td>${researcher.designation}</td>


<td>${researcher.skills || "-"}</td>


<td>${researcher.research_interest || "-"}</td>


<td>${researcher.institution_id}</td>


<td>


<button

class="btn btn-warning btn-sm"

onclick="editResearcher(${researcher.id})">


<i class="bi bi-pencil"></i>

Edit


</button>


</td>


</tr>


`;



});


}








form.addEventListener(
"submit",
saveResearcher
);





async function saveResearcher(e){


e.preventDefault();



const id =
document.getElementById(
"researcherId"
).value;



const data = {


full_name:
full_name.value,


department:
department.value,


skills:
skills.value,


research_interest:
research_interest.value,


designation:
designation.value,

email:
email.value || null,


institution_id:
parseInt(
institution_id.value
)


};





let response;



if(id===""){


response =
await fetch(
RESEARCHERS_API + "/",
{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:
JSON.stringify(data)

});


}

else{


response =
await fetch(
RESEARCHERS_API+"/"+id,
{

method:"PUT",

headers:{
"Content-Type":"application/json"
},

body:
JSON.stringify(data)

});


}





if(response.ok){


modal.hide();


form.reset();


loadResearchers();


}

else{


alert(
"Operation failed"
);


}



}








async function editResearcher(id){


const response =
await fetch(
RESEARCHERS_API+"/"+id
);



const researcher =
await response.json();




researcherId.value =
researcher.id;


full_name.value =
researcher.full_name;


department.value =
researcher.department;


designation.value =
researcher.designation;

email.value =
researcher.email || "";


skills.value =
researcher.skills;


research_interest.value =
researcher.research_interest;


institution_id.value =
researcher.institution_id;



modal.show();


}








document
.getElementById(
"searchResearcher"
)
.addEventListener(
"keyup",
function(){


const value =
this.value.toLowerCase();



const filtered =
researchersData.filter(
r=>

r.full_name
.toLowerCase()
.includes(value)

);



displayResearchers(filtered);


}

);







function logoutUser(){


localStorage.clear();


window.location.href="../index.html";


}






loadResearchers();
