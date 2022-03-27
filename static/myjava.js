
function searchandFilter() {
    
    var input = document.getElementById('filterby');
    var filter = input.value.toUpperCase();

    var table = document.getElementById('visitorTable');
    var tr = table.getElementsByTagName('tr');

    for(var x = 0; x < tr.length; x++) {
        td = tr[x].getElementsByTagName("td")[0];
        if(td) {
            if(td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                tr[x].style.display = "";
            }
            else {
                tr[x].style.display = "none";
            }
        }
    }
}


function filter() {
    var input = document.getElementById('filterby2');
    var filter = input.value.toUpperCase();

    var table = document.getElementById('placeTable');
    var tr = table.getElementsByTagName('tr');

    for(var x = 0; x < tr.length; x++) {
        td = tr[x].getElementsByTagName("td")[0];
        if(td) {
            if(td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                tr[x].style.display = "";
            }
            else {
                tr[x].style.display = "none";
            }
        }
    }
}



function saveInput() {

    //saves a visitor's input on their local computer for when next they visit website

    const fname = document.getElementById('vname').value;
    const lname = document.getElementById('vname2').value;
    const email = document.getElementById('vemail').value;
    const phone = document.getElementById('vphone').value;
    const addr = document.getElementById('vaddr').value;
    const city = document.getElementById('vcity').value;
    const state = document.getElementById('vstate').value;
    const zip = document.getElementById('vzip').value 

    setWithExpiry('fname', fname)
    setWithExpiry('lname', lname)
    setWithExpiry('email', email)
    setWithExpiry('phone', phone)
    setWithExpiry('addr', addr)
    setWithExpiry('city', city)
    setWithExpiry('state', state)
    setWithExpiry('zip', zip)
}

function setWithExpiry(key, value)
{
    const now = new Date();

    const item = {
        value: value,
        expiry: now.getTime() + 900000,
    }

    localStorage.setItem(key, JSON.stringify(item))
}