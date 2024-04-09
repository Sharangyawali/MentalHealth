function sendDataToSelectMenu(data) {
    var selectMenu = $('#slot_time');
    selectMenu.empty();
    $.each(data, function (index, slot) {
        if(slot.slot_start_time !== undefined){
        console.log(slot.id)
            selectMenu.append('<option value="' + slot.id + '">' + slot.slot_start_time + ' - ' + slot.slot_end_time + '</option>');

        }
        else{
            selectMenu.append('<option value="null" selected="selected">' + ' Not available ' + '</option>');
        }
        
    });
}



