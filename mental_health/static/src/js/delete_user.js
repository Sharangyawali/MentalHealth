odoo.define("mental_health.DeeleteUser",function(require){
'use strict';

var publicWidget=require("web.public.widget");
var core=require("web.core");

var _t=core._t;

publicWidget.registry.DeleteUser=publicWidget.Widget.extend({
    selector:'#vertical-tabpanel-4',
    events:{
        'click #delete':"_deleteUser",
        'click #gotoid':"_gotoUserid",
    },
    _deleteUser:function(evt){
    var self=this;
    var userId=$(evt.currentTarget).data('user-id');
        this._rpc({
            route: '/mental_health/unlink_user',
            params: {
                user_id: userId,
            },
        }).then(function (result) {
            if (result.success) {
                location.reload();
            } else {
                console.log("error in deleting");
            }
        });
    },
    _gotoUserid:function(evt){
        var self=this;
    var useridId=$(evt.currentTarget).data('userid-id');
    var url='/dashboard?uid=' + (useridId);
    window.location.href = url;

    }

})

})