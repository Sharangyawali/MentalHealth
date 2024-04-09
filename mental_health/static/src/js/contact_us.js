odoo.define("mental_health.contact_us", function (require) {
    "use strict";

    var rpc = require("web.rpc");
    var publicWidget = require("web.public.widget");

    return publicWidget.registry.ContactUs = publicWidget.Widget.extend({
        selector: ".wrapper",
        events: {
            'submit form': '_onSubmit',
        },

        init: function (parent, context) {
            this._super(parent, context);
        },

        start: function () {
            this._super.apply(this, arguments);
            console.log("$ is", $);
            this.name = this.$("#name").val(); // Use .val() to get the input value
            console.log("The value in name is ", this.name);
        },

        validateContactForm: function () {
            console.log("Hello damodar from contact us page");
            if (this.name) {
                this.name.val("Damodar"); // Use .val() to set the input value
            }
        },

        _onSubmit: function (ev) {
            ev.preventDefault();
            console.log("Form Submitted Successfully");
            // Handle your form submission logic here
        }
    });

    function fetchData(selectedDate) {
        $.ajax({
            url: '/available-time-slots/',
            type: 'GET',
            data: { date: selectedDate, doc_id: doc_id },
            dataType: 'json',
            success: function (data) {

               console.log("success============");
            },
            error: function (error) {

                console.error('Error fetching data:', error);
            }
        });
    }

});


