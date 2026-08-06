// ==========================================
// Dashboard Controller
// Scientific Collaboration Network Analyzer
// ==========================================



document.addEventListener("DOMContentLoaded", function(){

    const role = (localStorage.getItem("role") || "").toLowerCase();
    const rolePages = {"institution admin":"pages/institution-dashboard.html",publisher:"pages/publisher-dashboard.html",reviewer:"pages/reviewer-dashboard.html",researcher:"pages/researcher-dashboard.html"};
    if (rolePages[role]) { window.location.href = rolePages[role]; return; }


    loadDashboardData();

    loadUser();

    makeDashboardCardsClickable();



});




// ==========================================
// Load Username
// ==========================================


function loadUser(){


    const username =
    localStorage.getItem("username");


    const userElement =
    document.getElementById("loggedUser");



    if(userElement && username){


        userElement.innerText=username;


    }

    const welcomeElement = document.getElementById("dashboardWelcome");
    if(welcomeElement){
        const role = localStorage.getItem("role") || "Researcher";
        welcomeElement.innerText = username ? `Welcome back, ${username}. You are signed in as ${role}.` : "Welcome back.";
    }


}






// ==========================================
// Load Dashboard Statistics
// ==========================================


async function loadDashboardData(){
    try{
        const response = await fetch(DASHBOARD_API);
        const data = await response.json();

        document.getElementById("researcherCount").innerText = data.total_researchers || 0;
        document.getElementById("institutionCount").innerText = data.total_institutions || 0;
        document.getElementById("publicationCount").innerText = data.total_publications || 0;
        document.getElementById("conferenceCount").innerText = data.total_conferences || 0;
        document.getElementById("collaborationCount").innerText = data.total_collaborations || 0;
        document.getElementById("citationCount").innerText = data.total_citations || 0;
        document.getElementById("projectCount").innerText = data.total_projects || 0;
    }
    catch(error){
        console.log(
            "Dashboard loading error:",
            error
        );
    }
}








// ==========================================
// Researchers Count
// ==========================================


async function loadResearchers(){


    try{


        const response =
        await fetch(
            RESEARCHERS_API + "/"
        );


        const data =
        await response.json();



        document.getElementById(
            "researcherCount"
        ).innerText =
        data.length || 0;



    }


    catch(error){


        console.log(error);


    }


}









// ==========================================
// Institutions Count
// ==========================================


async function loadInstitutions(){


    try{


        const response =
        await fetch(
            INSTITUTIONS_API + "/"
        );


        const data =
        await response.json();



        document.getElementById(
            "institutionCount"
        ).innerText =
        data.length || 0;



    }


    catch(error){


        console.log(error);


    }


}









// ==========================================
// Publications Count
// ==========================================


async function loadPublications(){


    try{


        const response =
        await fetch(
            PUBLICATIONS_API + "/"
        );


        const data =
        await response.json();



        document.getElementById(
            "publicationCount"
        ).innerText =
        data.length || 0;



    }


    catch(error){


        console.log(error);


    }


}









// ==========================================
// Conferences Count
// ==========================================


async function loadConferences(){


    try{


        const response =
        await fetch(
            CONFERENCES_API + "/"
        );


        const data =
        await response.json();



        document.getElementById(
            "conferenceCount"
        ).innerText =
        data.length || 0;



    }


    catch(error){


        console.log(error);


    }


}







// ==========================================
// Logout
// ==========================================


function logoutUser(){


    localStorage.removeItem("token");

    localStorage.removeItem("username");

    localStorage.removeItem("role");


    window.location.href="index.html";


}


function makeDashboardCardsClickable(){
    const destinations = {
        researcherCount: "pages/researchers.html",
        institutionCount: "pages/institutions.html",
        publicationCount: "pages/publications.html",
        conferenceCount: "pages/conferences.html",
        collaborationCount: "pages/collaborations.html",
        citationCount: "pages/citations.html",
        projectCount: "pages/projects.html"
    };

    Object.entries(destinations).forEach(([id, destination]) => {
        const count = document.getElementById(id);
        const card = count?.closest(".stat-card");
        if (!card) return;
        card.dataset.target = destination;
        card.tabIndex = 0;
        card.setAttribute("role", "link");
        card.addEventListener("click", () => window.location.href = destination);
        card.addEventListener("keydown", event => {
            if (event.key === "Enter" || event.key === " ") window.location.href = destination;
        });
    });
}
