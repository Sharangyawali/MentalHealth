odoo.define("mental_health.DoctorControl",function(require){
'use strict';

var publicWidget=require("web.public.widget");
var core=require("web.core");

var _t=core._t;

publicWidget.registry.DoctorControl=publicWidget.Widget.extend({
    selector:'.appointment_request',
    events:{
        'click #accept':"_acceptRequest",
        'click #reject':"_deleteRequest",
    },
       _acceptRequest:function(evt){
        var self=this;
    var appId=$(evt.currentTarget).data('appid');
    this._rpc({
    model:'book.appointment',
    method:'write',
    args:[[appId],{state:'approved'}]
    }).then((result)=>{
    if(result){
    location.reload()
    }
    else{
    console.log("some error")
    }
    })
    },
    _deleteRequest:function(evt){
    var self=this;
    var AppRejId=$(evt.currentTarget).data('apprejid');
        this._rpc({
           model:'book.appointment',
    method:'write',
    args:[[AppRejId],{state:'reject'}]
        }).then(function (result) {
        location.reload();
            if (result.success) {
                location.reload();
            } else {
                console.log("error in deleting");
            }
        });
    },


})

})

odoo.define("mental_health.AppointmentCompleted",function(require){
'use strict';

var publicWidget=require("web.public.widget");
var core=require("web.core");

var _t=core._t;

publicWidget.registry.AppointmentCOmplete=publicWidget.Widget.extend({
    selector:'.accepted_appointment',
    events:{
        'click #done_appointment':"_appointment_finished",
    },
       _appointment_finished:function(evt){
        var self=this;
    var appointId=$(evt.currentTarget).data('appointid');
    this._rpc({
    model:'book.appointment',
    method:'write',
    args:[[appointId],{state:'served'}]
    }).then((result)=>{
    if(result){
    location.reload()
    }
    else{
    console.log("some error")
    }
    })
    },


})

})



odoo.define("mental_health.PatientHistory",function(require){
'use strict';

var publicWidget=require("web.public.widget");
var core=require("web.core");

var _t=core._t;

publicWidget.registry.PatientHistory=publicWidget.Widget.extend({
    selector:'#patient_history',
    events:{
        'click #patient':"_view_history",
    },
       _view_history:function(evt){
        var self=this;
    var patientId=$(evt.currentTarget).data('patientid');
    var url='/patient_history?id=' + (patientId)
    window.location.href = url;
    },
})

})