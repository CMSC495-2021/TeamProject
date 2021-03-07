var menuOpen = false;
// all event handlers
function init(){
    document.getElementById("mainMenu").addEventListener("click", function() {
        // click on menu and make it visible, otherwise make it hidden
        if(!menuOpen){
            document.querySelector('.subMenu').style.visibility = 'visible';
            menuOpen = true;
        }
        else{
            document.querySelector('.subMenu').style.visibility = 'hidden';
            menuOpen = false;
        }
    });
    document.querySelector('.mainview').addEventListener("click", function(){
        // click anywhere in the chat view to hide the menu
        if(menuOpen){
            document.querySelector('.subMenu').style.visibility = 'hidden';
            menuOpen = false;
        }
    });
}
document.addEventListener('readystatechange', function() {
    if (document.readyState === "complete") {
      init();
    }
});