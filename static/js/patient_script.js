'use strict';

$(document).ready(function() {
    $('#new-patient').change(function (event) {
        let value = event.target.checked;
        console.log(value);
        if (value) {
            $('.abc > li:not(:first-of-type)').show();
        } else {
            $('.abc > li:not(:first-of-type)').hide();
        }
    });

    $('#load-file').change(function (event) {
        let value = event.target.checked;
        console.log(value);
        if (value) {
            $('.form-control-file').parent().show();
            $('.analysis').empty();
        } else {
            $('.form-control-file').parent().hide();

        }
    });

    $('.form-control-patient').on('change', 'input[name="diseases"]', function (event) {
        console.log('Success')
        let target_href = event.target;
        let isFile = document.getElementById('load-file').checked;
        if (target_href) {
            event.preventDefault();
            $.ajax({
                url: "/show_required_analyzes/" + target_href.value + "/",

                success: function (data) {
                    if (!isFile) {
                        $('.analysis').empty();
                        $('.analysis').append($("<h2></h2>").text('Analyzes'));
                        for (var i = 0; i < data.required_analyzes.length; i++) {
                            let attrStr = data.required_analyzes[i].replaceAll(' ', '-')
                            $('.analysis').append($(`<label for=${attrStr}></label>`).text(`${data.required_analyzes[i]}: `));
                            $('.analysis').append($(`<input name=${attrStr} id=${attrStr} ></input><br>`));
                        }
                        console.log('finish');
                    } else {
                        $('.analysis').empty();
                    }
                }
            })
        }
    })
});