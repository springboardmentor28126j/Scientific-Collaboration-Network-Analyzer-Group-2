// =======================================
// API Configuration
// =======================================


const API_URL =
"http://127.0.0.1:8000";



function getToken(){

    return localStorage.getItem("token");

}



function authHeaders(){

    return {

        "Content-Type":"application/json",

        "Authorization":
        "Bearer " + getToken()

    };

}



async function apiGet(url){

    return await fetch(url,{

        method:"GET",

        headers:authHeaders()

    });

}



async function apiPost(url,data){

    return await fetch(url,{

        method:"POST",

        headers:authHeaders(),

        body:
        JSON.stringify(data)

    });

}



async function apiPut(url,data){

    return await fetch(url,{

        method:"PUT",

        headers:authHeaders(),

        body:
        JSON.stringify(data)

    });

}



async function apiDelete(url){

    return await fetch(url,{

        method:"DELETE",

        headers:authHeaders()

    });

}


// API ENDPOINTS


const LOGIN_API =
API_URL + "/users/login";


const REGISTER_API =
API_URL + "/users/register";


const RESEARCHERS_API =
API_URL + "/researchers/";


const PUBLICATIONS_API =
API_URL + "/publications/";


const CONFERENCES_API =
API_URL + "/conferences/";


const INSTITUTIONS_API =
API_URL + "/institutions/";


const COLLABORATIONS_API =
API_URL + "/collaborations/";


const DASHBOARD_API =
API_URL + "/dashboard/";


const REPORTS_API =
API_URL + "/reports";


const CITATIONS_API =
API_URL + "/citations/";


const UPLOAD_API =
API_URL + "/publications/upload/";