from pydra.engine import specs
from pydra import ShellCommandTask
import typing as ty

# input fields 
input_fields = [
    ("dimension", specs.File, 
    {}, ), 
]

#input spec 
N4BiasFieldCorrection_Input_Spec = specs.SpecInfo(
    name="Input", fields=input_fields, bases=(specs.ShellSpec,))


# output fields 
output_fields = []

# output spec 

N4BiasFieldCorrection_Input_Spec = specs.SpecInfo(name="Output", fields=output_fields, bases=(specs.ShellOutSpec,))


class N4BiasFieldCorrection(ShellCommandTask):
    """
    Example
    -------
    TODO: write docstring
    """

    input_spec = N4BiasFieldCorrection_input_spec
    output_spec = N4BiasFieldCorrection_output_spec
    executable = "N4BiasFieldCorrection"