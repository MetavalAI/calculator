from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_file,
    redirect,
    flash,
    url_for,
    current_app
)

from app import db
from app.services import evaluate_formula

from app.models import (
    Formula,
    FormulaVariable,
    Calculation,
    User,
    UnitConversion
)

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


# =========================
# HOME PAGE
# =========================
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


# =========================
# HISTORY
# =========================
@main.route('/history')
def history():

    calculations = Calculation.query.order_by(
        Calculation.id.desc()
    ).all()

    return render_template(
        'history.html',
        calculations=calculations
    )


# =========================
# EXPORT EXCEL
# =========================
@main.route('/export-excel')
def export_excel():

    calculations = Calculation.query.all()

    export_folder = 'exports'
    os.makedirs(export_folder, exist_ok=True)

    file_path = os.path.join(export_folder, 'calculations.xlsx')

    formula_groups = {}

    for calc in calculations:

        if calc.formula_name not in formula_groups:
            formula_groups[calc.formula_name] = []

        formula_groups[calc.formula_name].append({
            'Values Used': calc.values_used,
            'Answer': calc.answer,
            'Created At': calc.created_at
        })

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:

        for formula_name, records in formula_groups.items():

            df = pd.DataFrame(records)
            df.to_excel(writer, sheet_name=formula_name[:31], index=False)

    return send_file(
        os.path.abspath(file_path),
        as_attachment=True,
        download_name='calculations.xlsx'
    )


# =========================
# CREATE FORMULA
# =========================
@main.route('/create-formula', methods=['GET', 'POST'])
def create_formula():

    if not current_user.is_authenticated:
        return redirect('/login')

    if not current_user.is_admin:
        return "Access Denied"

    if request.method == 'POST':

        formula = Formula(
            name=request.form['name'],
            description=request.form['description'],
            expression=request.form['expression'],
            output_variable=request.form.get('output_variable', '')
        )

        db.session.add(formula)
        db.session.commit()

        variables = request.form.getlist('variable_name[]')
        labels = request.form.getlist('display_name[]')
        expected_units = request.form.getlist('expected_unit[]')
        variable_types = request.form.getlist('variable_type[]')

        for i in range(len(variables)):

            if variables[i].strip() == '':
                continue

            db.session.add(FormulaVariable(
                formula_id=formula.id,
                variable_name=variables[i],
                display_name=labels[i],
                expected_unit=expected_units[i],
                quantity_type=variable_types[i]
            ))

        db.session.commit()

        flash("Formula Created Successfully", "success")
        return redirect(url_for('main.home'))

    return render_template('create_formula.html')


# =========================
# CALCULATE PAGE
# =========================
@main.route('/calculate/<int:formula_id>')
def calculate_page(formula_id):

    formula = Formula.query.get_or_404(formula_id)

    variables = FormulaVariable.query.filter_by(
        formula_id=formula_id
    ).all()

    for var in variables:

        units = UnitConversion.query.filter_by(
            quantity_type=var.quantity_type
        ).all()

        var.unit_options = [u.unit_name for u in units]

    return render_template(
        'calculate.html',
        formula=formula,
        variables=variables
    )


# =========================
# API CALCULATE
# =========================
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

            if current_app.debug:
                print(var.variable_name, var.quantity_type)

            variable_config[var.variable_name] = {
                'expected_unit': var.expected_unit,
                'variable_type': var.quantity_type.lower() if var.quantity_type else 'none'
            }

        answer = evaluate_formula(
            selected_formula.expression,
            data['values'],
            variable_config,
            selected_formula.output_variable
        )

        answer_text = str(answer['value'])

        if answer.get('unit'):
            answer_text += f" {answer['unit']}"

        db.session.add(Calculation(
            formula_name=selected_formula.name,
            values_used=json.dumps(data['values']),
            answer=answer_text,
            created_at=datetime.utcnow()
        ))

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


# =========================
# LOGIN / LOGOUT
# =========================
@main.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        user = User.query.filter_by(
            username=request.form['username']
        ).first()

        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')

        error = "Invalid username or password"

    return render_template('login.html', error=error)


@main.route('/logout')
@login_required
def logout():

    logout_user()
    flash("Logged Out Successfully", "success")

    return redirect('/')


# =========================
# UNIT MANAGEMENT (CLEAN SYSTEM)
# =========================

@main.route('/unit-conversions', methods=['GET', 'POST'])
@login_required
def unit_master():

    if request.method == 'POST':

        for unit in UnitConversion.query.all():

            field = f'factor_{unit.id}'

            if field in request.form:
                unit.factor_to_base = float(request.form[field])

        db.session.commit()

        flash("Unit conversions updated", "success")
        return redirect('/unit-conversions')

    units = UnitConversion.query.order_by(
        UnitConversion.quantity_type
    ).all()

    return render_template('unit_conversions.html', units=units)


@main.route('/add-unit', methods=['POST'])
@login_required
def add_unit():

    db.session.add(UnitConversion(
        quantity_type=request.form['quantity_type'],
        unit_name=request.form['unit_name'],
        factor_to_base=float(request.form['factor_to_base'])
    ))

    db.session.commit()
    return redirect('/unit-conversions')


@main.route('/delete-unit/<int:id>')
@login_required
def delete_unit(id):

    unit = UnitConversion.query.get_or_404(id)

    db.session.delete(unit)
    db.session.commit()

    return redirect('/unit-conversions')


# =========================
# SEED UNITS (NO LOGIN REQUIRED)
# =========================
@main.route('/seed-units')
def seed_units():

    defaults = [
        ('distance', 'm', 1),
        ('distance', 'km', 1000),
        ('distance', 'cm', 0.01),

        ('time', 'sec', 1),
        ('time', 'min', 60),
        ('time', 'hr', 3600),

        ('speed', 'm/sec', 1),
        ('speed', 'km/hr', 0.277778),

        ('pressure', 'pa', 1),
        ('pressure', 'bar', 100000),
        ('pressure', 'psi', 6894.76)
    ]

    for q, u, f in defaults:

        exists = UnitConversion.query.filter_by(
            quantity_type=q,
            unit_name=u
        ).first()

        if not exists:
            db.session.add(UnitConversion(
                quantity_type=q,
                unit_name=u,
                factor_to_base=f
            ))

    db.session.commit()

    return "Units Seeded"