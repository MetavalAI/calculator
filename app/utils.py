from app.unit_conversions import UNIT_CONVERSIONS


def convert_to_expected(
    value,
    current_unit,
    expected_unit
):

    try:

        if value == '' or value is None:
            raise ValueError("Please enter all values")

        value = float(value)

        current_unit = current_unit.strip().lower()
        expected_unit = expected_unit.strip().lower()

        # same unit
        if current_unit == expected_unit:
            return value

        # convert to base
        base_value = (
            value *
            UNIT_CONVERSIONS[current_unit]
        )

        # base to expected
        converted_value = (
            base_value /
            UNIT_CONVERSIONS[expected_unit]
        )

        return converted_value

    except Exception as e:

        print("Conversion Error:", e)

        return float(value)