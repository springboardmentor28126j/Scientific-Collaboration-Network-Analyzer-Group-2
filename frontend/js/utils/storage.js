// =====================================
// Local Storage Manager
// =====================================


function saveUser(data){


    localStorage.setItem(

        "token",

        data.access_token || data.token

    );


    localStorage.setItem(

        "username",

        data.name || ""

    );


    localStorage.setItem(

        "role",

        data.role || ""

    );


}



function getUserToken(){

    return localStorage.getItem("token");

}



function logoutUser(){


    localStorage.clear();


    window.location.href =
    "../index.html";


}