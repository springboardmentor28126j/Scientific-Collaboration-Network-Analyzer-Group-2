// =====================================
// Authentication API
// =====================================


async function loginAPI(email,password){


    return await fetch(

        LOGIN_API,

        {

            method:"POST",

            headers:{

                "Content-Type":
                "application/json"

            },

            body:

            JSON.stringify({

                email:email,

                password:password

            })

        }

    );

}



async function registerAPI(data){


    return await fetch(

        REGISTER_API,

        {

            method:"POST",

            headers:{

                "Content-Type":
                "application/json"

            },

            body:

            JSON.stringify(data)

        }

    );

}