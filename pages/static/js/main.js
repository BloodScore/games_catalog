function openNav() {
    document.getElementById("mySidepanel").style.width = "250px";
    document.getElementById("open_btn").style.display = "none";
    document.getElementById("main").style.marginLeft = "150px";
    document.getElementById("search_container").style.marginLeft = "180px";

}

function closeNav() {
    document.getElementById("mySidepanel").style.width = "0";
    document.getElementById("open_btn").style.display = "block";
    document.getElementById("main").style.marginLeft = "0";
    document.getElementById("search_container").style.marginLeft = "0";
}
