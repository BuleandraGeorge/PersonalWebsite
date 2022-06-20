function getOptionList() {
    let navOptions = document.querySelector("#main-nav-bar").childNodes;
    let anchorList = [];
    for (option in navOptions) {
        children = navOptions[option].childNodes
        for (child in children) {
            if (children[child].tagName == "A") {
                anchorList.push(children[child])
            }
        }
    }
    return anchorList
}

function resetActive(el) {
    el.classList.remove("active");
}
function spypage() {
    let anchorList = getOptionList();
    anchorList.forEach(resetActive)
    let path = window.location.pathname;
    if (path == "/") {
        anchorList[0].classList.add("active");
        return 0
    }
    if (path == "/student") {
        anchorList[1].classList.add("active");
        return 0
    }
    if (path == "/developer") {
        anchorList[2].classList.add("active");
        return 0
    }
    if (path == "/dreamer") {
        anchorList[3].classList.add("active");
        return 0
    }
}
spypage();