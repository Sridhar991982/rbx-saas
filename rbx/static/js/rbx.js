var RBX = (function () {

    var _init = function () {
    	_tooltips()
    	_selectToDropdown()
    }

    var _tooltips = function () {
        $('a').tooltip({placement: 'bottom'})
    }

    var _selectToDropdown = function () {
        $('select').each(function(i, e){
            if (!($(e).data('convert') == 'no')) {
                $(e).hide().wrap('<div class="btn-group" id="select-group-' + i + '" />');
                var select = $('#select-group-' + i);
                console.log($(e).find(':selected').text())
                var current = ($(e).val()) ? $(e).find(':selected').text() : '&nbsp;';
                select.html('<input type="hidden" value="' + $(e).val() + '" name="' + $(e).attr('name') + '" id="' + $(e).attr('id') + '" class="' + $(e).attr('class') + '" />' +
                            '<a class="btn dropdown-toggle" data-toggle="dropdown" href="#""><span>' + current +
                            '</span> <span class="caret"></span></a>' +
                            '<ul class="dropdown-menu"></ul>');
                $(e).find('option').each(function(o,q) {
                    select.find('.dropdown-menu').append('<li><a href="#" data-value="' + $(q).attr('value') + '">' + $(q).text() + '</a></li>');
                    if ($(q).attr('selected')) select.find('.dropdown-menu li:eq(' + o + ')').click();
                });
                select.find('.dropdown-menu a').click(function() {
                    select.find('input[type=hidden]').val($(this).data('value')).change();
                    select.find('.btn:eq(0) span:eq(0)').text($(this).text());
                });
            }
        });
    }

    return {
        init: _init,
    }

})()

$(document).ready(RBX.init())
