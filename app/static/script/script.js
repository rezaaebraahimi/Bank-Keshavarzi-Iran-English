window.addEventListener("load", function(){
    setTimeout(
        function open(event){
            document.querySelector(".alert").style.display = "block";
        },
        100
    )
});

window.addEventListener("load", function(){
    setTimeout(
        function close(event){
            document.querySelector(".alert").style.display = "none";
        },
        3000
    )
});

