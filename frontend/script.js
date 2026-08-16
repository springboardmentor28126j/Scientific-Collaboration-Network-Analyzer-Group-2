function login() {
  const email = document.getElementById("username").value; // using same input box
  const password = document.getElementById("password").value;

  fetch("http://127.0.0.1:8000/users/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: email,        // ✅ FIXED
      password: password
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.message === "User not found") {
      alert("User not found ❌");
    } else {
      alert("Login successful ✅");
      window.location.href = "dashboard.html";
    }
  })
  .catch(err => {
    alert("Error occurred ❌");
    console.log(err);
  });
}

async function loadResearchers(){

    try{

        const response = await fetch(
            "http://127.0.0.1:8000/researchers/"
        );

        const researchers = await response.json();


        const list = document.getElementById("researcherList");

        list.innerHTML = "";


        researchers.forEach(researcher => {

    const li = document.createElement("li");

    li.innerHTML =
    `
    <b>Name:</b> ${researcher.full_name}<br>
    <b>Department:</b> ${researcher.department}<br>
    <b>Skills:</b> ${researcher.skills}<br>
    <b>Designation:</b> ${researcher.designation}<br>
    <b>Institution:</b> ${researcher.institution}<br>
    <b>Research Interest:</b> ${researcher.research_interest}

    <br>

    <button onclick="deleteResearcher(${researcher.id})">
        Delete
    </button>

    <hr>
    `;

    list.appendChild(li);

});


    }
    catch(error){

        console.log(error);

        alert("Could not load researchers");

    }

}
async function addResearcher(){

    const researcher = {

        full_name: document.getElementById("full_name").value,

        department: document.getElementById("department").value,

        skills: document.getElementById("skills").value,

        designation: document.getElementById("designation").value,

        institution: document.getElementById("institution").value,

        research_interest: document.getElementById("research_interest").value

    };


    try{

        const response = await fetch(
            "http://127.0.0.1:8000/researchers/",
            {
                method: "POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body: JSON.stringify(researcher)
            }
        );


        if(response.ok){

            alert("Researcher Added Successfully ✅");

            loadResearchers();

        }
        else{

            alert("Failed to add researcher ❌");

        }


    }
    catch(error){

        console.log(error);

        alert("Server Error");

    }

}

async function deleteResearcher(id){

    try{

        const response = await fetch(
            `http://127.0.0.1:8000/researchers/${id}`,
            {
                method:"DELETE"
            }
        );


        if(response.ok){

            alert("Researcher Deleted Successfully ✅");

            loadResearchers();

        }
        else{

            alert("Delete Failed ❌");

        }


    }
    catch(error){

        console.log(error);

        alert("Server Error");

    }

}