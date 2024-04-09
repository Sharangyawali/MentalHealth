 <!-- Schedule an Appointment -->
        <template id="schedule_an_appointment_template" name="Schedule an Appointment">
            <t t-call="website.layout">
                <link rel="stylesheet"
                    href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css" />
                <script
                    src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
                <script
                    src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
                <t
                    t-foreach="doctor" t-as="doct">
                    <div class="row g-3 date-time-container">
                        <form t-attf-action="/book-an-appointment"
                        method="POST"
                        enctype="multipart/form-data">
                            <div class="col-md-6">
                                <input type="text" id="datepicker" class="form-control date-picker"
                                name="schedule_date"
                                title="schedule date"
                                    placeholder="Select Date"/>
                            </div>
                            <div class="col-md-4">
                                <select class="form-select" name="slot_time" id="slot_time" title='time slots'>
                                        <option disabled="disabled" selected="selected">
                                            Select time
                                        </option>
                                </select>
                            </div>
                        </form>
                        
                    </div>
                <script type="text/javascript" src="/mental_health/static/src/js/book_schedule.js"/>
                <script> $(document).ready(function () {
                     var allowedDates = []; 
                     <t t-foreach="formatted_dates" t-as="formatted_date"> 
                        allowedDates.push('<t t-esc="formatted_date" />'); </t> 
                        $("#datepicker").datepicker({
                    dateFormat: 'mm/dd/yy', minDate: 0, beforeShowDay: function(date) { 
                        var formattedDate = $.datepicker.formatDate('yy/mm/dd', date); 
                        return [allowedDates.indexOf(formattedDate) !== -1]; } });

                    $("#datepicker").change(function () { 
                        var date= $(this).val();
                        console.log(date);
                        fetchData(date);
                    });

                    function fetchData(selectedDate) {
                        $.ajax({
                            url: '/available-time-slots/',
                            type: 'POST',
                            data: { date: selectedDate, doc_id:<t t-esc="doct['id']"/>  },
                            dataType: 'json',
                            success: function (data) {
                                
                               sendDataToSelectMenu(data);
                            },
                            error: function (error) {
                
                                console.error('Error fetching data:', error);
                            }
                        });
                    }                    
                 }); 
                </script>
            </t>
            </t>
        </template>