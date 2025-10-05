# =============================================================================
# SRAM Design Parasitic Extraction Script​
# =============================================================================

# 1. File Path Configuration​
set DESIGN_NAME "sram_sim"
set PLATFORM "nangate45"
set PLATFORM_DIR "./DCIM/nangate45"

# Technical Docs
set TECH_LEF_FILES [list \
    "${PLATFORM_DIR}/lef/NangateOpenCellLibrary.tech.lef" \
    "${PLATFORM_DIR}/lef/NangateOpenCellLibrary.macro.lef" \
    "${PLATFORM_DIR}/lef/NangateOpenCellLibrary.macro.mod.lef" \
    "${PLATFORM_DIR}/lef/NangateOpenCellLibrary.macro.rect.lef"
]
set MACRO_LEF "./DCIM/nangate45/lef/SRAM_6T_CORE_32x16_MC_TB.lef"
set DEF_FILE "./DCIM/results/routing/5_3_fillcell.def"
set LIB_FILE "./DCIM/nangate45/lib/NangateOpenCellLibrary_typical.lib"
set RCX_RULES "./DCIM/nangate45/rcx_patterns.rules"

# Output Configuration
set OUTPUT_SPEF "./DCIM/results/routing/5_3_parasitic.spef"

# 2. Environment Initialization​
puts "Starting parasitic extraction for ${DESIGN_NAME} ..."
puts "Input DEF: $DEF_FILE"
puts "Output SPEF: $OUTPUT_SPEF"

# 3. Primary Extraction Flow​
# 3.1 Load the Technology File

foreach lef $TECH_LEF_FILES {
    if {![file exists $lef]} {
        puts "ERROR: LEF file not found: $lef"
        exit 1
    }
    read_lef $lef
}

# Macro LEF（​​SRAM, etc.​）
if {![file exists $MACRO_LEF]} {
    puts "ERROR: Macro LEF file not found: $MACRO_LEF"
    exit 1
}
read_lef $MACRO_LEF

# Load liberty
if {![file exists $LIB_FILE]} {
    puts "ERROR: Liberty file not found: $LIB_FILE"
    exit 1
}
read_liberty $LIB_FILE

# 3.2 ​​Load the Design​
read_def $DEF_FILE

# 3.3 Configure Extraction Parameters (SRAM-Optimized)​
define_process_corner -ext_model_index 0 $RCX_RULES

extract_parasitics              \
    -ext_model_file $RCX_RULES  \
    -cc_model 8                 \
    -max_res 50                 \
    -context_depth 4            \
    -coupling_threshold 0.05    \
    -no_merge_via_res           
    
    # -cc_model 8 \               # Appropriately reduce the coupling range to improve runtime
    # -max_res 50 \               # Appropriately merge small resistors
    # -context_depth 4 \          # Reduce the number of vertical coupling layers to accelerate extraction
    # -coupling_threshold 0.05 \  # More sensitive coupling threshold​
    # -no_merge_via_res           # Preserve via resistance accuracy

# 4. ​​Export the Results​
write_spef $OUTPUT_SPEF

# 5. Report completed
puts "Parasitic parameter file generated successfully:"
puts "SPEF: $OUTPUT_SPEF"
