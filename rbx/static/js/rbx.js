var RBX = (function () {

    var _init = function () {
        $('.nav a').tooltip({placement: 'bottom'})
    }

    return {
        init: _init,
    }

})()

$(document).ready(RBX.init())
