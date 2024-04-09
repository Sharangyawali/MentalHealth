var registrationForm = document.getElementById("registration-form");
var userType = document.getElementById("userType");

function disableRegistrationBtn(){
    var submit = document.getElementById("submit");
    if (userType.value == "...") {
        submit.disabled = true;
    }
    else{
        submit.disabled = false;

    }
};
disableRegistrationBtn();
userType.addEventListener('change', (e) => {
    disableRegistrationBtn();
    if (userType.value == "individual") {
        registrationForm.innerHTML = `
        <div class="col-md-12">
            <label for="name" class="form-label required"> Name</label>
            <input type="text" name="name" t-att-value="name" id="name"
                class="form-control" placeholder="e.g. John Doe"
                required="required"
                autofocus="autofocus"
                t-att-readonly="'readonly' if only_passwords else None"
                t-att-autofocus="'autofocus' if login and not only_passwords else None" />
        </div>
        <div class="col-md-12">
            <label for="login" class="form-label required">Email</label>
            <input type="text" name="login" t-att-value="login" id="login"
                class="form-control"
                autocapitalize="off" required="required"
                t-att-readonly="'readonly' if only_passwords else None"
                placeholder="e.g. abc@example.com"
            />
        </div>
        <div class="col-md-12">
            <label for="phone" class="form-label">Phone</label>
            <input type="text" name="phone" t-att-value="phone" id="phone"
                class="form-control"
                autocapitalize="off" 
                t-att-readonly="'readonly' if only_passwords else None"
                placeholder="123456"
            />
        </div>

        <div class="col-md-12">
            <label for="city" class="form-label required">City</label>
            <input type="text" name="city" t-att-value="city" id="city"
                class="form-control"
                autocapitalize="off" required="required"
                t-att-readonly="'readonly' if only_passwords else None"
                placeholder="Brisbane, Australia"
            />
        </div>

        <div class="col-md-12">
            <label for="street" class="form-label required">Streeet</label>
            <input type="text" name="street" t-att-value="street" id="street"
                class="form-control"
                autocapitalize="off" required="required"
                t-att-readonly="'readonly' if only_passwords else None"
                placeholder="Wolseley Road, Point Piper, NSW"
            />
        </div>
        <div class="col-md-12">
            <label for="zip" class="form-label">Post Code</label>
            <input type="text" name="zip" id="zip"
                class="form-control"
                autocapitalize="off"
                t-att-readonly="'readonly' if only_passwords else None"
                placeholder="1245"
            />
        </div>

        <div class="col-md-12">
            <label for="password" class="form-label required">Password</label>
            <input type="password" name="password" id="password"
                class="form-control"
                required="required"
                t-att-autofocus="'autofocus' if only_passwords else None"
                placeholder="*******"
            />
        </div>
        <div class="col-md-12">
            <label for="confirm_password" class="form-label required">Confirm
                Password</label>
            <input type="password" name="confirm_password" id="confirm_password"
                class="form-control" required="required"
                placeholder="*******"
            />
        </div>
    `;
    }
    else {

        registrationForm.innerHTML = ` 
        <div class="col-md-12">
            <label for="name" class="form-label required">Organization Name</label>
            <input type="text" name="name" t-att-value="name" id="name"
                class="form-control" placeholder="e.g. Bibek's Venture Pvt. Ltd."
                required="required"
                autofocus="autofocus"
                t-att-readonly="'readonly' if only_passwords else None"
                t-att-autofocus="'autofocus' if login and not only_passwords else None" />
        </div>
        <div class="col-md-12">
            <label for="login" class="form-label required">Email</label>
            <input type="text" name="login" t-att-value="login" id="login"
                class="form-control"
                autocapitalize="off" required="required"
                t-att-readonly="'readonly' if only_passwords else None"
                placeholder="e.g. abc@example.com"
            />
        </div>
        <div class="col-md-12">
            <label for="phone" class="form-label">Phone</label>
            <input type="text" name="phone" t-att-value="phone" id="phone"
                class="form-control"
                autocapitalize="off"
                t-att-readonly="'readonly' if only_passwords else None"
                placeholder="123456"
            />
        </div>

        <div class="col-md-12">
            <label for="org_type" class="form-label required">Organization Type</label>
            <select id="org_type" class="form-select" name="org_type">      
            ${fetchOrg()}
            </select>
        </div>


        <div class="col-md-6">
            <label for="employee_size" class="form-label required">Employee Size</label>
            <input type="text" name="employee_size" t-att-value="employee_size"
                id="employee_size"
                class="form-control"
                autocapitalize="off" required="required"
                placeholder="50"
            />
        </div>
        <div class="col-md-6">
            <label for="industry" class="form-label required">Industry</label>
            <input type="text" name="industry" t-att-value="industry"
                id="industry"
                class="form-control"
                autocapitalize="off" required="required"
                placeholder="Hospitality"
            />
        </div>

        <div class="col-md-12">
            <label for="city" class="form-label required">City</label>
            <input type="text" name="city" t-att-value="city" id="city"
                class="form-control"
                autocapitalize="off" required="required"
                t-att-readonly="'readonly' if only_passwords else None"
                placeholder="Brisbane, Australia"
            />
        </div>

        <div class="col-md-12">
            <label for="street" class="form-label required">Streeet</label>
            <input type="text" name="street" t-att-value="street" id="street"
                class="form-control"
                autocapitalize="off" required="required"
                t-att-readonly="'readonly' if only_passwords else None"
                placeholder="Wolseley Road, Point Piper, NSW"
            />
        </div>
        <div class="col-md-12">
            <label for="zip" class="form-label">Post Code</label>
            <input type="text" name="zip" id="zip"
                class="form-control"
                autocapitalize="off"
                t-att-readonly="'readonly' if only_passwords else None"
                placeholder="1245"
            />
        </div>

        <div class="col-md-12">
            <label for="password" class="form-label required">Password</label>
            <input type="password" name="password" id="password"
                class="form-control"
                required="required"
                t-att-autofocus="'autofocus' if only_passwords else None"
                placeholder="*******"
            />
        </div>
        <div class="col-md-12">
            <label for="confirm_password" class="form-label required">Confirm
                Password</label>
            <input type="password" name="confirm_password" id="confirm_password"
                class="form-control" required="required"
                placeholder="*******"
            />
        </div>
    `;
    }
});

function fetchOrg() {
    $.ajax({
        url: '/org-types/',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            console.log(data);
            showOrg(data);
        },
        error: function (error) {
            console.error('Error fetching data:', error);
        }
    });
    
} 

function showOrg(data) {
    let options = '';

    data.forEach(element => {
        options += `<option value=${element.id}>${element.type}</option>`;
    });

    $("#org_type").html(options);
}