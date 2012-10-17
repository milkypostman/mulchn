$(document).ready(function () {
    $('#add_answer').click(function () {
        var num = clone_answer('.answers-input:last', 4);
        if (num >= 4) {
            $('#add_answer').fadeOut();
        }
    });
});

function clone_answer(selector, max_num) {
    var elem = $(selector)

    var new_input = elem.find(':input').clone(true);
    var num = parseInt(new_input.attr('id').replace(/.*-(\d{1,4})/m, '$1'));
    if (num >= max_num) { return; }
    var id = new_input.attr('id').replace('-' + num, '-' + (num+1));
    var placeholder = new_input.attr('placeholder').replace(num+1, num+2);
    new_input.attr({'name': id, 'id': id, 'placeholder': placeholder}).val('');
    var new_element = elem.clone(true);
    new_element.html(new_input);
    elem.after(new_element);
    return num+1;
}

