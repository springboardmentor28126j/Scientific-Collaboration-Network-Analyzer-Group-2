// =======================================
// Authentication Controller
// Scientific Collaboration Network Analyzer
// =======================================



const loginForm =
document.getElementById("loginForm");

const roleDashboard = role => ({"institution admin":"pages/institution-dashboard.html",publisher:"pages/publisher-dashboard.html",reviewer:"pages/reviewer-dashboard.html",researcher:"pages/researcher-dashboard.html"}[(role || "").toLowerCase()] || "dashboard.html");



if(loginForm){

loginForm.addEventListener(
"submit",
loginUser
);

}



async function loginUser(event){


event.preventDefault();



const email =
document.getElementById("email").value;



const password =
document.getElementById("password").value;



const messageBox =
document.getElementById("messageBox");



const loginBtn =
document.getElementById("loginBtn");



loginBtn.disabled=true;

loginBtn.innerHTML="Logging in...";



try{


const response =
await fetch(
"http://127.0.0.1:8000/users/login",
{


method:"POST",


headers:{

"Content-Type":"application/json"

},


body:JSON.stringify({

email:email,

password:password

})


});



const data =
await response.json();



if(data.message==="Login Successful"){



localStorage.setItem("token", data.access_token || "");
localStorage.setItem("username", data.user);
localStorage.setItem("role", data.role || "");


localStorage.setItem(
"loggedIn",
"true"
);



messageBox.className=
"alert alert-success";


messageBox.classList.remove("d-none");


messageBox.innerHTML=
"Login successful. Redirecting...";



setTimeout(()=>{


window.location.href=
roleDashboard(data.role);


},1000);



}


else{


messageBox.className=
"alert alert-danger";


messageBox.classList.remove("d-none");


messageBox.innerHTML=
data.message ||
"Invalid credentials";


}



}

catch(error){


messageBox.className=
"alert alert-danger";


messageBox.classList.remove("d-none");


messageBox.innerHTML=
"Server connection failed.";


}



loginBtn.disabled=false;


loginBtn.innerHTML=
'<i class="bi bi-box-arrow-in-right"></i> Login';



}





// ===============================
// Register
// ===============================



const registerForm =
document.getElementById("registerForm");



if(registerForm){


registerForm.addEventListener(
"submit",
registerUser
);


}




async function registerUser(event){


event.preventDefault();



const data={


name:
document.getElementById("name").value,


email:
document.getElementById("registerEmail").value,


password:
document.getElementById("registerPassword").value,


role:
document.getElementById("role").value


};




const messageBox =
document.getElementById("registerMessage");



try{


const response =
await fetch(

"http://127.0.0.1:8000/users/register",

{


method:"POST",


headers:{

"Content-Type":"application/json"

},


body:
JSON.stringify(data)


}

);



const result =
await response.json();



if(response.ok){


messageBox.className=
"alert alert-success";


messageBox.classList.remove("d-none");


messageBox.innerHTML=
"Registration successful. Redirecting...";


setTimeout(()=>{


window.location.href=
"index.html";


},1200);


}

else{


messageBox.className=
"alert alert-danger";


messageBox.classList.remove("d-none");


messageBox.innerHTML=
result.detail ||
"Registration failed";


}



}


catch(error){


messageBox.className=
"alert alert-danger";


messageBox.classList.remove("d-none");


messageBox.innerHTML=
"Server error";


}



}
