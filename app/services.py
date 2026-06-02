from asteval import Interpreter
import math

from app.models import UnitConversion


def convert_to_base(
    value,
    unit,
    variable_type
):

    record = UnitConversion.query.filter_by(
    quantity_type=variable_type,
    unit_name=unit
).first()

    if not record:

        raise Exception(
            f"Unit '{unit}' not found for type '{variable_type}'"
        )

    return float(value) * float(record.factor_to_base)


def evaluate_formula(
    expression,
    variables,
    variable_config,
    output_variable
):

    processed_values = {}
    
    # INPUT CONVERSION

    for variable_name, value_data in variables.items():

        value = value_data["value"]

        selected_unit = value_data["unit"]

        variable_type = variable_config[
            variable_name
        ]["variable_type"]

        base_value = convert_to_base(

            value=value,

            unit=selected_unit,

            variable_type=variable_type
        )

        processed_values[
            variable_name
        ] = base_value
    
    # EXPRESSION BUILDING

    final_expression = expression

    for variable, value in processed_values.items():

        final_expression = final_expression.replace(

            variable,

            str(value)
        )

    # SAFE EVALUATION    

    aeval = Interpreter(

        usersyms={

            "sqrt": math.sqrt,

            "pow": math.pow
        }
    )

    result = aeval(final_expression)

    if aeval.error:

        raise Exception(
            "Invalid Formula Expression"
        )

    # ROUNDING    

    if result == int(result):

        result = int(result)

    else:

        result = round(result, 6)

    return {

        "value": result,

        "unit": ""
    }