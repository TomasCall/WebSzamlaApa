let global_id = "";
let global_line = 0;

function getLine(line)
{
    global_line = line;
    let t = document.getElementById("table");
    let trs = t.getElementsByTagName("tr")[line];
    let tds = trs.getElementsByTagName("td");
    let list = [];
    for(let i=1;i<tds.length;i++)
    {
        list.push(tds[i].innerHTML)
    }
    
    document.getElementById("Szamlaszam").setAttribute('value',list[0]);
    global_id = document.getElementById("Szamlaszam").value;

    document.getElementById("Megrendeloneve").setAttribute('value',list[1]);
    document.getElementById("Osszeg").setAttribute('value',parseInt(list[2]));
    document.getElementById("Kiallitas").value=list[3];
    document.getElementById("Hatarido").value=list[4];
    if(list[5]=="1")
    {
        document.getElementById("Teljesitve").checked=true;
    }
    else
    {
        document.getElementById("Teljesitve").checked=false;
    }

    let userInfo = {
        "global_id":global_id,
    }
    let request = new XMLHttpRequest();
    request.open("POST",`/processUserInfo/${JSON.stringify(userInfo)}`)
    request.onload = () =>{
        let fM = request.responseText;
        console.log(fM);
    }
    request.send();
};
