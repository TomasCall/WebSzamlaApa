function Checker()
{
    let username = document.getElementById("usr").value;
    let email = document.getElementById("mail").value;
    let email_again = document.getElementById("emailagain").value;
    let pswd = document.getElementById("pswd").value;
    let passwordagain = document.getElementById("passwordagain").value;
    if(username != "" && email != "" && email_again != "" && pswd!="" && passwordagain !="")
    {
        if(email == email_again && pswd == passwordagain)
        {
            if(String(email).includes("@") && String(email_again).includes("@"))
            {
                document.getElementById("reg").style.display="inline-block";
            }
        }
    }
}