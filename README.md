# OpenACM

The initial version of paper" OpenACM: An Open-Source SRAM-Based Approximate CiM Compiler"



\##Arguments##



python flow\_script\_generator.py \[options]

--design\_name			Name of the design

--top\_model			Top-level model name

--platform			Target platform name

--platform\_dir			Directory containing platform files

--lib					Path to standard cell library file

--lib\_typical			Path to typical cell library file

--v					Path to Verilog library file

--tech\_lef				Path to technology LEF file

--sc\_lef				Path to standard cell LEF file

--sram\_lef			Path to SRAM LEF file

--sram\_lib			Path to SRAM library file

--rcx\_rules			Path to RCX rules file

--sdc\_file				Path to SDC constraints file

--scripts\_dir			Directory containing scripts files

--reports\_dir			Directory for reports

--location\_x			X-coordinate for SRAM macro placement

--location\_y			Y-coordinate for SRAM macro placement

--result\_dir			Directory for output results

--rtl\_dir				Directory containing RTL files

--multiplier\_dir			Directory containing multiplier files



python SRAM.py \[options]

--data\_width			Width of the data bus (in bits)

--addr\_count			Number of addressable locations (depth)

--rtl\_dir				Directory containing RTL files

--result\_dir			Directory for output results



python pe\_compiler.py \[options]

--data\_width			Width of the data bus (in bits)

--addr\_count			Number of addressable locations (depth)

--multiplier\_module		Name of the multiplier

--rtl\_dir				Directory containing RTL files



multiplier\_compiler.py  \[options]

--bit\_width			      Width of the multiplier

--generate\_Exact()           Generates exact multipliers



--generate\_Appro\_4\_2()  Generates approximate 4-2 compressor-based multipliers



--generate\_Log()             Generates log-based multipliers



Note:

We have updated the function generate\_Appro\_4\_2(test\_bit\_widths) to enhance the flexibility of the multiplier compiler. This update enables the program to automatically calculate the required number of approximate 4-2 compressors for a given bit width. The function supports batch generation for multiple bit widths and provides an interactive interface that allows users to choose combinations from eight predefined classic approximate compressors: Yang1, kong2, antonio, momeni, ha, akbar1, akbar2, and sabetz. If no input is provided, the system will default to Yang1.



\### Truth Table of Approximate 4-2 Compressors



!\[Approximate 4-2 Compressor Truth Table](./compressor.png)



\##Usage##



Place the script in the same directory as DCIM.



python flow\_script\_generator.py --location\_x 30 --location\_y 15

python SRAM.py --data\_width 8 --addr\_count 16

python pe\_compiler.py --data\_width 8 --addr\_count 16 --multiplier\_module Exact

./DCIM/tcl/eda.sh



​flow\_script\_generator.py​​ configures the location of SRAM macro cells within the chip.

SRAM.py​​ configures the bit width of the SRAM behavioral model.

pe\_compiler.py​​ configures the bit width and multiplier type of the system

Finally, ./DCIM/tcl/eda.sh​​ finally executes the EDA flow.

If needed, file paths can be customized using the listed parameters; otherwise, the default configuration will be used.



Version Note

Note:

This is the initial release of OpenACM.

Some parts are still under development, and we will continuously improve and expand its functionality in future versions.

