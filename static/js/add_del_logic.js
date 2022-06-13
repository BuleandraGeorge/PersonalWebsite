
document.addEventListener('click', function (e) {
    let element = e.target
    let button = e.target
    if (element.tagName == "I") button = element.parentNode
    if (button.className.indexOf('add') != -1)
    {
        initialInput = button.parentNode.previousElementSibling;
        newInput = document.createElement('input');
        for (let i = 0; i < 5; i++){
            newInput.setAttribute(initialInput.attributes[i].name, initialInput.attributes[i].nodeValue);
        }
        initialInput.parentNode.insertBefore(newInput, button.parentNode);
    }
    else if (button.className.indexOf('del') != -1)
    {
        let input_container = button.parentNode.parentNode.childNodes
        let inputs =[]
        for (child in input_container) {
            if(input_container[child].tagName=="INPUT") inputs.push(input_container[child])
		}
        if (inputs.length > 1) {
            inputs[inputs.length-1].remove();
		}
       
	}

})