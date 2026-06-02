from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_file,
    redirect,
    flash,
    url_for
)

from app import db
from app.services import evaluate_formula
from app.models import Formula, FormulaVariable, Calculation, User, UnitConversion
import pandas as pd
from datetime import datetime
import json
import os
import logging

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

main = Blueprint('main', __name__)


# HOME PAGE
@main.route('/')
def home():

    formulas = Formula.query.all()

    calculations = Calculation.query.order_by(
        Calculation.id.desc()
    ).limit(10)

    return render_template(
        'home.html',
        formulas=formulas,
        calculations=calculations,
        current_user=current_user
    )


# HISTORY PAGE
@main.route('/history')
def history():

    calculations = Calculation.query.order_by(
        Calculation.id.desc()
    ).all()

    return render_template(
        'history.html',
        calculations=calculations
    )


# EXPORT EXCEL
@main.route('/export-excel')
def export_excel():

    calculations = Calculation.query.all()

    export_folder = 'exports'

    os.makedirs(export_folder, exist_ok=True)

    file_path = os.path.join(
        export_folder,
        'calculations.xlsx'
    )

    formula_groups = {}

    for calc in calculations:

        if calc.formula_name not in formula_groups:
            formula_groups[calc.formula_name] = []

        formula_groups[calc.formula_name].append({

            'Values Used': calc.values_used,
            'Answer': calc.answer,
            'Created At': calc.created_at
        })

    with pd.ExcelWriter(
        file_path,
        engine='openpyxl'
    ) as writer:

        for formula_name, records in formula_groups.items():

            df = pd.DataFrame(records)

            safe_sheet_name = formula_name[:31]

            df.to_excel(
                writer,
                sheet_name=safe_sheet_name,
                index=False
            )

    return send_file(
        os.path.abspath(file_path),
        as_attachment=True,
        download_name='calculations.xlsx'
    )


# CREATE FORMULA
@main.route('/create-formula', methods=['GET', 'POST'])
def create_formula():

    if not current_user.is_authenticated:
        return redirect('/login')

    if not current_user.is_admin:
        return "Access Denied"

    if request.method == 'POST':

        name = request.form['name']
        description = request.form['description']
        expression = request.form['expression']

        formula = Formula(
            name=name,
            description=description,
            expression=expression,
            output_variable=request.form.get(
                'output_variable',
                ''
            )
        )

        db.session.add(formula)
        db.session.commit()

        variables = request.form.getlist('variable_name[]')
        labels = request.form.getlist('display_name[]')
        expected_units = request.form.getlist('expected_unit[]')
        available_units = request.form.getlist('available_units[]')
        variable_types = request.form.getlist('variable_type[]')

        print("VARIABLES =", variables)
        print("LABELS =", labels)
        print("EXPECTED =", expected_units)
        print("TYPES =", variable_types)

        for i in range(len(variables)):
            variable = FormulaVariable(
                formula_id=formula.id,
                variable_name=variables[i],
                display_name=labels[i],
                expected_unit=expected_units[i],
                quantity_type=variable_types[i]
            )

            db.session.add(variable)

        db.session.commit()

        flash(
            "Formula Created Successfully",
            "success"
        )

        return redirect(url_for('main.home'))

    return render_template('create_formula.html')


# CALCULATE PAGE
@main.route('/calculate/<int:formula_id>')
def calculate_page(formula_id):

    formula = Formula.query.get_or_404(formula_id)

    variables = FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).all()

    print("FORMULA ID =", formula_id)
    print("VARIABLE COUNT =", len(variables))

    return render_template(
        'calculate.html',
        formula=formula,
        variables=variables
    )


# API CALCULATE
@main.route('/api/calculate', methods=['POST'])
def calculate_api():

    try:

        data = request.json

        formula_id = data.get('formula_id')

        selected_formula = Formula.query.get(formula_id)

        if not selected_formula:

            return jsonify({
                'success': False,
                'error': 'Formula not found'
            }), 404

        variables = FormulaVariable.query.filter_by(
            formula_id=formula_id
        ).all()

        variable_config = {}

        for var in variables:
            print(
                "VAR:",
                var.variable_name,
                "TYPE:",
                var.quantity_type
            )
            variable_config[var.variable_name] = {
                'expected_unit': var.expected_unit,
                'variable_type':
                    var.quantity_type.lower()
                    if var.quantity_type
                    else 'none'
            }

        answer = evaluate_formula(
            selected_formula.expression,
            data['values'],
            variable_config,
            selected_formula.output_variable
        )

        calculation = Calculation(

            formula_name=selected_formula.name,

            values_used=json.dumps(data['values']),

            answer=str(answer['value']),

            created_at=datetime.utcnow()
        )

        db.session.add(calculation)
        db.session.commit()

        return jsonify({

            'success': True,
            'answer': answer
        })

    except Exception as e:

        logging.error(str(e))

        return jsonify({

            'success': False,
            'error': str(e)

        }), 400


# VIEW FORMULA
@main.route('/formula/<int:formula_id>')
def view_formula(formula_id):

    formula = Formula.query.get_or_404(formula_id)

    variables = FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).all()

    return render_template(
        'view_formula.html',
        formula=formula,
        variables=variables
    )


# EDIT FORMULA
@main.route('/edit-formula/<int:formula_id>', methods=['GET', 'POST'])
def edit_formula(formula_id):

    if not current_user.is_authenticated:
        return redirect('/login')

    if not current_user.is_admin:
        return "Access Denied"

    formula = Formula.query.get_or_404(formula_id)

    variables = FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).all()

    if request.method == 'POST':

        formula.name = request.form['name']
        formula.description = request.form['description']
        formula.expression = request.form['expression']
        formula.output_variable = request.form.get(
    'output_variable',
    ''
)

        db.session.commit()

        FormulaVariable.query.filter_by(
            formula_id=formula.id
        ).delete()

        variable_names = request.form.getlist('variable_name[]')
        display_names = request.form.getlist('display_name[]')
        expected_units = request.form.getlist('expected_unit[]')
        # available_units = request.form.getlist('available_units[]')
        variable_types = request.form.getlist('variable_type[]')

        for i in range(len(variable_names)):

            if variable_names[i].strip() == '':
                continue

            variable = FormulaVariable(
                formula_id=formula.id,
                variable_name=variable_names[i],
                display_name=display_names[i],
                expected_unit=expected_units[i],
                # available_units=available_units[i],
                quantity_type=variable_types[i]
            )

            db.session.add(variable)

        db.session.commit()

        flash(
            "Formula Updated Successfully",
            "success"
        )

        return redirect('/')

    return render_template(
        'edit_formula.html',
        formula=formula,
        variables=variables
    )


# DELETE FORMULA
@main.route('/delete-formula/<int:formula_id>')
def delete_formula(formula_id):

    if not current_user.is_authenticated:
        return redirect('/login')

    if not current_user.is_admin:
        return "Access Denied"

    formula = Formula.query.get_or_404(formula_id)

    FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).delete()

    db.session.delete(formula)

    db.session.commit()

    flash(
        "Formula Deleted Successfully",
        "success"
    )

    return redirect('/')


# LOGIN PAGE
@main.route('/login', methods=['GET', 'POST'])
def login():

    from app.models import User

    error = None

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and user.check_password(password):

            login_user(user)

            flash(
                f'Welcome {user.username}',
                'success'
            )

            return redirect('/')

        else:

            error = "Invalid username or password"

    return render_template(
        'login.html',
        error=error
    )

# LOGOUT
@main.route('/logout')
@login_required
def logout():

    logout_user()

    flash(
        "Logged Out Successfully",
        "success"
    )

    return redirect('/')

@main.route(
    '/unit-master',
    methods=['GET','POST']
)
@login_required
def unit_master():

    if request.method == 'POST':

        units = UnitConversion.query.all()

        for unit in units:

            field_name = f'factor_{unit.id}'

            if field_name in request.form:

                unit.factor_to_base = float(
                    request.form[field_name]
                )

        db.session.commit()

        flash(
            "Unit conversions updated",
            "success"
        )

        return redirect('/unit-master')

    units = UnitConversion.query.order_by(
        UnitConversion.quantity_type
    ).all()

    return render_template(
        'unit_conversions.html',
        units=units
    )

@main.route(
    '/add-unit',
    methods=['POST']
)
@login_required
def add_unit():

    unit = UnitConversion(

    quantity_type=request.form[
        'quantity_type'
    ],

    unit_name=request.form[
        'unit_name'
    ],

    factor_to_base=float(
        request.form[
            'factor_to_base'
        ]
    )
)

    db.session.add(unit)

    db.session.commit()

    return redirect('/unit-conversions')

@main.route(
    '/delete-unit/<int:id>'
)
@login_required
def delete_unit(id):

    unit = UnitConversion.query.get_or_404(id)

    db.session.delete(unit)

    db.session.commit()

    return redirect('/unit-master')

@main.route('/seed-units')

# @login_required
def seed_units():

    defaults = [

        ('distance','m',1),
        ('distance','km',1000),
        ('distance','cm',0.01),

        ('time','sec',1),
        ('time','min',60),
        ('time','hr',3600),

        ('speed','m/sec',1),
        ('speed','km/hr',0.277778),

        ('pressure','pa',1),
        ('pressure','bar',100000),
        ('pressure','psi',6894.76)
    ]

    for q,u,f in defaults:

        exists = UnitConversion.query.filter_by(
            quantity_type=q,
            unit_name=u
        ).first()

        if not exists:

            db.session.add(

                UnitConversion(

                    quantity_type=q,

                    unit_name=u,

                    factor_to_base=f
                )
            )

    db.session.commit()

    return "Units Seeded"