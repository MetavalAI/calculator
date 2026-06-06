from asteval import Interpreter
import math
import re
from app.models import UnitConversion

def convert_to_base(value, unit, variable_type):
    """
    Convert any unit value to base unit.
    """

    record = UnitConversion.query.filter_by(
        quantity_type=variable_type,
        unit_name=unit
    ).first()

    if not record:
        raise Exception(
            f"Unit '{unit}' not found for type '{variable_type}'"
        )

    return float(value) * float(record.factor_to_base)

def evaluate_formula(expression, variables, variable_config, output_variable):
    """
    Evaluate formula safely with unit conversion support.
    """

    processed_values = {}
# INPUT CONVERSION
    for name, data in variables.items():

        value = data["value"]
        unit = data["unit"]

        var_type = variable_config[name]["variable_type"]

        base_value = convert_to_base(
            value,
            unit,
            var_type
        )

        processed_values[name] = base_value
# BUILD EXPRESSION
    final_expression = expression

    for name, value in processed_values.items():

        final_expression = re.sub(
            rf"\b{re.escape(name)}\b",
            str(value),
            final_expression
        )
# SAFE EVALUATION
    aeval = Interpreter(
        usersyms={
            "sqrt": math.sqrt,
            "pow": math.pow
        }
    )

    try:
        result = aeval(final_expression)

    except ZeroDivisionError:
        raise Exception("Division by zero error in formula")

    except Exception as e:
        raise Exception(f"Formula evaluation error: {str(e)}")

    if aeval.error:
        raise Exception("Invalid Formula Expression")
# ROUNDING
    if result == int(result):
        result = int(result)
    else:
        result = round(result, 6)
# OUTPUT UNIT SYSTEM
    output_unit = ""

    output_config = variable_config.get(output_variable)

    if output_config:

        output_type = output_config.get("variable_type")

        unit_row = UnitConversion.query.filter_by(
            quantity_type=output_type
        ).first()

        if unit_row:
            output_unit = unit_row.unit_name
# FINAL RESPONSE
    return {
        "value": result,
        "unit": output_unit
}