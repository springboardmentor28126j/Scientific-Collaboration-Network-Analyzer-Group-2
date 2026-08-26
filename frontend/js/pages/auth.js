// =======================================
// Authentication Controller
// Scientific Collaboration Network Analyzer
// =======================================



const loginForm =
document.getElementById("loginForm");

const roleDashboard = role => ({"institution admin":"pages/institution-dashboard.html",publisher:"pages/publisher-dashboard.html",reviewer:"pages/reviewer-dashboard.html",researcher:"pages/researcher-dashboard.html"}[(role || "").toLowerCase()] || "dashboard.html");

async function loadCaptcha(){
const question=document.getElementById("captchaQuestion"), token=document.getElementById("captchaToken"), answer=document.getElementById("captchaAnswer");
if(!question || !token) return;
question.textContent="Loading…";
try { const response=await fetch("http://127.0.0.1:8000/users/captcha"); const data=await response.json(); question.textContent=data.question; token.value=data.captcha_token; if(answer) answer.value=""; }
catch { question.textContent="Security check unavailable"; token.value=""; }
}

document.getElementById("refreshCaptcha")?.addEventListener("click", loadCaptcha);
if(loginForm) loadCaptcha();

document.getElementById("passwordToggle")?.addEventListener("click", () => {
const input=document.getElementById("password"), icon=document.querySelector("#passwordToggle i");
const visible=input.type === "text"; input.type=visible ? "password" : "text";
icon.className=visible ? "bi bi-eye" : "bi bi-eye-slash";
document.getElementById("passwordToggle").setAttribute("aria-label",visible ? "Show password" : "Hide password");
});

(() => {
const hash=window.location.hash || "";
if(hash.startsWith("#scna-oauth=")){
try { const data=JSON.parse(decodeURIComponent(hash.slice(12))); localStorage.setItem("token",data.token); localStorage.setItem("username",data.name); localStorage.setItem("role",data.role); localStorage.setItem("loggedIn","true"); window.history.replaceState({},document.title,window.location.pathname); window.location.replace(roleDashboard(data.role)); } catch { window.history.replaceState({},document.title,window.location.pathname); }
} else if(hash.startsWith("#scna-oauth-error=")) {
window.addEventListener("DOMContentLoaded",()=>{ const box=document.getElementById("messageBox"); if(box){ box.className="alert alert-danger"; box.textContent=decodeURIComponent(hash.slice(18)); } window.history.replaceState({},document.title,window.location.pathname); });
}
})();



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

,captcha_token:document.getElementById("captchaToken").value

,captcha_answer:document.getElementById("captchaAnswer").value

})


});



const data =
await response.json();

if (!response.ok) loadCaptcha();



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


confirm_password:
document.getElementById("confirmPassword").value,


role:
document.getElementById("role").value


};




const messageBox =
document.getElementById("registerMessage");

const password = data.password;
const passwordOk = password.length >= 8 && /[A-Z]/.test(password) && /[a-z]/.test(password) && /\d/.test(password) && /[^A-Za-z0-9]/.test(password);

if (!passwordOk || password !== data.confirm_password) {
messageBox.className="alert alert-danger";
messageBox.classList.remove("d-none");
messageBox.innerHTML = password !== data.confirm_password ? "Passwords do not match." : "Password must be 8+ characters and include uppercase, lowercase, a number, and a special character.";
return;
}



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


const registerPasswordInput = document.getElementById("registerPassword");
const confirmPasswordInput = document.getElementById("confirmPassword");
const passwordFeedback = document.getElementById("passwordFeedback");
if (registerPasswordInput && confirmPasswordInput && passwordFeedback) {
const showPasswordFeedback = () => {
const value = registerPasswordInput.value;
const checks = [value.length >= 8, /[A-Z]/.test(value), /[a-z]/.test(value), /\d/.test(value), /[^A-Za-z0-9]/.test(value)];
const complete = checks.every(Boolean);
const matches = !confirmPasswordInput.value || value === confirmPasswordInput.value;
passwordFeedback.className = `form-text ${complete && matches ? 'text-success' : 'text-muted'}`;
passwordFeedback.textContent = complete ? (matches ? 'Strong password ready.' : 'Passwords do not match.') : `Password strength: ${checks.filter(Boolean).length}/5 requirements met.`;
};
registerPasswordInput.addEventListener("input", showPasswordFeedback);
confirmPasswordInput.addEventListener("input", showPasswordFeedback);
}
