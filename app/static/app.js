function addVariable() {

    const container = document.getElementById('variables-container');

    const html = `

    <div class="row mb-3 variable-row">

        <div class="col">
            <input type="text" name="variable_name[]" placeholder="Variable Name" class="form-control">
        </div>

        <div class="col">
            <input type="text" name="display_name[]" placeholder="Display Name" class="form-control">
        </div>

        <div class="col">
            <input type="text" name="expected_unit[]" placeholder="Expected Unit" class="form-control">
        </div>

        <div class="col">
            <input type="text" name="available_units[]" placeholder="GPM,LPM,m3/hr" class="form-control">
        </div>

        <div class="col">
            <input type="text" name="variable_type[]" placeholder="flow_rate" class="form-control">
        </div>

    </div>

    `;

    container.insertAdjacentHTML('beforeend', html);
}