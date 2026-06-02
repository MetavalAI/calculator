from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

class Formula(db.Model):
    __tablename__ = 'formulas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    expression = db.Column(db.Text, nullable=False)
    output_variable = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FormulaVariable(db.Model):
    __tablename__ = 'formula_variables'

    id = db.Column(db.Integer, primary_key=True)
    formula_id = db.Column(db.Integer, db.ForeignKey('formulas.id'))
    variable_name = db.Column(db.String(100))
    display_name = db.Column(db.String(200))
    expected_unit = db.Column(db.String(50))
    available_units = db.Column(db.Text)
    quantity_type = db.Column(
    db.String(50),
    default='none'
)


class Calculation(db.Model):
    __tablename__ = 'calculations'

    id = db.Column(db.Integer, primary_key=True)
    formula_name = db.Column(db.String(200))
    values_used = db.Column(db.Text)
    answer = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(200),
        nullable=False
    )

    is_admin = db.Column(
        db.Boolean,
        default=False
    )

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )

class UnitConversion(db.Model):

    __tablename__ = 'unit_conversions'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    quantity_type = db.Column(
        db.String(50),
        nullable=False
    )

    unit_name = db.Column(
        db.String(50),
        nullable=False
    )

    factor_to_base = db.Column(
        db.Float,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )