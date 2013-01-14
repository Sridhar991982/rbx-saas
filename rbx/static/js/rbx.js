var RBX = (function () {

    var _init = function () {
    	_tooltips()
    	_dissmissSiteAlert()

    	_modalFragment()
    	_submitModalChanges()

    	_selectToDropdown()
    	_newBoxForm()

        _navTabs()
    	_activateTabFromHash()
    }

    var _tooltips = function () {
    	$(window).on('resize', function () {
            if (!window.matchMedia || (window.matchMedia('(min-width: 979px)').matches))
                $('a[rel="tooltip"]').tooltip({placement: 'bottom'})
            else
                $('a[rel="tooltip"]').tooltip('destroy')
        }).trigger('resize')
    }

    var _dissmissSiteAlert = function () {
        $('.site-alert button.close').on('click', function () {
            $(this).parent().parent().remove()
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
            modal.find('.modal-body').load(form.attr('action') + ' #fragment',
                form.serializeArray(), function () {
                modal.find('button.btn[data-dismiss="modal"]').text('Close')
                modal.on('hidden', function () {
                	modal.off('hidden')
                	location.reload()
                })
            })
            return false;
        })
    }

    var _selectToDropdown = function () {
        $('select').each(function(i, e){
            if (!($(e).data('convert') == 'no')) {
                $(e).hide().wrap('<div class="btn-group" id="select-group-' + i + '" />')

                var select = $('#select-group-' + i),
                    current = ($(e).val()) ? $(e).find(':selected').text() : '&nbsp;'

                select.html('<input type="hidden" value="' + $(e).val() +
                                '" name="' + $(e).attr('name') + '" id="' + $(e).attr('id') +
                                '" class="' + $(e).attr('class') + '" />' +
                            '<a class="btn dropdown-toggle" data-toggle="dropdown" href="#""><span>' +
                              current +'</span> <span class="caret"></span></a>' +
                            '<ul class="dropdown-menu"></ul>')

                $(e).find('option').each(function(o,q) {
                    select.find('.dropdown-menu').append('<li><a href="#" data-value="' + $(q).attr('value') + '">' + $(q).text() + '</a></li>')
                    if ($(q).attr('selected'))
                        select.find('.dropdown-menu li:eq(' + o + ')').click();
                });

                select.find('.dropdown-menu a').click(function() {
                    select.find('input[type=hidden]').val($(this).data('value')).change()
                    select.find('.btn:eq(0) span:eq(0)').text($(this).text())
                    $(this).parent().parent().parent().removeClass('open')
                    return false
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

    var _newBoxForm = function () {
        $('.new_box').on('click', function () {
            $(this).parent().find('.box-list').append($('#tpl_box_form').html())
            $(this).remove()
            $('#id_source').parent().append($('#id_source_type').clone())
            $('#div_id_source_type').remove()
            _selectToDropdown()
        })
    }

    return {
        init: _init,
    }

})()

$(document).ready(RBX.init())
