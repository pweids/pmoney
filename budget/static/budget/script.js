
function leftArrowPressed() {
    document.getElementById('left-navigate').click();
}

function rightArrowPressed() {
    document.getElementById('right-navigate').click();
}

document.onkeydown = function (evt) {
    evt = evt || window.event;
    switch (evt.keyCode) {
        case 37:
            leftArrowPressed();
            break;
        case 39:
            rightArrowPressed();
            break;
    }
};