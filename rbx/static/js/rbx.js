var RBX = (function () {

    var _init = function () {
    	_tooltips()

    	_modalFragment()
    	_submitModalChanges()

    	_selectToDropdown()

        _navTabs()
    	_activateTabFromHash()
    }

    var _tooltips = function () {
    	$(window).resize(function () {
            if (!$('.hidden-desktop').is(':visible'))
                $('a').tooltip({placement: 'bottom'})
        })
    }

    var _modalFragment = function () {
        $('.modal-fragment').on('click', function() {
        	var target = $(this).attr('data-target');
            $(target).modal({keyboard: false})
            $(target + ' .modal-body').load($(this).attr('href') + ' #fragment')
            return false;
        })
    }

    var _submitModalChanges = function () {
        $('.submit-change').on('click', function () {
        	var modal = $(this).parent().parent(),
                form = modal.find('form')
            modal.find('.modal-body').load(form.attr('action') + ' #fragment', form.serializeArray())
            return false;
        })
    }

    var _selectToDropdown = function () {
        $('select').each(function(i, e){
            if (!($(e).data('convert') == 'no')) {
                $(e).hide().wrap('<div class="btn-group" id="select-group-' + i + '" />');
                var select = $('#select-group-' + i),
                    current = ($(e).val()) ? $(e).find(':selected').text() : '&nbsp;';
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

    var _navTabs = function () {
        $('.nav-tabs a').on('click', function () {
            $(this).tab('show')
            location.hash = '/' + $(this).attr('href').substr(1)
            return false
        })
    }

    var _activateTabFromHash = function () {
        var hash = location.hash.substr(2),
            hashPieces = hash.split('?'),
            activeTab = $('[href=#' + hashPieces[0] + ']')
            activeTab && activeTab.tab('show')
    }

    return {
        init: _init,
    }

})()

$(document).ready(RBX.init())
