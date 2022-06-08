document.getElementById('add').addEventListener('click', function () {
    newInput = document.createElement('input');
    newInput.setAttribute('placeholder', 'Add Feature');
    newInput.setAttribute('type', 'text');
    newInput.setAttribute('class', 'form-control mb-2');
    newInput.setAttribute('name', 'no_name');
    referenceNode = document.getElementById('features_buttons')
    document.getElementById('features_inputs').insertBefore(newInput, referenceNode);
})

document.getElementById('del').addEventListener('click', function () {
    referenceNode = document.getElementById('add')
    list = document.getElementById('features_inputs').childNodes
    let inputs = [];
    for (element in list) {
        if (list[element].tagName == "INPUT") {
            inputs.push(list[element]);
		}
    }
    if (inputs.length>1)
    {
        inputs[inputs.length - 1].remove();
    }
})