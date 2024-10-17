

function changeView(index){
    containers = document.getElementsByClassName("grid-container")
    for(var i = 0 ; i<containers.length; i++){
        if(i == index){
            containers[i].classList.remove('hidden');
        }else{
            containers[i].classList.add('hidden');
        }
    }

}


document.addEventListener('DOMContentLoaded', () => {
    const change_buttons = document.querySelectorAll('.change-button');
    change_buttons.forEach((button, index) => {
        button.addEventListener('click', ()=> changeView(index));
    });
    const containers = document.getElementsByClassName("grid-container")
    for(var i = 1 ; i<containers.length; i++){
        containers[i].classList.add('hidden');
    }
});