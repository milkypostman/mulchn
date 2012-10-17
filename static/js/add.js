var maxFieldId = 4;

String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

$(document).ready(function () {
    var newId = clone_answer('.answers-input:last', maxFieldId);
    while(newId < maxFieldId)
    {
        newId = clone_answer('.answers-input:last', maxFieldId);
    }
    /*
    $('#add_answer').click(function () {
        var newId =

        // if new ID is the last we want
        if (newId >= maxFieldId) {
            $('#add_answer').fadeOut();
        }
    });
    */
});


function clone_answer(selector, maxId) {
    var elem = $(selector)

    // clone the input field
    var new_input = elem.find(':input').clone(true);

    // determine which number we're dealing with
    var curId = parseInt(new_input.attr('id').replace(/.*-(\d{1,4})/m, '$1'));
    var newId = curId + 1;

    // possible that we double tap the button; ignore
    if (curId >= maxId) { return curId; }

    var id = new_input.attr('id').replace('-' + curId, '-' + (newId));
    var placeholder = new_input.attr('placeholder').replace(newId, curId+2);

    if (!placeholder.endsWith("(optional)")) {
        placeholder += " (optional)";
    }

    new_input.attr({'name': id, 'id': id, 'placeholder': placeholder}).val('');

    var new_element = elem.clone(true);
    new_element.html(new_input);
    elem.after(new_element);

    // return the id we created
    return newId;
}

